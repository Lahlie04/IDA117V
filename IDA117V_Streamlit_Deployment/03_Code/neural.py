"""Small NumPy entity-embedding network used as the second neural model."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from sklearn.metrics import f1_score, log_loss


def _sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, -30, 30)
    return 1.0 / (1.0 + np.exp(-values))


def _embedding_dimension(cardinality: int) -> int:
    return min(12, max(3, round(np.sqrt(max(2, cardinality)))))


@dataclass
class EntityEmbeddingNetwork:
    embeddings: List[np.ndarray]
    weight_1: np.ndarray
    bias_1: np.ndarray
    weight_2: np.ndarray
    bias_2: np.ndarray
    numeric_mean: np.ndarray
    numeric_std: np.ndarray
    threshold: float = 0.5

    def _inputs(self, categorical: np.ndarray, numeric: np.ndarray) -> np.ndarray:
        pieces = [table[categorical[:, index]] for index, table in enumerate(self.embeddings)]
        scaled = (numeric - self.numeric_mean) / self.numeric_std
        return np.concatenate(pieces + [scaled.astype(np.float32)], axis=1)

    def predict_proba(self, categorical: np.ndarray, numeric: np.ndarray) -> np.ndarray:
        inputs = self._inputs(categorical, numeric)
        hidden = np.maximum(inputs @ self.weight_1 + self.bias_1, 0)
        probabilities = _sigmoid((hidden @ self.weight_2 + self.bias_2).ravel())
        return np.column_stack([1.0 - probabilities, probabilities])

    def predict(self, categorical: np.ndarray, numeric: np.ndarray) -> np.ndarray:
        return (self.predict_proba(categorical, numeric)[:, 1] >= self.threshold).astype(np.int8)


def train_embedding_network(
    categorical_train: np.ndarray,
    numeric_train: np.ndarray,
    y_train: np.ndarray,
    categorical_validation: np.ndarray,
    numeric_validation: np.ndarray,
    y_validation: np.ndarray,
    seed: int = 42,
    hidden_units: int = 48,
    max_epochs: int = 10,
    patience: int = 3,
    batch_size: int = 4096,
    learning_rate: float = 0.0015,
    weight_decay: float = 1e-5,
) -> Tuple[EntityEmbeddingNetwork, List[Dict[str, float]]]:
    rng = np.random.default_rng(seed)
    cardinalities = [int(categorical_train[:, i].max()) for i in range(categorical_train.shape[1])]
    dimensions = [_embedding_dimension(value) for value in cardinalities]
    embeddings = [
        rng.normal(0, 0.03, size=(cardinality + 1, dimension)).astype(np.float32)
        for cardinality, dimension in zip(cardinalities, dimensions)
    ]
    numeric_mean = numeric_train.mean(axis=0).astype(np.float32)
    numeric_std = numeric_train.std(axis=0).astype(np.float32)
    numeric_std = np.where(numeric_std < 1e-6, 1.0, numeric_std).astype(np.float32)
    input_width = sum(dimensions) + numeric_train.shape[1]
    weight_1 = rng.normal(0, np.sqrt(2 / input_width), size=(input_width, hidden_units)).astype(np.float32)
    bias_1 = np.zeros(hidden_units, np.float32)
    weight_2 = rng.normal(0, np.sqrt(2 / hidden_units), size=(hidden_units, 1)).astype(np.float32)
    bias_2 = np.zeros(1, np.float32)

    params = embeddings + [weight_1, bias_1, weight_2, bias_2]
    first_moment = [np.zeros_like(value) for value in params]
    second_moment = [np.zeros_like(value) for value in params]
    beta_1, beta_2, epsilon = 0.9, 0.999, 1e-8
    step = 0

    positives = max(int(y_train.sum()), 1)
    negatives = max(len(y_train) - positives, 1)
    positive_weight = len(y_train) / (2 * positives)
    negative_weight = len(y_train) / (2 * negatives)

    best_state = None
    best_score = -1.0
    stale = 0
    history: List[Dict[str, float]] = []

    slices = []
    offset = 0
    for dimension in dimensions:
        slices.append(slice(offset, offset + dimension))
        offset += dimension

    for epoch in range(1, max_epochs + 1):
        order = rng.permutation(len(y_train))
        epoch_loss = 0.0
        for start in range(0, len(order), batch_size):
            batch = order[start : start + batch_size]
            categorical = categorical_train[batch]
            numeric = numeric_train[batch]
            target = y_train[batch].astype(np.float32)
            pieces = [table[categorical[:, i]] for i, table in enumerate(embeddings)]
            numeric_scaled = (numeric - numeric_mean) / numeric_std
            inputs = np.concatenate(pieces + [numeric_scaled.astype(np.float32)], axis=1)
            pre_hidden = inputs @ weight_1 + bias_1
            hidden = np.maximum(pre_hidden, 0)
            logits = (hidden @ weight_2 + bias_2).ravel()
            probability = _sigmoid(logits)
            sample_weight = np.where(target == 1, positive_weight, negative_weight).astype(np.float32)
            epoch_loss += float(np.sum(sample_weight * (-(target * np.log(probability + 1e-8) + (1-target) * np.log(1-probability + 1e-8)))))

            dlogit = ((probability - target) * sample_weight / len(batch)).astype(np.float32)
            grad_weight_2 = hidden.T @ dlogit[:, None] + weight_decay * weight_2
            grad_bias_2 = np.array([dlogit.sum()], dtype=np.float32)
            dhidden = dlogit[:, None] @ weight_2.T
            dpre = dhidden * (pre_hidden > 0)
            grad_weight_1 = inputs.T @ dpre + weight_decay * weight_1
            grad_bias_1 = dpre.sum(axis=0)
            dinputs = dpre @ weight_1.T

            embedding_grads = []
            for index, table in enumerate(embeddings):
                gradient = np.zeros_like(table)
                np.add.at(gradient, categorical[:, index], dinputs[:, slices[index]])
                gradient += weight_decay * table
                embedding_grads.append(gradient)

            gradients = embedding_grads + [grad_weight_1, grad_bias_1, grad_weight_2, grad_bias_2]
            step += 1
            for index, (parameter, gradient) in enumerate(zip(params, gradients)):
                first_moment[index] = beta_1 * first_moment[index] + (1-beta_1) * gradient
                second_moment[index] = beta_2 * second_moment[index] + (1-beta_2) * (gradient * gradient)
                m_hat = first_moment[index] / (1 - beta_1 ** step)
                v_hat = second_moment[index] / (1 - beta_2 ** step)
                parameter -= learning_rate * m_hat / (np.sqrt(v_hat) + epsilon)

        model = EntityEmbeddingNetwork(
            embeddings, weight_1, bias_1, weight_2, bias_2, numeric_mean, numeric_std
        )
        validation_probability = model.predict_proba(categorical_validation, numeric_validation)[:, 1]
        validation_prediction = (validation_probability >= 0.5).astype(np.int8)
        score = f1_score(y_validation, validation_prediction, average="macro", zero_division=0)
        history.append({
            "epoch": epoch,
            "train_weighted_loss": epoch_loss / len(y_train),
            "validation_log_loss": float(log_loss(y_validation, validation_probability, labels=[0, 1])),
            "validation_macro_f1": float(score),
        })
        if score > best_score + 1e-4:
            best_score = float(score)
            best_state = copy.deepcopy(model)
            stale = 0
        else:
            stale += 1
            if stale >= patience:
                break

    if best_state is None:
        raise RuntimeError("Entity-embedding training did not produce a model.")
    return best_state, history
