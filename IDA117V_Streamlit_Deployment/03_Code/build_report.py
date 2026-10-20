"""Generate a concise reproducibility appendix PDF from saved run evidence."""
from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "05_Results"
REPORT = ROOT / "01_Report" / "IDA117V_Reproducibility_Appendix.pdf"


def main() -> None:
    summary = json.loads((RESULTS / "run_summary.json").read_text(encoding="utf-8"))
    audit = summary["dataset"]
    metrics = summary["test_metrics"]
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=7.5, leading=9))
    styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], backColor=colors.HexColor("#FFF4E5"), borderColor=colors.HexColor("#E98B3A"), borderWidth=0.7, borderPadding=8, spaceBefore=8, spaceAfter=8))
    styles["Title"].textColor = colors.HexColor("#123B61")
    styles["Heading1"].textColor = colors.HexColor("#2F6B9A")

    doc = SimpleDocTemplate(str(REPORT), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=17*mm, bottomMargin=17*mm, title="IDA117V Reproducibility Appendix")
    story = [
        Paragraph("IDA117V Reproducibility Appendix", styles["Title"]),
        Paragraph("Predicting Seven-Day Municipal Service-Request Non-Completion Risk", styles["Heading2"]),
        Spacer(1, 6),
        Paragraph("This appendix records the exact source snapshot, execution protocol and model evidence produced by the repository package. It supplements, rather than replaces, the compiled assignment report.", styles["BodyText"]),
        Paragraph("Target repository: https://github.com/mahlatseselowa/IDA117V.git. The final target-repository commit hash is not stated here because it must be read from that exact repository after the package is committed.", styles["Callout"]),
        Paragraph("Dataset snapshot", styles["Heading1"]),
    ]
    data = [
        ["Item", "Code-derived value"],
        ["Source rows / columns", f"{audit['source_rows']:,} / {audit['source_columns']}"],
        ["Rows excluded: missing creation time", f"{audit['excluded_missing_creation_timestamp']:,}"],
        ["Model rows", f"{audit['model_rows']:,}"],
        ["Date coverage", f"{audit['date_min']} to {audit['date_max']}"],
        ["Within seven days", f"{audit['within_7_days']:,}"],
        ["At risk", f"{audit['at_risk']:,} ({audit['at_risk_rate']:.1%})"],
        ["Train / validation / test", f"{audit['splits']['train']:,} / {audit['splits']['validation']:,} / {audit['splits']['test']:,}"],
        ["Source SHA-256", audit['source_sha256']],
    ]
    table = Table(data, colWidths=[58*mm, 112*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#123B61")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#C7D2DC")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F4F7F9")]),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("LEADING", (0,0), (-1,-1), 10.5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [table, Spacer(1, 10), Paragraph("Locked-test result", styles["Heading1"])]
    metric_data = [
        ["Metric", "Optimized LightGBM"],
        ["Decision threshold", f"{metrics['threshold']:.2f}"],
        ["Accuracy", f"{metrics['accuracy']:.4f}"],
        ["Macro-F1", f"{metrics['macro_f1']:.4f}"],
        ["At-risk precision", f"{metrics['at_risk_precision']:.4f}"],
        ["At-risk recall", f"{metrics['at_risk_recall']:.4f}"],
        ["ROC-AUC", f"{metrics['roc_auc']:.4f}"],
        ["Average precision", f"{metrics['average_precision']:.4f}"],
    ]
    metric_table = Table(metric_data, colWidths=[85*mm, 85*mm], repeatRows=1)
    metric_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2A9D8F")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (1,1), (1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#C7D2DC")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F4F7F9")]),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [metric_table, Spacer(1, 10), Paragraph("Execution order", styles["Heading1"])]
    for number, text in enumerate([
        "Install the exact versions in requirements.txt using Python 3.12.",
        "Place the source workbook in 02_Data/raw; it is excluded from Git pending licence confirmation.",
        "Run 03_Code/run_analysis.py to regenerate the model, figures and result evidence.",
        "Run 03_Code/make_documentation.py to refresh the data dictionary and snapshot note.",
        "Run 03_Code/build_report.py to regenerate this appendix.",
        "Run 03_Code/verify_interface.py and then launch 03_Code/app.py with Streamlit.",
    ], 1):
        story.append(Paragraph(f"{number}. {text}", styles["BodyText"]))
    story += [Spacer(1, 8), Paragraph("Interpretation limits", styles["Heading1"])]
    for text in [
        "The seven-day horizon and creation-time availability of Work_Center require stakeholder confirmation.",
        "The extract covers only two months; seasonal and longer-term generalisation is not established.",
        "Missing completion is treated conservatively as at risk; source-system status semantics must be confirmed.",
        "Location fields may be quasi-identifiers. The model must not be used to deny, close or automatically deprioritise a request.",
        "Predictions are associations, not causal findings. Human review remains mandatory.",
    ]:
        story.append(Paragraph(f"• {text}", styles["BodyText"]))
    story += [
        Spacer(1, 8),
        Paragraph("Snapshot consistency", styles["Heading1"]),
        Paragraph(audit["note"], styles["Callout"]),
        Paragraph("Saved evidence inventory", styles["Heading1"]),
    ]
    for text in [
        "dataset_audit.json and run_summary.json - source fingerprint, split and headline metrics.",
        "validation_model_comparison.csv and test_model_comparison.csv - identical-case model comparison.",
        "lightgbm_trials.csv, ablation_results.csv and learning_curve.csv - controlled selection and diagnosis.",
        "heldout_predictions.npz and locked_test_predictions.csv - paired locked-test evidence.",
        "subgroup_audit.csv and capacity_scenarios.csv - fairness/operations review inputs.",
        "interface_ui_tests.json - three valid cases, one invalid case and HTTP health check.",
    ]:
        story.append(Paragraph(f"• {text}", styles["BodyText"]))
    story += [
        PageBreak(),
        Paragraph("Submission and approval status", styles["Heading1"]),
        Paragraph("The table distinguishes completed package evidence from items that still require external evidence. No approval, public link, signature or repository commit is claimed without support.", styles["BodyText"]),
    ]
    status_rows = [
        ["Item", "Status", "Evidence still required / control"],
        ["Manual-upload repository package", "Completed and verified locally", "Target URL supplied as https://github.com/mahlatseselowa/IDA117V.git; public accessibility and final commit hash remain unverified until upload/commit."],
        ["Dataset licence and redistribution", "Recorded metadata only; approval not claimed", "Exact item-level Custom License text, source-to-file chain of custody and written redistribution permission. Raw data remains excluded."],
        ["Entity-embedding architecture", "Implemented; lecturer approval required and not evidenced", "Dated lecturer email, LMS message, signed note or other explicit approval, or replace with an accepted architecture."],
        ["Streamlit deployment", "Local launch and health check verified", "Public app link is not created or verified."],
        ["Presentation/recording", "Plan and local demo evidence completed", "Public or lecturer-accessible recording link is not created or verified."],
        ["Contribution statement", "One-page blank template included", "Real names, student numbers, roles, specific outputs, dates and signatures."],
    ]
    status_table = Table(
        [[Paragraph(str(value), styles["Small"]) for value in row] for row in status_rows],
        colWidths=[40*mm, 43*mm, 87*mm], repeatRows=1,
    )
    status_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#123B61")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#C7D2DC")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F4F7F9")]),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story += [
        status_table,
        Spacer(1, 8),
        Paragraph("McNemar interpretation", styles["Heading1"]),
        Paragraph("McNemar's test in this project evaluates paired correctness on the same locked cases. It tests whether the two discordant probabilities - champion only correct versus comparator only correct - are equal. It does not test macro-F1 or the difference between macro-F1 scores. Macro-F1, precision and recall remain separate descriptive metrics for practical interpretation.", styles["Callout"]),
        Paragraph("Streamlit demonstration evidence", styles["Heading1"]),
    ]
    demo_rows = [
        ["Case", "Date", "Complaint", "Probability", "Expected / verified outcome"],
        ["Example 1", "2026-05-23", "Suspect Tampering", "79.7%", "At risk; observed at risk; passed"],
        ["Example 2", "2026-05-28", "Meter: Damaged / Faulty", "68.2%", "At risk; observed at risk; passed"],
        ["Example 3", "2026-05-30", "Customer Reconnection Request", "51.6%", "Below 0.65; observed within 7 days; passed"],
        ["Invalid", "-", "Blank complaint type", "-", "Complaint type is required; passed"],
    ]
    demo_table = Table(
        [[Paragraph(str(value), styles["Small"]) for value in row] for row in demo_rows],
        colWidths=[25*mm, 25*mm, 50*mm, 25*mm, 45*mm], repeatRows=1,
    )
    demo_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2A9D8F")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#C7D2DC")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F4F7F9")]),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story += [
        demo_table,
        Paragraph("Local launch and HTTP 200 are verified. Public Streamlit link: [NOT CREATED / NOT VERIFIED]. Presentation/recording link: [NOT CREATED / NOT VERIFIED].", styles["Callout"]),
        Paragraph("Target-repository hand-off", styles["Heading1"]),
        Paragraph("Commit the repository-ready package only after access to the exact target repository has been established. The raw workbook is intentionally excluded by .gitignore pending licence confirmation. After commit, verify the remote URL, a clean working tree and the 40-character HEAD hash. Never substitute the reference repository or reuse its commit hash.", styles["BodyText"]),
        Spacer(1, 8),
        Paragraph("Responsible-use conclusion", styles["Heading1"]),
        Paragraph("The evidence supports only a cautious human-controlled pilot - not automated denial, closure, deprioritisation, staff discipline or public ranking. Revalidate after material change.", styles["Callout"]),
    ]
    doc.build(story)
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
