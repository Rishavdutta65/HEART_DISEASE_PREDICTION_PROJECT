import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.graphics.shapes import Rect, String, Group, Line, Drawing
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

try:
    from svglib.svglib import svg2rlg
    SVGLIB_AVAILABLE = True
except ImportError:
    SVGLIB_AVAILABLE = False

def create_risk_meter(probability):
    """Creates a visual risk meter graphic using reportlab graphics."""
    d = Drawing(400, 40)
    
    # Background track
    d.add(Rect(0, 15, 400, 10, rx=5, ry=5, fillColor=colors.HexColor('#1e293b'), strokeColor=None))
    
    # Green zone (0-39%)
    d.add(Rect(0, 15, 160, 10, fillColor=colors.HexColor('#4ade80'), strokeColor=None))
    # Yellow zone (40-69%)
    d.add(Rect(160, 15, 120, 10, fillColor=colors.HexColor('#fbbf24'), strokeColor=None))
    # Red zone (70-100%)
    d.add(Rect(280, 15, 120, 10, fillColor=colors.HexColor('#f87171'), strokeColor=None))
    
    # Pointer
    pos_x = probability * 400
    d.add(Line(pos_x, 5, pos_x, 35, strokeColor=colors.black, strokeWidth=2))
    
    # Triangle marker
    from reportlab.graphics.shapes import Polygon
    d.add(Polygon([pos_x-5, 5, pos_x+5, 5, pos_x, 15], fillColor=colors.black, strokeColor=None))
    
    # Labels
    d.add(String(0, 0, "LOW", fontSize=8, fontName="Helvetica-Bold", fillColor=colors.HexColor('#4ade80')))
    d.add(String(180, 0, "MEDIUM", fontSize=8, fontName="Helvetica-Bold", fillColor=colors.HexColor('#fbbf24')))
    d.add(String(375, 0, "HIGH", fontSize=8, fontName="Helvetica-Bold", fillColor=colors.HexColor('#f87171')))
    
    # Current Score Label
    score_label = f"{int(probability*100)}%"
    d.add(String(pos_x - 5, 38, score_label, fontSize=9, fontName="Helvetica-Bold", fillColor=colors.black))
    
    return d

def create_feature_bars(importances):
    """Creates a bar chart for feature importances."""
    d = Drawing(400, 120)
    y_offset = 100
    
    for feature, val in importances:
        # Label
        d.add(String(0, y_offset, feature, fontSize=9, fontName="Helvetica", fillColor=colors.HexColor('#334155')))
        # Bar track
        d.add(Rect(100, y_offset-2, 250, 8, fillColor=colors.HexColor('#e2e8f0'), strokeColor=None))
        # Value bar (normalize to max width 250, assuming max val ~ 0.3)
        bar_w = min(250, (val / 0.3) * 250)
        d.add(Rect(100, y_offset-2, bar_w, 8, fillColor=colors.HexColor('#3b82f6'), strokeColor=None))
        # Percent text
        d.add(String(360, y_offset, f"{int(val*100)}%", fontSize=8, fontName="Helvetica-Bold", fillColor=colors.HexColor('#475569')))
        
        y_offset -= 20
        
    return d

