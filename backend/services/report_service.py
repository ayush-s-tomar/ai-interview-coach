import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_report(session_data: dict) -> bytes:
    """Generate a styled PDF interview feedback report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle("Title", parent=styles["Title"],
        fontSize=22, textColor=colors.HexColor("#1a1a2e"), spaceAfter=4)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#4a4a8a"), spaceAfter=12)
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#2d2d72"), spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=10, leading=15, textColor=colors.HexColor("#333333"))
    tip_style = ParagraphStyle("Tip", parent=styles["Normal"],
        fontSize=9, leading=13, textColor=colors.HexColor("#555555"),
        leftIndent=10)
    score_label = ParagraphStyle("ScoreLabel", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#666666"))

    elements = []
    role = session_data.get("role", "Software Engineer")
    candidate = session_data.get("candidate_name", "Candidate")
    date_str = datetime.now().strftime("%B %d, %Y")
    scores_list = session_data.get("scores", [])
    questions = session_data.get("questions", [])
    answers = session_data.get("answers", [])

    # Header
    elements.append(Paragraph("AI Interview Coach", title_style))
    elements.append(Paragraph(f"Performance Report — {role} | {date_str}", subtitle_style))
    elements.append(Paragraph(f"Candidate: <b>{candidate}</b>", body_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2d2d72"), spaceAfter=12))

    # Overall summary table
    avg_scores = {
        "Relevance": 0, "Clarity": 0,
        "Technical Accuracy": 0, "Confidence": 0, "Overall": 0
    }
    if scores_list:
        for s in scores_list:
            avg_scores["Relevance"] += s.get("relevance", 0)
            avg_scores["Clarity"] += s.get("clarity", 0)
            avg_scores["Technical Accuracy"] += s.get("technical_accuracy", 0)
            avg_scores["Confidence"] += s.get("confidence", 0)
            avg_scores["Overall"] += s.get("overall", 0)
        n = len(scores_list)
        avg_scores = {k: round(v / n, 1) for k, v in avg_scores.items()}

    elements.append(Paragraph("Overall Performance", heading_style))

    def score_bar(score):
        filled = int(score)
        bar = "█" * filled + "░" * (10 - filled)
        return f"{bar}  {score}/10"

    summary_data = [["Dimension", "Score", "Visual"]]
    for dim, val in avg_scores.items():
        summary_data.append([dim, f"{val}/10", score_bar(val)])

    t = Table(summary_data, colWidths=[55*mm, 25*mm, 80*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2d2d72")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTSIZE", (0,0), (-1,0), 10),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f0f0f8"), colors.white]),
        ("FONTSIZE", (0,1), (-1,-1), 9),
        ("FONTNAME", (2,1), (2,-1), "Courier"),
        ("TEXTCOLOR", (2,1), (2,-1), colors.HexColor("#2d2d72")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 10))

    # Per-question breakdown
    elements.append(Paragraph("Question-by-Question Breakdown", heading_style))

    for i, (q, a, s) in enumerate(zip(questions, answers, scores_list), 1):
        block = []
        block.append(Paragraph(f"<b>Q{i}:</b> {q}", body_style))
        block.append(Spacer(1, 3))

        ans_text = a if len(a) <= 300 else a[:300] + "..."
        block.append(Paragraph(f"<i>Answer:</i> {ans_text}", tip_style))
        block.append(Spacer(1, 4))

        # Mini score row
        scores_row = [
            ["Relevance", "Clarity", "Tech Accuracy", "Confidence", "Overall"],
            [
                f"{s.get('relevance',0)}/10",
                f"{s.get('clarity',0)}/10",
                f"{s.get('technical_accuracy',0)}/10",
                f"{s.get('confidence',0)}/10",
                f"{s.get('overall',0)}/10",
            ]
        ]
        mini_t = Table(scores_row, colWidths=[32*mm]*5)
        mini_t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8e8f4")),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#bbbbcc")),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        block.append(mini_t)
        block.append(Spacer(1, 4))

        block.append(Paragraph(f"<b>Feedback:</b> {s.get('feedback','')}", body_style))
        block.append(Spacer(1, 3))

        tips = s.get("improvement_tips", [])
        if tips:
            block.append(Paragraph("<b>Improvement Tips:</b>", body_style))
            for tip in tips:
                block.append(Paragraph(f"• {tip}", tip_style))

        block.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor("#dddddd"), spaceAfter=8, spaceBefore=8))
        elements.append(KeepTogether(block))

    # Final recommendation
    overall = avg_scores.get("Overall", 0)
    if overall >= 7.5:
        verdict = "Strong Candidate — You demonstrated solid knowledge. Focus on depth in weak areas."
        verdict_color = "#1a7a1a"
    elif overall >= 5:
        verdict = "Promising — Good foundation with room to grow. Review flagged topics before your next interview."
        verdict_color = "#8a6a00"
    else:
        verdict = "Needs Work — Revisit the fundamentals and practice structured answers using the STAR method."
        verdict_color = "#8a1a1a"

    verdict_style = ParagraphStyle("Verdict", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor(verdict_color), leading=16)
    elements.append(Paragraph("Final Verdict", heading_style))
    elements.append(Paragraph(verdict, verdict_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "Generated by AI Interview Coach • Practice makes perfect.",
        ParagraphStyle("Footer", parent=styles["Normal"],
            fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(elements)
    return buffer.getvalue()
