from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime

def generate_loan_report_pdf(application_data: dict, decision_data: dict) -> BytesIO:
    """
    Generate a professional PDF report for loan application decision
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#e2e8f0'),
        borderPadding=5,
        backColor=colors.HexColor('#f1f5f9')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )
    
    # Title
    title = Paragraph("LOAN APPLICATION DECISION REPORT", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Timestamp
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    timestamp_para = Paragraph(f"<i>Generated: {timestamp}</i>", normal_style)
    elements.append(timestamp_para)
    elements.append(Spacer(1, 0.3*inch))
    
    # Decision Badge
    decision = decision_data.get('decision', 'Review')
    decision_color = {
        'Approve': colors.HexColor('#10b981'),
        'Reject': colors.HexColor('#ef4444'),
        'Review': colors.HexColor('#f59e0b')
    }.get(decision, colors.HexColor('#6b7280'))
    
    decision_style = ParagraphStyle(
        'DecisionStyle',
        parent=styles['Heading1'],
        fontSize=32,
        textColor=decision_color,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=20
    )
    
    decision_para = Paragraph(f"DECISION: {decision.upper()}", decision_style)
    elements.append(decision_para)
    elements.append(Spacer(1, 0.3*inch))
    
    # Applicant Information Section
    elements.append(Paragraph("APPLICANT INFORMATION", heading_style))
    
    currency_symbol = '₹' if application_data.get('currency') == 'INR' else '$'
    
    applicant_data = [
        ['User ID:', application_data.get('user_id', 'N/A')],
        ['Annual Income:', f"{currency_symbol}{application_data.get('income', 0):,.2f}"],
        ['Currency:', application_data.get('currency', 'USD')],
        ['Credit Score:', str(application_data.get('credit_score', 'N/A'))],
        ['Debt-to-Income Ratio:', f"{application_data.get('dti', 0):.2%}"],
        ['Employment Length:', f"{application_data.get('employment_length', 0)} years"],
        ['Loan Tenure:', f"{application_data.get('loan_tenure', 'Not specified')} years" if application_data.get('loan_tenure') else 'Not specified']
    ]
    
    applicant_table = Table(applicant_data, colWidths=[2.5*inch, 4*inch])
    applicant_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0'))
    ]))
    
    elements.append(applicant_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Payslip Verification Section
    payslip_data = application_data.get('payslip_verification', {})
    if payslip_data:
        elements.append(Paragraph("PAYSLIP VERIFICATION", heading_style))
        
        verification_status = "VERIFIED ✓" if payslip_data.get('verified') else "NOT VERIFIED ✗"
        verification_color = colors.HexColor('#10b981') if payslip_data.get('verified') else colors.HexColor('#ef4444')
        
        payslip_verification_data = [
            ['Verification Status:', verification_status],
            ['Payslip Document:', payslip_data.get('payslip_filename', 'N/A')],
            ['Claimed Income:', f"{currency_symbol}{payslip_data.get('claimed_income', 'N/A')}"],
            ['Verified On:', payslip_data.get('verification_timestamp', 'N/A')]
        ]
        
        payslip_table = Table(payslip_verification_data, colWidths=[2.5*inch, 4*inch])
        payslip_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (1, 0), (1, 0), verification_color),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0'))
        ]))
        
        elements.append(payslip_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Decision Summary Section
    elements.append(Paragraph("DECISION SUMMARY", heading_style))
    
    risk_score = decision_data.get('risk_score', 0)
    confidence = decision_data.get('confidence', 0)
    
    decision_summary_data = [
        ['Final Decision:', decision.upper()],
        ['Risk Score:', f"{risk_score * 100:.2f}%"],
        ['Confidence Level:', f"{confidence * 100:.2f}%"]
    ]
    
    decision_table = Table(decision_summary_data, colWidths=[2.5*inch, 4*inch])
    decision_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0'))
    ]))
    
    elements.append(decision_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # AI Explanation Section
    elements.append(Paragraph("ANALYSIS EXPLANATION", heading_style))
    explanation = decision_data.get('explanation', 'No explanation provided.')
    explanation_para = Paragraph(explanation, normal_style)
    elements.append(explanation_para)
    elements.append(Spacer(1, 0.3*inch))
    
    # Key Factors Section
    important_features = decision_data.get('important_features', [])
    if important_features:
        elements.append(Paragraph("KEY FACTORS ANALYSIS", heading_style))
        
        for idx, feature in enumerate(important_features, 1):
            feature_name = feature.get('feature', 'Unknown').replace('_', ' ').title()
            feature_impact = feature.get('impact', 'No impact data')
            
            feature_text = f"<b>{idx}. {feature_name}:</b> {feature_impact}"
            feature_para = Paragraph(feature_text, normal_style)
            elements.append(feature_para)
            elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.4*inch))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=6,
        borderWidth=1,
        borderColor=colors.HexColor('#e2e8f0'),
        borderPadding=10,
        backColor=colors.HexColor('#f8fafc')
    )
    
    disclaimer_text = """
    <b>DISCLAIMER:</b> This report is generated by an AI-powered loan underwriting system.
    The decision is based on machine learning analysis and should be reviewed by authorized
    personnel before final approval. This document is confidential and intended solely for the applicant.
    """
    
    disclaimer_para = Paragraph(disclaimer_text, disclaimer_style)
    elements.append(disclaimer_para)
    
    # Footer
    elements.append(Spacer(1, 0.2*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )
    footer_text = "AI Loan Underwriting System | Machine Learning & Explainable AI"
    footer_para = Paragraph(footer_text, footer_style)
    elements.append(footer_para)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    buffer.seek(0)
    return buffer
