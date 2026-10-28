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

# Base directory for storing individual laboratory requirement PDFs
REQUIREMENTS_PDF_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'documentation', 'individual_patient_lab_requirements'
))

class SinglePageNumberedCanvas(canvas.Canvas):
    """Canvas that adds running header and footer with total page count."""
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
        # Top Header line
        self.setStrokeColor(colors.HexColor('#CBD5E0'))
        self.setLineWidth(0.75)
        self.line(36, 806, 559, 806)

        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor('#1A365D'))
        self.drawString(36, 812, "MEDIPREP HEALTHCARE SYSTEM – OFFICIAL LABORATORY REQUISITION")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor('#718096'))
        self.drawRightString(559, 812, "Hospital Readiness & Clinical Preparation System")

        # Bottom Footer line
        self.line(36, 38, 559, 38)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor('#718096'))
        self.drawString(36, 26, "MediPrep Clinical Portal | Confidential Single-Patient Laboratory Requisition")
        self.drawRightString(559, 26, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_expected_filename(item):
    """Derives the expected standardized PDF filename for an investigation item."""
    first_name = (item.get('patient_first_name') or '').strip().replace(' ', '_')
    last_name = (item.get('patient_last_name') or '').strip().replace(' ', '_')
    task_name = item.get('task_name', '')
    proc_id = item.get('procedure_id')

    if proc_id == 10 or 'Renal' in task_name or 'Creatinine' in task_name:
        return f"{first_name}_{last_name}_Renal_Function_Report.pdf"
    elif proc_id == 1 or 'ECG' in task_name:
        return f"{first_name}_{last_name}_ECG_Report.pdf"
    return f"{first_name}_{last_name}_Lab_Report.pdf"


def generate_single_patient_pdf(item, target_dir=None):
    """
    Generates a single, authoritative A4 PDF for an individual patient laboratory requirement.
    Strictly excludes patient ID 86 (aaa bbb) and cancelled procedures.
    """
    # Guard: Completely exclude patient ID 86 (aaa bbb)
    patient_id = item.get('patient_user_id') or item.get('patient_id')
    if patient_id == 86 or item.get('patient_email') == 'bbbb123@gmail.com' or item.get('schedule_status') == 'cancelled':
        logger.warning(f"Skipping PDF generation for excluded/cancelled patient ID {patient_id}")
        return None

    if not target_dir:
        target_dir = REQUIREMENTS_PDF_DIR
    os.makedirs(target_dir, exist_ok=True)

    filename = get_expected_filename(item)
    pdf_path = os.path.join(target_dir, filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1A365D')
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4A5568')
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=7,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
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
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1A202C')
    )

    badge_pending = ParagraphStyle(
        'BadgePending',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#975A16')
    )

    badge_uploaded = ParagraphStyle(
        'BadgeUploaded',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#2B6CB0')
    )

    badge_verified = ParagraphStyle(
        'BadgeVerified',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#22543D')
    )

    badge_unverified = ParagraphStyle(
        'BadgeUnverified',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#718096')
    )

    elements = []

    # 1. Document Banner Header
    ref_code = f"REQ-2026-PT{patient_id}-CK{item.get('id')}"
    sched_dt = item.get('formatted_scheduled_at') or format_datetime_display(item.get('scheduled_at'))
    doc_name = f"Dr. {item.get('doctor_first_name', '')} {item.get('doctor_last_name', '')}".strip() or "Attending Physician"

    header_table_data = [
        [
            Paragraph("<b>CENTRAL CLINICAL LABORATORY</b><br/><font size='7' color='#718096'>HOSPITAL PRE-PROCEDURAL INVESTIGATION REQUISITION</font>", body_style),
            Paragraph(f"<b>DOCUMENT REF:</b> {ref_code}<br/><b>DATE OF ISSUE:</b> {datetime.now().strftime('%d-%m-%Y')}<br/><b>STATUS:</b> <font color='#D69E2E'>Active Order</font>", ParagraphStyle('HRight', parent=body_style, alignment=TA_RIGHT, fontSize=7.5, leading=9.5))
        ]
    ]
    banner_table = Table(header_table_data, colWidths=[310, 213])
    banner_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceBefore=2, spaceAfter=6))

    # 2. Main Title
    pat_full_name = f"{item.get('patient_first_name', '')} {item.get('patient_last_name', '')}".strip()
    elements.append(Paragraph(f"Preoperative Laboratory Requirement: {pat_full_name}", title_style))
    elements.append(Paragraph(f"Official diagnostic requisition mandated for clinical procedure readiness in MediPrep.", subtitle_style))
    elements.append(Spacer(1, 8))

    # 3. Patient Information Card
    elements.append(Paragraph("1. Patient Identification", section_heading))
    patient_info_data = [
        [
            Paragraph("<b>Patient Full Name:</b>", label_style),
            Paragraph(f"<b>{pat_full_name}</b>", value_style),
            Paragraph("<b>Patient User ID:</b>", label_style),
            Paragraph(f"#{patient_id}", value_style)
        ],
        [
            Paragraph("<b>Patient Email:</b>", label_style),
            Paragraph(item.get('patient_email') or "N/A", value_style),
            Paragraph("<b>Account Status:</b>", label_style),
            Paragraph("<font color='#38A169'><b>Active Patient Account</b></font>", value_style)
        ]
    ]
    pat_table = Table(patient_info_data, colWidths=[110, 150, 110, 153])
    pat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(pat_table)
    elements.append(Spacer(1, 8))

    # 4. Scheduled Clinical Procedure Details Card
    elements.append(Paragraph("2. Scheduled Clinical Procedure", section_heading))
    proc_info_data = [
        [
            Paragraph("<b>Scheduled Procedure:</b>", label_style),
            Paragraph(f"<b>{item.get('procedure_name')}</b>", value_style),
            Paragraph("<b>Procedure ID:</b>", label_style),
            Paragraph(f"Procedure #{item.get('procedure_id')}", value_style)
        ],
        [
            Paragraph("<b>CPT / Billing Code:</b>", label_style),
            Paragraph(f"<code>{item.get('procedure_code', 'N/A')}</code>", value_style),
            Paragraph("<b>Booking / Schedule ID:</b>", label_style),
            Paragraph(f"Schedule #{item.get('schedule_id')}", value_style)
        ],
        [
            Paragraph("<b>Scheduled Date & Time:</b>", label_style),
            Paragraph(f"<b>{sched_dt}</b>", value_style),
            Paragraph("<b>Attending Doctor:</b>", label_style),
            Paragraph(f"<b>{doc_name}</b>", value_style)
        ],
        [
            Paragraph("<b>Clinical Location / Room:</b>", label_style),
            Paragraph(item.get('location') or "Hospital Main Facility", value_style),
            Paragraph("<b>Booking Status:</b>", label_style),
            Paragraph("<font color='#2B6CB0'><b>Scheduled / Confirmed</b></font>", value_style)
        ]
    ]
    proc_table = Table(proc_info_data, colWidths=[120, 140, 120, 143])
    proc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(proc_table)
    elements.append(Spacer(1, 8))

    # 5. Required Laboratory Investigation Details Card
    task_name = item.get('task_name', '')
    if item.get('procedure_id') == 10 or 'Renal' in task_name:
        investigation_title = "Renal Function Panel (Serum Creatinine and eGFR)"
        clinical_rationale = (
            "Mandatory glomerular filtration rate assessment prior to intravascular iodinated contrast administration. "
            "Evaluates renal excretion capacity to avoid Contrast-Induced Nephropathy (CIN)."
        )
        specimen_type = "Venous Blood (Serum)"
        dept = "Clinical Biochemistry / Central Hospital Laboratory"
    else:
        investigation_title = "Recent 12-Lead Electrocardiogram (ECG) Report"
        clinical_rationale = (
            "Mandatory electrophysiological rhythm and ischemic baseline evaluation prior to arterial cannulation "
            "and invasive coronary catheterization."
        )
        specimen_type = "Standard 12-Lead Electrocardiographic Tracing"
        dept = "Cardiopulmonary Diagnostics / Central Hospital Laboratory"

    elements.append(Paragraph("3. Mandated Laboratory Investigation & Protocol", section_heading))
    lab_req_data = [
        [
            Paragraph("<b>Required Investigation:</b>", label_style),
            Paragraph(f"<b>{investigation_title}</b>", value_style)
        ],
        [
            Paragraph("<b>Checklist Task Name:</b>", label_style),
            Paragraph(f"<code>{task_name}</code> (Checklist Item ID #{item.get('id')})", value_style)
        ],
        [
            Paragraph("<b>Diagnostic Department:</b>", label_style),
            Paragraph(dept, value_style)
        ],
        [
            Paragraph("<b>Specimen / Tracing:</b>", label_style),
            Paragraph(specimen_type, value_style)
        ],
        [
            Paragraph("<b>Clinical Indication & Protocol:</b>", label_style),
            Paragraph(clinical_rationale, body_style)
        ]
    ]
    lab_req_table = Table(lab_req_data, colWidths=[130, 393])
    lab_req_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(lab_req_table)
    elements.append(Spacer(1, 8))

    # 6. Actual Report Upload & Medical Verification Statuses
    has_uploaded = bool(item.get('latest_report_id'))
    rep_status_str = "Uploaded" if has_uploaded else "Pending Upload"
    verif_status_val = item.get('verification_status')
    if verif_status_val == 'verified':
        verif_status_str = "Verified / Accepted"
        verif_p = Paragraph(f"<b>{verif_status_str}</b>", badge_verified)
    elif verif_status_val in ['needs_review', 'needs_clarification']:
        verif_status_str = "Needs Clarification"
        verif_p = Paragraph(f"<b>{verif_status_str}</b>", badge_pending)
    elif has_uploaded:
        verif_status_str = "Pending Doctor Review"
        verif_p = Paragraph(f"<b>{verif_status_str}</b>", badge_pending)
    else:
        verif_status_str = "Unverified (Awaiting Report Upload)"
        verif_p = Paragraph(f"<b>{verif_status_str}</b>", badge_unverified)

    rep_p = Paragraph(f"<b>{rep_status_str}</b>", badge_uploaded if has_uploaded else badge_pending)

    elements.append(Paragraph("4. Requisition Status & Diagnostic Fulfillment", section_heading))
    status_table_data = [
        [
            Paragraph("<b>Report Upload Status:</b>", label_style),
            rep_p,
            Paragraph("<b>Doctor Verification:</b>", label_style),
            verif_p
        ],
        [
            Paragraph("<b>Fulfillment State:</b>", label_style),
            Paragraph(
                "Report pending electronic upload in Hospital Lab Portal (<code>/lab/dashboard</code>)." if not has_uploaded else "Official report ingested and locked on server.",
                body_style
            ),
            Paragraph("<b>Pre-Op Clearance:</b>", label_style),
            Paragraph(
                "<font color='#D69E2E'><b>Pending Lab Clearance</b></font>" if not has_uploaded else "<font color='#38A169'><b>Report Under Clinical Review</b></font>",
                body_style
            )
        ]
    ]
    status_table = Table(status_table_data, colWidths=[120, 140, 120, 143])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 10))

    # 7. Standard Operating Procedure (SOP) & Authorized Sign-off Box
    elements.append(Paragraph("5. Laboratory Technician Operating Protocol & Stamp", section_heading))
    sop_data = [
        [
            Paragraph(
                "<b>Mandatory Protocol for Hospital Laboratory Personnel:</b><br/>"
                "1. Confirm patient identity against wristband / government ID before specimen collection or diagnostic tracing.<br/>"
                "2. Perform test in accordance with hospital diagnostic quality assurance standards.<br/>"
                "3. Electronically upload signed diagnostic report via MediPrep Hospital Lab Portal.<br/>"
                "4. All uploaded files are tamper-locked and immediately linked to Attending Doctor's readiness checklist.",
                body_style
            ),
            Paragraph(
                "<b>Central Laboratory Seal & Attestation:</b><br/><br/>"
                "______________________________________<br/>"
                "<b>Sarah Jenkins</b>, Senior Laboratory Technician<br/>"
                "Central Hospital Clinical Diagnostic Laboratory<br/>"
                f"<font size='6.5' color='#718096'>MediPrep Health System • {datetime.now().strftime('%d-%m-%Y %H:%M')}</font>",
                ParagraphStyle('SignBox', parent=body_style, alignment=TA_CENTER, fontSize=7.5, leading=10.5)
            )
        ]
    ]
    sop_table = Table(sop_data, colWidths=[310, 213])
    sop_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EDF2F7')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(sop_table)

    # Build PDF
    doc.build(elements, canvasmaker=SinglePageNumberedCanvas)
    logger.info(f"Generated single-patient PDF: {pdf_path}")
    return pdf_path, filename


