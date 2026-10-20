"""Rebuild the IDA117V service-request analysis and all saved evidence."""
from __future__ import annotations

import copy
import hashlib
import json
import platform
import sys
from pathlib import Path

import joblib
import lightgbm as lgb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from lightgbm import LGBMClassifier, early_stopping, log_evaluation
from scipy.stats import binomtest
from sklearn import __version__ as sklearn_version
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from neural import train_embedding_network
from prepare_data import (
    CAT_FEATURES,
    FEATURES,
    NUM_FEATURES,
    RAW_DATA,
    SEED,
    TARGET,
    encode_categories,
    encode_dense,
    encode_lightgbm,
    fit_category_maps,
    fit_frequency_maps,
    load_source,
    prepare_frame,
    split_xy,
)

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "04_Figures"
RESULTS = ROOT / "05_Results"
DOCS = ROOT / "06_Documentation"
CODE = ROOT / "03_Code"
PROCESSED = ROOT / "02_Data" / "processed"


def json_dump(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def best_threshold(y_true: np.ndarray, probability: np.ndarray) -> tuple[float, float]:
    candidates = np.round(np.arange(0.25, 0.801, 0.01), 2)
    scores = [f1_score(y_true, probability >= value, average="macro", zero_division=0) for value in candidates]
    index = int(np.argmax(scores))
    return float(candidates[index]), float(scores[index])


def metrics_for(name: str, y_true: np.ndarray, probability: np.ndarray, threshold: float) -> dict:
    prediction = (probability >= threshold).astype(np.int8)
    return {
        "model": name,
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, prediction)),
        "macro_f1": float(f1_score(y_true, prediction, average="macro", zero_division=0)),
        "at_risk_precision": float(precision_score(y_true, prediction, zero_division=0)),
        "at_risk_recall": float(recall_score(y_true, prediction, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "average_precision": float(average_precision_score(y_true, probability)),
        "confusion_matrix": confusion_matrix(y_true, prediction).tolist(),
        "classification_report": classification_report(y_true, prediction, output_dict=True, zero_division=0),
    }


def save_figure(filename: str) -> None:
    plt.tight_layout()
    plt.savefig(FIGURES / filename, dpi=180, bbox_inches="tight")
    plt.close()


def make_eda(source: pd.DataFrame, frame: pd.DataFrame) -> None:
    plt.figure(figsize=(6, 4))
    frame[TARGET].value_counts().sort_index().rename({0: "Within 7 days", 1: "At risk"}).plot.bar(color=["#2A9D8F", "#E76F51"])
    plt.title("Seven-day completion target")
    plt.ylabel("Service requests")
    plt.xticks(rotation=0)
    save_figure("01_target_distribution.png")

    missing = source.isna().mean().sort_values(ascending=True).tail(10) * 100
    plt.figure(figsize=(8, 5))
    missing.plot.barh(color="#457B9D")
    plt.title("Highest field-level missingness")
    plt.xlabel("Missing values (%)")
    save_figure("02_missingness.png")

    top = frame.groupby("C3_Complaint_Type").agg(requests=(TARGET, "size"), risk_rate=(TARGET, "mean")).nlargest(15, "requests").sort_values("risk_rate")
    plt.figure(figsize=(9, 6))
    (top["risk_rate"] * 100).plot.barh(color="#E9C46A")
    plt.title("Risk among the 15 highest-volume complaint types")
    plt.xlabel("Requests at risk (%)")
    save_figure("03_complaint_risk.png")

    council = frame.groupby("Sub_Council").agg(requests=(TARGET, "size"), risk_rate=(TARGET, "mean"))
    council = council.loc[council.requests >= 200].sort_values("risk_rate")
    plt.figure(figsize=(8, 6))
    (council.risk_rate * 100).plot.barh(color="#264653")
    plt.title("Seven-day risk by sub-council (n >= 200)")
    plt.xlabel("Requests at risk (%)")
    save_figure("04_subcouncil_risk.png")

    daily = frame.assign(day=frame.created_local.dt.floor("D").dt.tz_localize(None)).groupby("day").agg(requests=(TARGET, "size"), risk_rate=(TARGET, "mean"))
    figure, axis_1 = plt.subplots(figsize=(10, 5))
    axis_1.plot(daily.index, daily.requests, color="#457B9D", label="Requests")
    axis_1.set_ylabel("Requests", color="#457B9D")
    axis_2 = axis_1.twinx()
    axis_2.plot(daily.index, daily.risk_rate * 100, color="#E76F51", label="At-risk rate")
    axis_2.set_ylabel("At-risk rate (%)", color="#E76F51")
    axis_1.set_title("Daily request volume and seven-day risk")
    figure.autofmt_xdate()
    save_figure("05_daily_volume_risk.png")

    duration = (frame.Completed_Date - frame.Created_On_Date).dt.total_seconds() / 86400
    duration = duration[(duration >= 0) & (duration <= 30)]
    plt.figure(figsize=(8, 4))
    plt.hist(duration, bins=30, color="#2A9D8F", edgecolor="white")
    plt.axvline(7, color="#E76F51", linestyle="--", label="7-day horizon")
    plt.title("Completion duration (0-30 days)")
    plt.xlabel("Days")
    plt.ylabel("Completed requests")
    plt.legend()
    save_figure("06_completion_duration.png")

    complaint = frame.groupby("C3_Complaint_Type").agg(requests=(TARGET, "size"), risk_rate=(TARGET, "mean"))
    plt.figure(figsize=(7, 5))
    plt.scatter(complaint.requests, complaint.risk_rate * 100, alpha=0.45, color="#6A4C93")
    plt.xscale("log")
    plt.title("Complaint volume versus seven-day risk")
    plt.xlabel("Requests (log scale)")
    plt.ylabel("At-risk rate (%)")
    save_figure("07_complaint_volume_risk.png")


def main() -> None:
    np.random.seed(SEED)
    for folder in [FIGURES, RESULTS, DOCS, PROCESSED]:
        folder.mkdir(parents=True, exist_ok=True)

    source = load_source()
    frame = prepare_frame(source)
    split = split_xy(frame)
    X_train, y_train, train_frame = split["train"]
    X_validation, y_validation, validation_frame = split["validation"]
    X_test, y_test, test_frame = split["test"]

    duration = (pd.to_datetime(source.Completed_Date, errors="coerce", utc=True) - pd.to_datetime(source.Created_On_Date, errors="coerce", utc=True)).dt.total_seconds() / 86400
    audit = {
        "source_file": RAW_DATA.name,
        "source_sha256": sha256(RAW_DATA),
        "source_rows": int(len(source)),
        "source_columns": int(len(source.columns)),
        "excluded_missing_creation_timestamp": int(pd.to_datetime(source.Created_On_Date, errors="coerce", utc=True).isna().sum()),
        "model_rows": int(len(frame)),
        "date_min": str(frame.created_local.min().date()),
        "date_max": str(frame.created_local.max().date()),
        "date_count": int(frame.created_local.dt.date.nunique()),
        "within_7_days": int((frame[TARGET] == 0).sum()),
        "at_risk": int((frame[TARGET] == 1).sum()),
        "at_risk_rate": float(frame[TARGET].mean()),
        "missing_completion": int(pd.to_datetime(source.Completed_Date, errors="coerce", utc=True).isna().sum()),
        "exact_duplicates": int(source.duplicated().sum()),
        "repeated_notification_rows": int(source.duplicated("Notification", keep=False).sum()),
        "coordinate_1_missing": int(pd.to_numeric(source.X_Y_Co_ordinate_1, errors="coerce").isna().sum()),
        "coordinate_2_missing": int(pd.to_numeric(source.X_Y_Co_ordinate_2, errors="coerce").isna().sum()),
        "coordinate_zero_pair": int(((pd.to_numeric(source.X_Y_Co_ordinate_1, errors="coerce") == 0) & (pd.to_numeric(source.X_Y_Co_ordinate_2, errors="coerce") == 0)).sum()),
        "duration_over_30_days": int((duration > 30).sum()),
        "duration_over_90_days": int((duration > 90).sum()),
        "duration_over_180_days": int((duration > 180).sum()),
        "category_cardinality": {column: int(frame[column].nunique()) for column in CAT_FEATURES},
        "splits": {name: int(len(values[0])) for name, values in split.items()},
        "note": "Counts are computed from the workbook packaged here and may differ from earlier report drafts that used a different CSV snapshot.",
    }
    json_dump(RESULTS / "dataset_audit.json", audit)
    make_eda(source, frame)

    # Keep a small, non-identifying prepared sample for schema inspection.
    frame[FEATURES + [TARGET]].head(500).to_csv(PROCESSED / "prepared_schema_sample.csv", index=False)

    baseline = DummyClassifier(strategy="prior")
    baseline.fit(np.zeros((len(y_train), 1)), y_train)
    validation_probabilities = {"Dummy baseline": np.full(len(y_validation), baseline.class_prior_[1])}
    test_probabilities = {"Dummy baseline": np.full(len(y_test), baseline.class_prior_[1])}

    logistic_preprocessing = ColumnTransformer([
        ("categorical", OneHotEncoder(handle_unknown="ignore", min_frequency=10, dtype=np.float32), CAT_FEATURES),
        ("numeric", StandardScaler(), NUM_FEATURES),
    ], sparse_threshold=0.3)
    logistic = Pipeline([
        ("preprocessing", logistic_preprocessing),
        ("model", SGDClassifier(loss="log_loss", penalty="elasticnet", alpha=1e-5, l1_ratio=0.05, class_weight="balanced", max_iter=60, tol=1e-4, random_state=SEED, average=True)),
    ])
    logistic.fit(X_train, y_train)
    validation_probabilities["Regularized logistic"] = logistic.predict_proba(X_validation)[:, 1]
    test_probabilities["Regularized logistic"] = logistic.predict_proba(X_test)[:, 1]

    category_maps = fit_category_maps(X_train)
    encoded_train = encode_lightgbm(X_train, category_maps)
    encoded_validation = encode_lightgbm(X_validation, category_maps)
    encoded_test = encode_lightgbm(X_test, category_maps)
    categorical_indices = list(range(len(CAT_FEATURES)))

    base_lightgbm = LGBMClassifier(
        n_estimators=350, learning_rate=0.05, num_leaves=31, min_child_samples=50,
        subsample=0.9, colsample_bytree=0.9, reg_alpha=0.0, reg_lambda=1.0,
        class_weight="balanced", random_state=SEED, n_jobs=-1, verbosity=-1,
    )
    base_lightgbm.fit(
        encoded_train, y_train, categorical_feature=categorical_indices,
        eval_set=[(encoded_validation, y_validation)], eval_metric="binary_logloss",
        callbacks=[early_stopping(40, verbose=False), log_evaluation(0)],
    )
    validation_probabilities["LightGBM base"] = base_lightgbm.predict_proba(encoded_validation)[:, 1]
    test_probabilities["LightGBM base"] = base_lightgbm.predict_proba(encoded_test)[:, 1]

    frequency_maps = fit_frequency_maps(X_train)
    dense_train, dense_mean, dense_std = encode_dense(X_train, frequency_maps)
    dense_validation, _, _ = encode_dense(X_validation, frequency_maps, dense_mean, dense_std)
    dense_test, _, _ = encode_dense(X_test, frequency_maps, dense_mean, dense_std)
    mlp = MLPClassifier(
        hidden_layer_sizes=(64, 32), activation="relu", solver="adam", alpha=1e-4,
        batch_size=2048, learning_rate_init=0.001, max_iter=1, warm_start=True,
        shuffle=True, random_state=SEED,
    )
    best_mlp, best_mlp_score, stale = None, -1.0, 0
    mlp_history = []
    for epoch in range(1, 21):
        mlp.partial_fit(dense_train, y_train, classes=np.array([0, 1]) if epoch == 1 else None)
        probability = mlp.predict_proba(dense_validation)[:, 1]
        score = f1_score(y_validation, probability >= 0.5, average="macro", zero_division=0)
        mlp_history.append({"epoch": epoch, "validation_macro_f1": float(score), "loss": float(mlp.loss_)})
        if score > best_mlp_score + 1e-4:
            best_mlp, best_mlp_score, stale = copy.deepcopy(mlp), float(score), 0
        else:
            stale += 1
            if stale >= 4:
                break
    validation_probabilities["Dense MLP"] = best_mlp.predict_proba(dense_validation)[:, 1]
    test_probabilities["Dense MLP"] = best_mlp.predict_proba(dense_test)[:, 1]
    json_dump(RESULTS / "mlp_history.json", mlp_history)

    embedding_category_train = encode_categories(X_train, category_maps)
    embedding_category_validation = encode_categories(X_validation, category_maps)
    embedding_category_test = encode_categories(X_test, category_maps)
    numeric_train = X_train[NUM_FEATURES].to_numpy(np.float32)
    numeric_validation = X_validation[NUM_FEATURES].to_numpy(np.float32)
    numeric_test = X_test[NUM_FEATURES].to_numpy(np.float32)
    embedding_model, embedding_history = train_embedding_network(
        embedding_category_train, numeric_train, y_train,
        embedding_category_validation, numeric_validation, y_validation,
        seed=SEED, max_epochs=10, patience=3,
    )
    validation_probabilities["Entity-embedding network"] = embedding_model.predict_proba(embedding_category_validation, numeric_validation)[:, 1]
    test_probabilities["Entity-embedding network"] = embedding_model.predict_proba(embedding_category_test, numeric_test)[:, 1]
    json_dump(RESULTS / "embedding_history.json", embedding_history)

    validation_comparison = []
    for name, probability in validation_probabilities.items():
        record = metrics_for(name, y_validation, probability, 0.5)
        validation_comparison.append({key: value for key, value in record.items() if key not in {"classification_report", "confusion_matrix"}})
    pd.DataFrame(validation_comparison).sort_values("macro_f1", ascending=False).to_csv(RESULTS / "validation_model_comparison.csv", index=False)

    # Hyperparameter search uses validation only and keeps the test set locked.
    trials = [
        {"num_leaves": 15, "min_child_samples": 50, "learning_rate": 0.05, "reg_lambda": 1.0},
        {"num_leaves": 31, "min_child_samples": 50, "learning_rate": 0.05, "reg_lambda": 2.0},
        {"num_leaves": 31, "min_child_samples": 100, "learning_rate": 0.03, "reg_lambda": 2.0},
        {"num_leaves": 63, "min_child_samples": 100, "learning_rate": 0.03, "reg_lambda": 3.0},
    ]
    trial_rows = []
    best_model = None
    best_trial_score = -1.0
    best_parameters = None
    best_model_threshold = 0.5
    for number, parameters in enumerate(trials, 1):
        model = LGBMClassifier(
            n_estimators=700, subsample=0.9, colsample_bytree=0.9, reg_alpha=0.0,
            class_weight="balanced", random_state=SEED, n_jobs=-1, verbosity=-1,
            **parameters,
        )
        model.fit(
            encoded_train, y_train, categorical_feature=categorical_indices,
            eval_set=[(encoded_validation, y_validation)], eval_metric="binary_logloss",
            callbacks=[early_stopping(60, verbose=False), log_evaluation(0)],
        )
        probability = model.predict_proba(encoded_validation)[:, 1]
        threshold, score = best_threshold(y_validation, probability)
        trial_rows.append({"trial": number, **parameters, "best_iteration": int(model.best_iteration_), "threshold": threshold, "validation_macro_f1": score})
        if score > best_trial_score:
            best_model, best_trial_score = model, score
            best_parameters, best_model_threshold = parameters, threshold
    pd.DataFrame(trial_rows).to_csv(RESULTS / "lightgbm_trials.csv", index=False)

    final_validation_probability = best_model.predict_proba(encoded_validation)[:, 1]
    final_test_probability = best_model.predict_proba(encoded_test)[:, 1]
    validation_probabilities["Optimized LightGBM"] = final_validation_probability
    test_probabilities["Optimized LightGBM"] = final_test_probability

    validation_metrics = metrics_for("Optimized LightGBM", y_validation, final_validation_probability, best_model_threshold)
    test_metrics = metrics_for("Optimized LightGBM", y_test, final_test_probability, best_model_threshold)
    all_test_metrics = [
        metrics_for(name, y_test, probability, best_model_threshold if name == "Optimized LightGBM" else 0.5)
        for name, probability in test_probabilities.items()
    ]
    json_dump(RESULTS / "validation_metrics.json", validation_metrics)
    json_dump(RESULTS / "test_metrics.json", test_metrics)
    json_dump(RESULTS / "all_test_metrics.json", all_test_metrics)
    pd.DataFrame([{key: value for key, value in item.items() if key not in {"classification_report", "confusion_matrix"}} for item in all_test_metrics]).to_csv(RESULTS / "test_model_comparison.csv", index=False)

    # Ablation study on the optimized settings.
    ablations = [
        ("Full feature set", []),
        ("Remove Work_Center", ["Work_Center"]),
        ("Remove location group", ["Sub_Council", "Ward", "Suburb"]),
        ("Remove temporal group", ["day_of_week", "day_index", "day_of_month", "is_weekend"]),
        ("Remove coordinate-quality flags", ["coord_missing", "coord_zero"]),
    ]
    ablation_rows = []
    for label, removed in ablations:
        kept_cat = [value for value in CAT_FEATURES if value not in removed]
        kept_num = [value for value in NUM_FEATURES if value not in removed]
        kept_maps = fit_category_maps(X_train, kept_cat)
        train_encoded = encode_lightgbm(X_train, kept_maps, kept_cat, kept_num)
        validation_encoded = encode_lightgbm(X_validation, kept_maps, kept_cat, kept_num)
        model = LGBMClassifier(
            n_estimators=int(best_model.best_iteration_ or 100), subsample=0.9, colsample_bytree=0.9,
            reg_alpha=0.0, class_weight="balanced", random_state=SEED, n_jobs=-1, verbosity=-1,
            **best_parameters,
        )
        model.fit(train_encoded, y_train, categorical_feature=list(range(len(kept_cat))))
        probability = model.predict_proba(validation_encoded)[:, 1]
        score = f1_score(y_validation, probability >= best_model_threshold, average="macro", zero_division=0)
        ablation_rows.append({"ablation": label, "removed_features": ", ".join(removed), "validation_macro_f1": float(score)})
    full_score = ablation_rows[0]["validation_macro_f1"]
    for row in ablation_rows:
        row["delta_vs_full"] = row["validation_macro_f1"] - full_score
    pd.DataFrame(ablation_rows).to_csv(RESULTS / "ablation_results.csv", index=False)

    # Learning curve on chronologically earliest fractions of training data.
    learning_rows = []
    for fraction in [0.2, 0.4, 0.6, 0.8, 1.0]:
        count = int(len(X_train) * fraction)
        model = LGBMClassifier(
            n_estimators=int(best_model.best_iteration_ or 100), subsample=0.9, colsample_bytree=0.9,
            reg_alpha=0.0, class_weight="balanced", random_state=SEED, n_jobs=-1, verbosity=-1,
            **best_parameters,
        )
        model.fit(encoded_train[:count], y_train[:count], categorical_feature=categorical_indices)
        train_probability = model.predict_proba(encoded_train[:count])[:, 1]
        validation_probability = model.predict_proba(encoded_validation)[:, 1]
        learning_rows.append({
            "training_fraction": fraction,
            "training_rows": count,
            "training_macro_f1": float(f1_score(y_train[:count], train_probability >= best_model_threshold, average="macro", zero_division=0)),
            "validation_macro_f1": float(f1_score(y_validation, validation_probability >= best_model_threshold, average="macro", zero_division=0)),
        })
    learning = pd.DataFrame(learning_rows)
    learning.to_csv(RESULTS / "learning_curve.csv", index=False)
    plt.figure(figsize=(7, 4))
    plt.plot(learning.training_rows, learning.training_macro_f1, marker="o", label="Training")
    plt.plot(learning.training_rows, learning.validation_macro_f1, marker="o", label="Validation")
    plt.xlabel("Chronological training rows")
    plt.ylabel("Macro-F1")
    plt.title("Optimized LightGBM learning curve")
    plt.legend()
    save_figure("08_learning_curve.png")

    # Model comparison figure.
    comparison = pd.read_csv(RESULTS / "test_model_comparison.csv").sort_values("macro_f1")
    plt.figure(figsize=(8, 5))
    plt.barh(comparison.model, comparison.macro_f1, color="#457B9D")
    plt.xlabel("Locked-test macro-F1")
    plt.title("Model comparison on the locked test period")
    save_figure("09_test_model_comparison.png")

    # Confusion matrix and curves for final model.
    final_prediction = (final_test_probability >= best_model_threshold).astype(np.int8)
    matrix = confusion_matrix(y_test, final_prediction)
    plt.figure(figsize=(5, 4))
    plt.imshow(matrix, cmap="Blues")
    for (row, column), value in np.ndenumerate(matrix):
        plt.text(column, row, f"{value:,}", ha="center", va="center")
    plt.xticks([0, 1], ["Within 7 days", "At risk"])
    plt.yticks([0, 1], ["Within 7 days", "At risk"])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Optimized LightGBM confusion matrix")
    save_figure("10_confusion_matrix.png")

    fpr, tpr, _ = roc_curve(y_test, final_test_probability)
    precision, recall, _ = precision_recall_curve(y_test, final_test_probability)
    figure, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(fpr, tpr, color="#2A9D8F")
    axes[0].plot([0, 1], [0, 1], linestyle="--", color="gray")
    axes[0].set(title="ROC curve", xlabel="False-positive rate", ylabel="True-positive rate")
    axes[1].plot(recall, precision, color="#E76F51")
    axes[1].set(title="Precision-recall curve", xlabel="Recall", ylabel="Precision")
    save_figure("11_roc_pr_curves.png")

    # Paired final-model comparison against the dense MLP.
    mlp_prediction = (test_probabilities["Dense MLP"] >= 0.5).astype(np.int8)
    final_correct = final_prediction == y_test
    mlp_correct = mlp_prediction == y_test
    b = int((final_correct & ~mlp_correct).sum())
    c = int((~final_correct & mlp_correct).sum())
    p_value = float(binomtest(min(b, c), b + c, 0.5, alternative="two-sided").pvalue) if b + c else 1.0
    json_dump(RESULTS / "mcnemar_test.json", {"optimized_lightgbm_only_correct": b, "dense_mlp_only_correct": c, "exact_two_sided_p_value": p_value})

    # Subgroup audit.
    subgroup_rows = []
    for group, indexes in test_frame.groupby("Sub_Council").groups.items():
        indexes = np.asarray(list(indexes), dtype=int)
        if len(indexes) < 200:
            continue
        group_prediction = final_prediction[indexes]
        group_target = y_test[indexes]
        subgroup_rows.append({
            "Sub_Council": group,
            "rows": len(indexes),
            "actual_risk_rate": float(group_target.mean()),
            "predicted_review_rate": float(group_prediction.mean()),
            "at_risk_recall": float(recall_score(group_target, group_prediction, zero_division=0)),
            "false_positive_rate": float(((group_prediction == 1) & (group_target == 0)).sum() / max((group_target == 0).sum(), 1)),
        })
    subgroup = pd.DataFrame(subgroup_rows).sort_values("at_risk_recall")
    subgroup.to_csv(RESULTS / "subgroup_audit.csv", index=False)
    if not subgroup.empty:
        plt.figure(figsize=(8, 6))
        plt.barh(subgroup.Sub_Council.astype(str), subgroup.at_risk_recall, color="#6A4C93")
        plt.xlabel("At-risk recall")
        plt.title("Locked-test recall by sub-council (n >= 200)")
        save_figure("12_subgroup_recall.png")

    # Capacity scenario.
    capacity_rows = []
    order = np.argsort(-final_test_probability)
    for review_share in [0.10, 0.20, 0.30, 0.40, 0.50]:
        count = max(1, int(len(order) * review_share))
        selected = order[:count]
        capture = float(y_test[selected].sum() / max(y_test.sum(), 1))
        precision = float(y_test[selected].mean())
        capacity_rows.append({"review_share": review_share, "review_rows": count, "at_risk_capture": capture, "review_precision": precision})
    pd.DataFrame(capacity_rows).to_csv(RESULTS / "capacity_scenarios.csv", index=False)

    # Demonstration inputs come from held-out cases; identifiers and raw coordinates are omitted.
    demonstration_indexes = np.linspace(0, len(X_test) - 1, 3, dtype=int)
    demo = X_test.iloc[demonstration_indexes].copy()
    demo.insert(0, "case", ["Example 1", "Example 2", "Example 3"])
    demo["observed_risk_7d"] = y_test[demonstration_indexes]
    demo["predicted_probability"] = final_test_probability[demonstration_indexes]
    demo.to_csv(RESULTS / "demo_valid_inputs.csv", index=False)
    invalid = demo.iloc[[0]][FEATURES].copy()
    invalid["C3_Complaint_Type"] = ""
    invalid.to_csv(RESULTS / "demo_invalid_input.csv", index=False)

    prediction_export = test_frame[["ObjectId", "Created_On_Date", TARGET]].copy()
    prediction_export["probability_at_risk"] = final_test_probability
    prediction_export["prediction_at_risk"] = final_prediction
    prediction_export.to_csv(RESULTS / "locked_test_predictions.csv", index=False)
    np.savez_compressed(
        RESULTS / "heldout_predictions.npz", y_test=y_test,
        optimized_lightgbm_probability=final_test_probability,
        dense_mlp_probability=test_probabilities["Dense MLP"],
    )

    bundle = {
        "model": best_model,
        "category_maps": category_maps,
        "categorical_features": CAT_FEATURES,
        "numeric_features": NUM_FEATURES,
        "features": FEATURES,
        "threshold": best_model_threshold,
        "seed": SEED,
        "best_parameters": best_parameters,
        "best_iteration": int(best_model.best_iteration_),
        "supported_start": "2026-04-01",
        "source_sha256": audit["source_sha256"],
        "package_note": "Load only this trusted joblib file from the assignment package.",
    }
    joblib.dump(bundle, CODE / "final_model.joblib", compress=3)
    joblib.dump({
        "baseline": baseline,
        "logistic": logistic,
        "base_lightgbm": base_lightgbm,
        "optimized_lightgbm": best_model,
        "dense_mlp": best_mlp,
        "embedding_model": embedding_model,
        "category_maps": category_maps,
        "frequency_maps": frequency_maps,
        "dense_mean": dense_mean,
        "dense_std": dense_std,
        "mlp_history": mlp_history,
        "embedding_history": embedding_history,
        "seed": SEED,
    }, CODE / "model_comparison_bundle.joblib", compress=3)

    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scikit_learn": sklearn_version,
        "scipy": scipy.__version__,
        "lightgbm": lgb.__version__,
        "joblib": joblib.__version__,
    }
    json_dump(RESULTS / "environment.json", environment)
    summary = {
        "dataset": audit,
        "selected_model": "Optimized LightGBM",
        "selected_threshold": best_model_threshold,
        "validation_macro_f1": validation_metrics["macro_f1"],
        "test_metrics": {key: value for key, value in test_metrics.items() if key not in {"classification_report", "confusion_matrix"}},
        "mcnemar_against_dense_mlp": {"b": b, "c": c, "p_value": p_value},
    }
    json_dump(RESULTS / "run_summary.json", summary)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