def generate_medical_pdf(data, static_dir):
    """Generates the advanced medical PDF."""
    buffer = io.BytesIO()
    
    # Document Setup
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'MainTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'), spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'SubTitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=20
    )
    section_title = ParagraphStyle(
        'SectionTitle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1d4ed8'),
        spaceBefore=15, spaceAfter=10
    )
    normal_text = ParagraphStyle(
        'NormalText', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#334155'), leading=14
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#94a3b8'), leading=10,
        alignment=1 # Center
    )

    story = []
    
    # ------------------ A. HEADER ------------------
    # Try to load SVG logo
    logo_path = os.path.join(static_dir, 'logo.svg')
    header_data = []
    if SVGLIB_AVAILABLE and os.path.exists(logo_path):
        try:
            drawing = svg2rlg(logo_path)
            drawing.width = 60
            drawing.height = 60
            drawing.scale(60/512.0, 60/512.0) # 512x512 original
            header_data = [[drawing, Paragraph("<b>Heart Disease Prediction System</b><br/><font color='#64748b'>AI-Powered Health Analysis Report</font>", styles['Normal'])]]
        except Exception as e:
            print("SVG error:", e)
            header_data = [["", Paragraph("<b>Heart Disease Prediction System</b><br/><font color='#64748b'>AI-Powered Health Analysis Report</font>", styles['Normal'])]]
    else:
        header_data = [["", Paragraph("<b>Heart Disease Prediction System</b><br/><font color='#64748b'>AI-Powered Health Analysis Report</font>", styles['Normal'])]]

    header_table = Table(header_data, colWidths=[70, 400])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(header_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Meta Info
    report_id = f"REP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    meta_data = [
        [Paragraph(f"<b>Report ID:</b> {report_id}", normal_text), 
         Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%b %d, %Y %I:%M %p')}", normal_text)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 250])
    story.append(meta_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ------------------ B. PATIENT INFO ------------------
    story.append(Paragraph("Patient Information", section_title))
    inp = data.get('input_data', {})
    if not inp or not isinstance(inp, dict):
        inp = data
    
    # Map raw values to readable strings if possible
    cp_map = {0: "Typical Angina", 1: "Atypical Angina", 2: "Non-anginal Pain", 3: "Asymptomatic"}
    fbs_map = {0: "False (<= 120mg/dl)", 1: "True (> 120mg/dl)"}
    exang_map = {0: "No", 1: "Yes"}
    
    def get_val(key, default="N/A"):
        val = inp.get(key)
        if val is None or str(val).strip() == '' or str(val).lower() == 'n/a':
            return default
        return val

    def get_mapped(key, mapping, default="N/A"):
        val = inp.get(key)
        if val is None or str(val).strip() == '' or str(val).lower() == 'n/a':
            return default
        try:
            return mapping.get(int(float(val)), str(val))
        except:
            return str(val)

    age_val = get_val('age')
    age_str = f"{age_val} yrs" if age_val != "N/A" else "N/A"
    
    sex_val = inp.get('sex')
    if sex_val is None or str(sex_val).strip() == '' or str(sex_val).lower() == 'n/a':
        sex_str = "N/A"
    elif str(sex_val) in ['1', '1.0', 'Male']:
        sex_str = "Male"
    else:
        sex_str = "Female"

    cp_str = get_mapped('cp', cp_map)
    bp_val = get_val('trestbps')
    bp_str = f"{bp_val} mmHg" if bp_val != "N/A" else "N/A"
    chol_val = get_val('chol')
    chol_str = f"{chol_val} mg/dL" if chol_val != "N/A" else "N/A"
    fbs_str = get_mapped('fbs', fbs_map)
    
    restecg_map = {0: "Normal", 1: "ST-T Wave Abnormality", 2: "Left Ventricular Hypertrophy"}
    restecg_str = get_mapped('restecg', restecg_map)
    
    hr_val = get_val('thalach')
    hr_str = f"{hr_val} bpm" if hr_val != "N/A" else "N/A"
    exang_str = get_mapped('exang', exang_map)
    oldpeak_str = str(get_val('oldpeak'))
    
    slope_map = {0: "Upsloping", 1: "Flat", 2: "Downsloping"}
    slope_str = get_mapped('slope', slope_map)
    ca_str = str(get_val('ca'))
    
    thal_map = {1: "Fixed Defect", 2: "Normal", 3: "Reversible Defect"}
    thal_str = get_mapped('thal', thal_map)

    patient_table_data = [
        ["Age", age_str, "Sex", sex_str],
        ["Chest Pain", cp_str, "Resting BP", bp_str],
        ["Cholesterol", chol_str, "Fasting Sugar", fbs_str],
        ["Resting ECG", restecg_str, "Max Heart Rate", hr_str],
        ["Exercise Angina", exang_str, "ST Depression", oldpeak_str],
        ["Slope", slope_str, "Major Vessels", ca_str],
        ["Thalassemia", thal_str, "", ""]
    ]
    
    ptable = Table(patient_table_data, colWidths=[110, 140, 110, 140])
    ptable.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#334155')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
    ]))
    story.append(ptable)
    
    # ------------------ C. PREDICTION SUMMARY ------------------
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Prediction Summary", section_title))
    
    prob = data.get('probability', 0)
    pct = int(round(prob * 100))
    
    if pct >= 71:
        risk_level = "HIGH RISK"
        risk_color = colors.HexColor('#fef2f2')
        text_color = colors.HexColor('#ef4444')
    elif pct >= 41:
        risk_level = "MEDIUM RISK"
        risk_color = colors.HexColor('#fffbeb')
        text_color = colors.HexColor('#d97706')
    else:
        risk_level = "LOW RISK"
        risk_color = colors.HexColor('#f0fdf4')
        text_color = colors.HexColor('#22c55e')

    summary_data = [
        [Paragraph(f"<b>Prediction Result:</b><br/> <font color='{text_color}' size='14'><b>{risk_level}</b></font>", normal_text),
         Paragraph(f"<b>Risk Score:</b><br/> <font size='14'><b>{pct}%</b></font>", normal_text)],
        [Paragraph(f"<b>Model Accuracy:</b> {data.get('accuracy', 'N/A')}", normal_text),
         Paragraph(f"<b>Confidence:</b> {data.get('accuracy', 'N/A')} (Est.)", normal_text)]
    ]
    
    stable = Table(summary_data, colWidths=[250, 250])
    stable.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), risk_color),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(stable)
    
    # ------------------ D. VISUAL RISK METER ------------------
    story.append(Spacer(1, 0.2*inch))
    story.append(create_risk_meter(prob))
    
    # ------------------ E. AI ANALYSIS ------------------
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("AI Analysis Insights", section_title))
    
    importances = data.get('feature_importances', [])
    # Sort importances
    if isinstance(importances, dict):
        imp_sorted = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:5]
    elif isinstance(importances, list):
        # Handle if it's already a list of tuples
        imp_sorted = importances[:5]
    else:
        imp_sorted = []
        
    if imp_sorted:
        top1 = imp_sorted[0][0].replace('_', ' ')
        top2 = imp_sorted[1][0].replace('_', ' ')
        ai_text = f"Based on the machine learning model analysis, the attributes <b>{top1}</b> and <b>{top2}</b> contributed most significantly to the calculated risk score of {pct}%. The model evaluates 13 distinct cardiac features simultaneously to detect non-linear patterns associated with heart disease."
    else:
        ai_text = "The AI model has evaluated all 13 medical inputs to generate this risk score."
        
    story.append(Paragraph(ai_text, normal_text))
    
    # ------------------ F. FEATURE IMPORTANCE ------------------
    if imp_sorted:
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("Most Influential Factors:", ParagraphStyle('Sub', parent=normal_text, fontName='Helvetica-Bold')))
        story.append(Spacer(1, 0.1*inch))
        story.append(create_feature_bars(imp_sorted))

    # ------------------ G & H. RECOMMENDATIONS ------------------
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Personalized Recommendations", section_title))
    
    rec_text = ""
    if pct >= 71:
        rec_text = """
        • Consult a cardiologist<br/>
        • Undergo further medical tests<br/>
        • Follow medical advice<br/>
        • Regular monitoring
        """
    elif pct >= 41:
        rec_text = """
        • Improve diet<br/>
        • Increase physical activity<br/>
        • Monitor BP/cholesterol<br/>
        • Consult doctor if symptoms occur
        """
    else:
        rec_text = """
        • Maintain healthy diet<br/>
        • Regular exercise<br/>
        • Adequate sleep<br/>
        • Routine checkups
        """
        
    story.append(Paragraph(rec_text, normal_text))

    # ------------------ I. DISCLAIMER ------------------
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("This report is generated using an AI/ML prediction model and is intended for educational and screening purposes only. It should not replace professional medical diagnosis, advice, or treatment. Always consult a qualified healthcare provider regarding any medical condition.", disclaimer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
