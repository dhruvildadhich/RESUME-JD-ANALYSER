import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.schemas.analysis import AnalyzeResponse

def generate_analysis_report(data: AnalyzeResponse) -> io.BytesIO:
    """Generates a professional PDF report from the analysis data."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        textColor=colors.HexColor("#1e293b")
    )
    
    heading2 = ParagraphStyle(
        'Heading2Style',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor("#334155")
    )

    heading3 = ParagraphStyle(
        'Heading3Style',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor("#475569")
    )

    normal_style = styles['Normal']
    
    elements = []

    # 1. Header
    elements.append(Paragraph("AI Recruiter Intelligence Report", title_style))
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"<b>Generated:</b> {current_time}", normal_style))
    elements.append(Paragraph("<b>Evaluation Type:</b> Resume vs Job Description Analysis", normal_style))
    elements.append(Spacer(1, 20))

    # 2. Executive Summary
    elements.append(Paragraph("Executive Summary", heading2))
    
    cand_obj = getattr(data, "candidate_level", None)
    cand_level = getattr(cand_obj, "candidate_level", "N/A") if cand_obj else "N/A"
    
    conf_obj = getattr(data, "confidence", None)
    conf_level = f"{getattr(conf_obj, 'confidence_level', 'UNKNOWN')} Confidence" if conf_obj else "N/A"
    
    exec_data = [
        ["Overall Match Score", f"{data.match_score} / 100", data.hiring_recommendation],
        ["Candidate Level", cand_level, ""],
        ["Evaluation Confidence", conf_level, ""]
    ]
    
    t_exec = Table(exec_data, colWidths=[150, 150, 200])
    t_exec.setStyle(TableStyle([
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#334155")),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
    ]))
    elements.append(t_exec)
    elements.append(Spacer(1, 15))

    # 2b. Recruiter Decision Box
    rec_dec = getattr(data, "recruiter_decision", None)
    if rec_dec:
        decision_text = getattr(rec_dec, "decision", "N/A")
        risk_text = getattr(rec_dec, "risk_level", "N/A")
        reasons = getattr(rec_dec, "reasons", [])
        decision_color = colors.HexColor("#166534") if "Strong" in decision_text else (
            colors.HexColor("#92400e") if "Potential" in decision_text else colors.HexColor("#991b1b")
        )
        bg_color = colors.HexColor("#f0fdf4") if "Strong" in decision_text else (
            colors.HexColor("#fffbeb") if "Potential" in decision_text else colors.HexColor("#fef2f2")
        )
        rec_data = [[f"Recruiter Decision: {decision_text}", f"Risk: {risk_text}"]]
        t_rec = Table(rec_data, colWidths=[350, 150])
        t_rec.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), decision_color),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 14),
            ('FONTSIZE', (1, 0), (1, 0), 11),
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ]))
        elements.append(t_rec)
        if reasons:
            for r in reasons:
                elements.append(Paragraph(f"  • {r}", normal_style))
        elements.append(Spacer(1, 20))

    # 3. Score Breakdown Section
    elements.append(Paragraph("Score Breakdown", heading2))
    breakdown_data = [
        ["Category", "Weight", "Score"],
        ["Technical Skills Match", "40%", f"{int(data.skill_overlap_score)}%"],
        ["AI Engineering Depth", "25%", f"{int(data.project_experience_score)}%"],
        ["Semantic Similarity", "20%", f"{int(data.semantic_similarity_score)}%"],
        ["Production Engineering", "15%", f"{int(data.bonus_score)}%"],
    ]
    t_breakdown = Table(breakdown_data, colWidths=[200, 100, 100])
    t_breakdown.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    elements.append(t_breakdown)
    elements.append(Spacer(1, 20))

    # 4. Matched Skills Section
    elements.append(Paragraph("Matched Skills", heading2))
    if getattr(data, "matched_skills", None):
        skills_data = [["Skill", "Match Type", "Experience Level", "Evidence"]]
        for skill in data.matched_skills:
            evidence_val = getattr(skill, "evidence", None) or "N/A"
            evidence_para = Paragraph(evidence_val[:120] + ("..." if len(evidence_val) > 120 else ""), normal_style)
            req_skill = getattr(skill, "required_skill", None) or getattr(skill, "skill", "Unknown")
            exp_level = getattr(skill, "experience_level", None) or "Mention Only"
            skills_data.append([
                Paragraph(f"<b>{req_skill}</b>", normal_style),
                getattr(skill, "match_type", "UNKNOWN").replace("_MATCH", "").replace("_", " "),
                Paragraph(exp_level, normal_style),
                evidence_para
            ])
        t_skills = Table(skills_data, colWidths=[110, 85, 110, 195])
        t_skills.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(t_skills)
    else:
        elements.append(Paragraph("No skills matched.", normal_style))
    elements.append(Spacer(1, 20))

    # 5. Missing Skills Section
    elements.append(Paragraph("Missing Skills", heading2))
    
    def _add_missing(title, items, importance):
        if not items:
            return
        elements.append(Paragraph(title, heading3))
        missing_data = [["Skill", "Importance", "Explanation"]]
        for item in items:
            explanation = (
                getattr(item, "note", None)
                or getattr(item, "reason", None)
                or "No explanation provided."
            )
            missing_data.append([
                Paragraph(getattr(item, "skill", "Unknown Skill"), normal_style),
                importance,
                Paragraph(explanation, normal_style)
            ])
        t_missing = Table(missing_data, colWidths=[130, 100, 280])
        t_missing.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(t_missing)
        elements.append(Spacer(1, 10))

    _add_missing("Critical Gaps", data.critical_gaps, "Critical")
    _add_missing("Recommended Improvements", data.recommended_improvements, "Recommended")
    _add_missing("Optional Skills", data.optional_skills, "Optional")
    
    if not (data.critical_gaps or data.recommended_improvements or data.optional_skills):
        elements.append(Paragraph("No notable missing skills.", normal_style))
    
    elements.append(Spacer(1, 10))

    # 6. AI Recruiter Evaluation Section
    elements.append(Paragraph("AI Recruiter Evaluation", heading2))
    elements.append(Paragraph("<b>Strengths</b>", heading3))
    if data.strengths:
        for s in data.strengths:
            elements.append(Paragraph(f"• {s}", normal_style))
    else:
        elements.append(Paragraph("No specific strengths identified.", normal_style))
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Areas To Improve</b>", heading3))
    if data.weaknesses:
        for w in data.weaknesses:
            elements.append(Paragraph(f"• {w}", normal_style))
    else:
        elements.append(Paragraph("No specific weaknesses identified.", normal_style))
        
    elements.append(Spacer(1, 20))
    
    # 7. Personalized Improvement Plan
    elements.append(Paragraph("Personalized Improvement Plan", heading2))
    improvement_plan = getattr(data, "improvement_plan", None)
    if improvement_plan:
        for i, item in enumerate(improvement_plan, 1):
            skill = getattr(item, "missing_skill", "")
            priority = getattr(item, "priority", "")
            suggestion = getattr(item, "suggestion", "")
            elements.append(Paragraph(f"<b>{i}. [{priority}] {skill}</b>", normal_style))
            elements.append(Paragraph(suggestion, normal_style))
            elements.append(Spacer(1, 6))
    elif data.suggestions:
        for i, suggestion in enumerate(data.suggestions, 1):
            elements.append(Paragraph(f"<b>{i}.</b> {suggestion}", normal_style))
            elements.append(Spacer(1, 5))
    else:
        elements.append(Paragraph("No suggestions available.", normal_style))

    # 8. AI Confidence Analysis
    confidence_analysis = getattr(data, "confidence_analysis", None)
    if confidence_analysis:
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("Analysis Confidence", heading2))
        conf_score = getattr(confidence_analysis, "confidence_score", "N/A")
        conf_level = getattr(confidence_analysis, "level", "")
        conf_reasons = getattr(confidence_analysis, "reasons", [])
        elements.append(Paragraph(f"<b>Score: {conf_score}% ({conf_level})</b>", normal_style))
        for reason in conf_reasons:
            elements.append(Paragraph(f"  • {reason}", normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