def generate_all_7_patient_pdfs(target_dir=None):
    """
    Generates exactly the 7 individual laboratory requirement PDFs for eligible active patients.
    Returns a dict mapping patient name to file path and metadata.
    """
    if not target_dir:
        target_dir = REQUIREMENTS_PDF_DIR
    os.makedirs(target_dir, exist_ok=True)

    # Retrieve all active hospital investigations
    items = LabRepository.get_assigned_investigations(lab_type='hospital', include_inactive=False)
    
    generated_files = []
    for item in items:
        # Strictly exclude aaa bbb
        if item.get('patient_user_id') == 86 or item.get('patient_email') == 'bbbb123@gmail.com':
            continue
        result = generate_single_patient_pdf(item, target_dir=target_dir)
        if result:
            pdf_path, filename = result
            generated_files.append({
                'item_id': item['id'],
                'patient_id': item['patient_user_id'],
                'patient_name': f"{item['patient_first_name']} {item['patient_last_name']}",
                'filename': filename,
                'path': pdf_path,
                'size': os.path.getsize(pdf_path)
            })

    return generated_files


def get_or_generate_patient_pdf(item_id, target_dir=None):
    """
    Fetches an existing PDF or generates it on-the-fly for a specific checklist item ID.
    Strictly excludes patient ID 86 (aaa bbb).
    """
    if not target_dir:
        target_dir = REQUIREMENTS_PDF_DIR
    os.makedirs(target_dir, exist_ok=True)

    # Get active investigations
    items = LabRepository.get_assigned_investigations(lab_type='hospital', include_inactive=False)
    target_item = next((x for x in items if x['id'] == item_id), None)
    if not target_item:
        return None, None

    # Guard against patient 86
    if target_item.get('patient_user_id') == 86 or target_item.get('patient_email') == 'bbbb123@gmail.com':
        return None, None

    filename = get_expected_filename(target_item)
    pdf_path = os.path.join(target_dir, filename)

    if not os.path.exists(pdf_path):
        res = generate_single_patient_pdf(target_item, target_dir=target_dir)
        if not res:
            return None, None
        pdf_path, filename = res

    return pdf_path, filename
