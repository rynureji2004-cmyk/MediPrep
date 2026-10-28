import os
import logging
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

from app.repositories.lab_repository import LabRepository
from app.utilities.validators import format_datetime_display

logger = logging.getLogger(__name__)

# Base directory for storing individual sample laboratory test reports
SAMPLE_REPORTS_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'documentation', 'sample_patient_lab_reports'
))

class SampleReportCanvas(canvas.Canvas):
    """Custom canvas that renders running header and footer with SAMPLE disclaimers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        # Top Running Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor('#C53030')) # Crimson red
        self.drawString(36, 812, "SAMPLE REPORT — NOT FOR CLINICAL USE")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor('#718096'))
        self.drawRightString(559, 812, "MediPrep Hospital Readiness System • Demo Data Only")

        self.setStrokeColor(colors.HexColor('#E2E8F0'))
        self.setLineWidth(0.75)
        self.line(36, 806, 559, 806)

        # Bottom Running Footer
        self.line(36, 36, 559, 36)
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor('#C53030'))
        self.drawString(36, 25, "SAMPLE — NOT FOR CLINICAL USE")
        self.setFont("Helvetica", 7)
        self.setFillColor(colors.HexColor('#718096'))
        self.drawString(185, 25, "• Fictional illustrative test results generated for academic/system demonstration only •")
        self.drawRightString(559, 25, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_sample_report_filename(item):
    """Generates unique standardized filename for sample test report."""
    first_name = (item.get('patient_first_name') or '').strip().replace(' ', '_')
    last_name = (item.get('patient_last_name') or '').strip().replace(' ', '_')
    task_name = item.get('task_name', '')
    proc_id = item.get('procedure_id')

    if proc_id == 10 or 'Renal' in task_name or 'Creatinine' in task_name:
        return f"{first_name}_{last_name}_Sample_Renal_Function_Report.pdf"
    elif proc_id == 1 or 'ECG' in task_name:
        return f"{first_name}_{last_name}_Sample_ECG_Report.pdf"
    return f"{first_name}_{last_name}_Sample_Lab_Report.pdf"


def generate_single_sample_report_pdf(item, target_dir=None):
    """
    Generates a single, professional sample laboratory test report PDF.
    Strictly excludes patient ID 86 (aaa bbb) and cancelled procedures.
    Every report prominently states 'SAMPLE — NOT FOR CLINICAL USE' with fictional illustrative test results.
    """
    patient_id = item.get('patient_user_id') or item.get('patient_id')
    # Safety guard: Completely exclude patient ID 86 (aaa bbb)
    if patient_id == 86 or item.get('patient_email') == 'bbbb123@gmail.com' or item.get('schedule_status') == 'cancelled':
        logger.warning(f"Skipping sample report generation for excluded patient ID {patient_id}")
        return None

    if not target_dir:
        target_dir = SAMPLE_REPORTS_DIR
    os.makedirs(target_dir, exist_ok=True)

    filename = get_sample_report_filename(item)
    pdf_path = os.path.join(target_dir, filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42,
        pageCompression=0
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        textColor=colors.HexColor('#1A365D')
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#4A5568')
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=5,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#2D3748')
    )

    label_style = ParagraphStyle(
        'FieldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#4A5568')
    )

    value_style = ParagraphStyle(
        'FieldValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#1A202C')
    )

    table_th = ParagraphStyle(
        'TableTH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    table_td = ParagraphStyle(
        'TableTD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#2D3748')
    )

    table_td_center = ParagraphStyle(
        'TableTDCenter',
        parent=table_td,
        alignment=TA_CENTER
    )

    flag_normal = ParagraphStyle(
        'FlagNormal',
        parent=table_td,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#22543D'),
        alignment=TA_CENTER
    )

    disclaimer_text = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#742A2A'),
        alignment=TA_CENTER
    )

    elements = []

    # 1. Prominent Warning Banner: SAMPLE — NOT FOR CLINICAL USE
    banner_data = [[
        Paragraph(
            "<b>SAMPLE REPORT — NOT FOR CLINICAL USE</b><br/>"
            "<font size='7'>FICTIONAL DEMONSTRATION TEST RESULTS • GENERATED STRICTLY FOR MEDIPREP SYSTEM TESTING</font>",
            disclaimer_text
        )
    ]]
    banner_table = Table(banner_data, colWidths=[523])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FED7D7')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E53E3E')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 6))

    # 2. Hospital & Laboratory Information Header
    is_renal = (item.get('procedure_id') == 10) or ('Renal' in item.get('task_name', ''))
    dept_name = "Division of Clinical Biochemistry" if is_renal else "Division of Cardiopulmonary Diagnostics"
    test_title = "RENAL FUNCTION TEST REPORT" if is_renal else "12-LEAD ELECTROCARDIOGRAM (ECG) REPORT"
    ref_code = f"SMP-REN-2026-PT{patient_id}" if is_renal else f"SMP-ECG-2026-PT{patient_id}"

    header_data = [
        [
            Paragraph("<b>CENTRAL HOSPITAL CLINICAL LABORATORY</b><br/>"
                      f"<font size='7.5' color='#4A5568'>{dept_name}</font><br/>"
                      "<font size='6.5' color='#718096'>NABH / NABL Accredited Diagnostic Center • MediPrep Healthcare</font>", body_style),
            Paragraph(f"<b>REPORT REF:</b> {ref_code}<br/>"
                      f"<b>SAMPLE DATE:</b> 26-10-2026<br/>"
                      "<b>DOCUMENT TYPE:</b> <font color='#C53030'><b>Fictional Demo Report</b></font>",
                      ParagraphStyle('HRight', parent=body_style, alignment=TA_RIGHT, fontSize=7.5, leading=9.5))
        ]
    ]
    header_table = Table(header_data, colWidths=[310, 213])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E0'), spaceBefore=4, spaceAfter=6))

    # 3. Main Title
    pat_full_name = f"{item.get('patient_first_name', '')} {item.get('patient_last_name', '')}".strip()
    elements.append(Paragraph(f"{test_title} — {pat_full_name}", title_style))
    elements.append(Paragraph(f"Simulated pre-procedure diagnostic assessment report for <b>{item.get('procedure_name')}</b>.", subtitle_style))
    elements.append(Spacer(1, 6))

    # 4. Patient Demographics & Scheduled Procedure Details Card
    sched_dt = item.get('formatted_scheduled_at') or format_datetime_display(item.get('scheduled_at'))
    doc_name = f"Dr. {item.get('doctor_first_name', '')} {item.get('doctor_last_name', '')}".strip() or "Attending Physician"
    
    pat_info = [
        [
            Paragraph("<b>Patient Name:</b>", label_style),
            Paragraph(f"<b>{pat_full_name}</b>", value_style),
            Paragraph("<b>Patient User ID:</b>", label_style),
            Paragraph(f"#{patient_id}", value_style)
        ],
        [
            Paragraph("<b>Scheduled Procedure:</b>", label_style),
            Paragraph(f"{item.get('procedure_name')} (ID: #{item.get('procedure_id')})", value_style),
            Paragraph("<b>Procedure Date:</b>", label_style),
            Paragraph(f"<b>{sched_dt}</b>", value_style)
        ],
        [
            Paragraph("<b>Referring Physician:</b>", label_style),
            Paragraph(f"<b>{doc_name}</b>", value_style),
            Paragraph("<b>Clinical Facility:</b>", label_style),
            Paragraph(item.get('location') or "Hospital Main Diagnostic Suite", value_style)
        ],
        [
            Paragraph("<b>Specimen / Tracing:</b>", label_style),
            Paragraph("Serum (Venous Blood)" if is_renal else "Standard 12-Lead Surface ECG", value_style),
            Paragraph("<b>Report Status:</b>", label_style),
            Paragraph("<font color='#C53030'><b>SAMPLE (Illustrative Only)</b></font>", value_style)
        ]
    ]
    info_table = Table(pat_info, colWidths=[115, 145, 115, 148])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8))

    # 5. Diagnostic Test Results Section
    if is_renal:
        elements.append(Paragraph("1. Illustrative Renal Function Panel Results", section_heading))
        elements.append(Paragraph("<b>Methodology:</b> Automated Enzymatic Creatinine / CKD-EPI 2021 eGFR Equation. (Illustrative values for demo).", body_style))
        elements.append(Spacer(1, 3))

        renal_results = [
            [
                Paragraph("<b>Investigation / Parameter</b>", table_th),
                Paragraph("<b>Illustrative Result</b>", table_th),
                Paragraph("<b>Units</b>", table_th),
                Paragraph("<b>Biological Reference Interval</b>", table_th),
                Paragraph("<b>Status / Flag</b>", table_th)
            ],
            [
                Paragraph("<b>Serum Creatinine</b>", table_td),
                Paragraph("<b>0.96</b>", table_td_center),
                Paragraph("mg/dL", table_td_center),
                Paragraph("0.70 – 1.20", table_td_center),
                Paragraph("Normal (Sample)", flag_normal)
            ],
            [
                Paragraph("<b>eGFR (CKD-EPI Formula)</b>", table_td),
                Paragraph("<b>94.5</b>", table_td_center),
                Paragraph("mL/min/1.73 m²", table_td_center),
                Paragraph("&ge; 60.0 (Normal Filtration)", table_td_center),
                Paragraph("Normal (Sample)", flag_normal)
            ],
            [
                Paragraph("<b>Blood Urea Nitrogen (BUN)</b>", table_td),
                Paragraph("<b>14.2</b>", table_td_center),
                Paragraph("mg/dL", table_td_center),
                Paragraph("7.0 – 20.0", table_td_center),
                Paragraph("Normal (Sample)", flag_normal)
            ],
            [
                Paragraph("<b>BUN / Creatinine Ratio</b>", table_td),
                Paragraph("<b>14.8</b>", table_td_center),
                Paragraph("Ratio", table_td_center),
                Paragraph("10.0 – 20.0", table_td_center),
                Paragraph("Normal (Sample)", flag_normal)
            ],
            [
                Paragraph("<b>Serum Electrolytes (Sodium / Potassium)</b>", table_td),
                Paragraph("139 / 4.2", table_td_center),
                Paragraph("mEq/L", table_td_center),
                Paragraph("Na: 135-145 | K: 3.5-5.0", table_td_center),
                Paragraph("Normal (Sample)", flag_normal)
            ]
        ]
        res_table = Table(renal_results, colWidths=[140, 80, 80, 125, 98])
        res_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#234E52')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),
            ('TOPPADDING', (0,0), (-1,-1), 3.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ]))
        elements.append(res_table)
        elements.append(Spacer(1, 8))

        # Clinical Interpretation Box
        elements.append(Paragraph("2. Illustrative Clinical Interpretation & Contrast Assessment", section_heading))
        interp_text = (
            "<b>Pre-Procedural Clearance Assessment (Illustrative Demonstration):</b><br/>"
            "• Patient demonstrates physiological serum creatinine (0.96 mg/dL) and preserved glomerular filtration rate (eGFR 94.5 mL/min/1.73 m²).<br/>"
            "• <b>Contrast Safety:</b> eGFR &ge; 60 mL/min/1.73 m² indicates normal renal clearance. Standard clinical protocol allows iodinated contrast injection for the scheduled CT Scan Abdomen and Pelvis.<br/>"
            "• <i>Notice: All values and statements above are simulated demonstration entries for MediPrep testing.</i>"
        )
    else:
        elements.append(Paragraph("1. Illustrative 12-Lead Electrocardiogram Parameters", section_heading))
        elements.append(Paragraph("<b>Tracing Specifications:</b> 25 mm/s paper speed, 10 mm/mV calibration, standard limb and precordial lead placement. (Illustrative parameters for demo).", body_style))
        elements.append(Spacer(1, 3))

        ecg_params = [
            [
                Paragraph("<b>ECG Measurement Parameter</b>", table_th),
                Paragraph("<b>Illustrative Result</b>", table_th),
                Paragraph("<b>Units</b>", table_th),
                Paragraph("<b>Physiological Reference Range</b>", table_th),
                Paragraph("<b>Status / Flag</b>", table_th)
            ],
            [
                Paragraph("<b>Ventricular Heart Rate</b>", table_td),
                Paragraph("<b>72</b>", table_td_center),
                Paragraph("beats/min", table_td_center),
                Paragraph("60 – 100 bpm", table_td_center),
                Paragraph("Normal Sinus (Sample)", flag_normal)
            ],
            [
                Paragraph("<b>PR Interval</b>", table_td),
                Paragraph("<b>158</b>", table_td_center),
                Paragraph("ms", table_td_center),
                Paragraph("120 – 200 ms", table_td_center),
                Paragraph("Normal Conduction", flag_normal)
            ],
            [
                Paragraph("<b>QRS Duration</b>", table_td),
                Paragraph("<b>86</b>", table_td_center),
                Paragraph("ms", table_td_center),
                Paragraph("&lt; 120 ms", table_td_center),
                Paragraph("Normal Depolarization", flag_normal)
            ],
            [
                Paragraph("<b>QT / QTc (Bazett Formula)</b>", table_td),
                Paragraph("<b>394 / 418</b>", table_td_center),
                Paragraph("ms", table_td_center),
                Paragraph("QTc &lt; 450 ms (Males) / 460 ms (Females)", table_td_center),
                Paragraph("Normal Repolarization", flag_normal)
            ],
            [
                Paragraph("<b>P - QRS - T Axes</b>", table_td),
                Paragraph("<b>52° / 64° / 48°</b>", table_td_center),
                Paragraph("degrees", table_td_center),
                Paragraph("Normal Axis (-30° to +90°)", table_td_center),
                Paragraph("Normal Axis (Sample)", flag_normal)
            ]
        ]
        res_table = Table(ecg_params, colWidths=[140, 80, 80, 125, 98])
        res_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),
            ('TOPPADDING', (0,0), (-1,-1), 3.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ]))
        elements.append(res_table)
        elements.append(Spacer(1, 8))

        # 12-Lead Findings Summary & Interpretation
        elements.append(Paragraph("2. Illustrative 12-Lead Analysis & Pre-Cath Findings", section_heading))
        interp_text = (
            "<b>12-Lead Electrocardiographic Assessment (Illustrative Demonstration):</b><br/>"
            "• <b>Rhythm & Conduction:</b> Normal Sinus Rhythm at 72 bpm. 1:1 atrioventricular conduction without evidence of pre-excitation.<br/>"
            "• <b>Limb Leads (I, II, III, aVR, aVL, aVF):</b> Normal frontal plane axis (+64°). No acute ST-segment deviation or pathologic Q waves.<br/>"
            "• <b>Precordial Leads (V1–V6):</b> Normal R-wave progression across anterior leads with transition at V3–V4. No ischemic T-wave inversion.<br/>"
            "• <b>Pre-Catheterization Summary:</b> Tracing reflects baseline physiological cardiac rhythm without acute ischemic contraindication for Left Heart Catheterization.<br/>"
            "• <i>Notice: No genuine ECG waveform is printed here. Findings are simulated demonstration data only.</i>"
        )

    # Render Interpretation Box
    interp_box = Table([[Paragraph(interp_text, body_style)]], colWidths=[523])
    interp_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(interp_box)
    elements.append(Spacer(1, 8))

    # 6. Prominent Safety Disclaimer Box
    elements.append(Paragraph("3. Mandatory System Disclaimer", section_heading))
    disclaimer_box_data = [[
        Paragraph(
            "<b>IMPORTANT REGULATORY & CLINICAL DISCLAIMER:</b><br/>"
            "<b>SAMPLE — NOT FOR CLINICAL USE.</b> "
            "This document is an artificial test report generated exclusively for project evaluation and automated workflow verification in the MediPrep Hospital Readiness System. "
            "All diagnostic values, numerical measurements, and interpretive statements are strictly fictional illustrations. "
            "This document does not represent actual patient health data, an authentic clinical encounter, or genuine medical diagnostic advice. "
            "Never use this file for patient treatment or clinical decision-making.",
            ParagraphStyle('DiscBoxText', parent=body_style, fontSize=7, leading=9.5, textColor=colors.HexColor('#742A2A'))
        )
    ]]
    disc_table = Table(disclaimer_box_data, colWidths=[523])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFF5F5')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#FEB2B2')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(disc_table)
    elements.append(Spacer(1, 8))

    # 7. Laboratory Staff Attestation Sign-off
    elements.append(Paragraph("4. Diagnostic Department Attestation (Demonstration Sign-Off)", section_heading))
    attest_data = [
        [
            Paragraph("<b>Diagnostic Technologist:</b><br/>"
                      "Sarah Jenkins, Senior Lab Tech<br/>"
                      "<font size='6.5' color='#718096'>Clinical Diagnostic Unit • Lic #MED-LAB-8901</font>", body_style),
            Paragraph("<b>Supervising Clinical Specialist:</b><br/>"
                      "Dr. K. R. Nambiar, MD, DNB (Clinical Pathology)<br/>"
                      "<font size='6.5' color='#718096'>Central Diagnostic Services • Reg #KMC-44512</font>", body_style),
            Paragraph("<b>MediPrep System Seal:</b><br/>"
                      "<b>SAMPLE REPORT</b><br/>"
                      "<font size='6.5' color='#718096'>Timestamp: 2026-10-26 10:30</font>", ParagraphStyle('SealText', parent=body_style, alignment=TA_CENTER))
        ]
    ]
    attest_table = Table(attest_data, colWidths=[174, 215, 134])
    attest_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EDF2F7')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(attest_table)

    # Build PDF
    doc.build(elements, canvasmaker=SampleReportCanvas)
    logger.info(f"Generated sample laboratory report: {pdf_path}")
    return pdf_path, filename


def generate_all_7_sample_reports(target_dir=None):
    """
    Generates exactly 7 separate sample laboratory test report PDFs for the 7 active patients.
    Returns list of dicts with file metadata.
    """
    if not target_dir:
        target_dir = SAMPLE_REPORTS_DIR
    os.makedirs(target_dir, exist_ok=True)

    items = LabRepository.get_assigned_investigations(lab_type='hospital', include_inactive=False)
    
    generated_files = []
    for item in items:
        # Strictly exclude aaa bbb
        if item.get('patient_user_id') == 86 or item.get('patient_email') == 'bbbb123@gmail.com':
            continue

        result = generate_single_sample_report_pdf(item, target_dir=target_dir)
        if result:
            pdf_path, filename = result
            generated_files.append({
                'item_id': item['id'],
                'patient_id': item['patient_user_id'],
                'patient_name': f"{item['patient_first_name']} {item['patient_last_name']}",
                'procedure_name': item['procedure_name'],
                'task_name': item['task_name'],
                'filename': filename,
                'path': pdf_path,
                'size': os.path.getsize(pdf_path)
            })

    return generated_files


def get_or_generate_sample_report_pdf(item_id, target_dir=None):
    """
    Retrieves or dynamically generates a sample report PDF for a specific checklist item ID.
    Strictly excludes patient ID 86 (aaa bbb).
    """
    if not target_dir:
        target_dir = SAMPLE_REPORTS_DIR
    os.makedirs(target_dir, exist_ok=True)

    items = LabRepository.get_assigned_investigations(lab_type='hospital', include_inactive=False)
    target_item = next((x for x in items if x['id'] == item_id), None)
    if not target_item:
        return None, None

    # Guard against patient 86
    if target_item.get('patient_user_id') == 86 or target_item.get('patient_email') == 'bbbb123@gmail.com':
        return None, None

    filename = get_sample_report_filename(target_item)
    pdf_path = os.path.join(target_dir, filename)

    if not os.path.exists(pdf_path):
        res = generate_single_sample_report_pdf(target_item, target_dir=target_dir)
        if not res:
            return None, None
        pdf_path, filename = res

    return pdf_path, filename
