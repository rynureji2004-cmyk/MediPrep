import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.repositories.doctor_repository import DoctorRepository
from app.services.alerts_service import AlertsService
import logging

logger = logging.getLogger(__name__)

class ReportsService:
    """Clinical Preoperative Report Generator (No AI). Generates formatted PDFs using ReportLab."""

    @staticmethod
    def get_report_data(doctor_id, report_type):
        """Fetches data rows depending on the requested report category."""
        schedules = DoctorRepository.get_schedules_by_doctor(doctor_id)
        
        # Dynamically evaluate/update readiness status for active scheduled procedures
        from app.services.readiness_service import ReadinessService
        for s in schedules:
            if s.get('status') in ['scheduled', 'delayed']:
                try:
                    res = ReadinessService.evaluate_and_update_readiness(s['id'])
                    s['readiness_status'] = res['readiness_status']
                except Exception as e:
                    logger.error(f"Readiness evaluation error for schedule {s['id']}: {e}")
        
        from app.utilities.validators import format_datetime_display

        if report_type == 'ready_patients':
            title = "Clinical Preoperative Report: Ready Patients"
            headers = ["Patient Name", "Procedure", "Date/Time", "Location", "Readiness Status"]
            rows = []
            for s in schedules:
                if s.get('status') in ['scheduled', 'delayed'] and s.get('readiness_status') == 'green':
                    rows.append([
                        f"{s['patient_first_name']} {s['patient_last_name']}",
                        f"{s['procedure_code']} - {s['procedure_name']}",
                        format_datetime_display(s['scheduled_at']),
                        s['location'],
                        "Ready (Green)"
                    ])
                    
        elif report_type == 'pending_patients':
            title = "Clinical Preoperative Report: Pending Patients"
            headers = ["Patient Name", "Procedure", "Date/Time", "Location", "Readiness Status"]
            rows = []
            for s in schedules:
                if s.get('status') in ['scheduled', 'delayed'] and s.get('readiness_status') != 'green':
                    status = s.get('readiness_status', 'red').upper()
                    rows.append([
                        f"{s['patient_first_name']} {s['patient_last_name']}",
                        f"{s['procedure_code']} - {s['procedure_name']}",
                        format_datetime_display(s['scheduled_at']),
                        s['location'],
                        f"Pending ({status})"
                    ])
                    
        elif report_type == 'completed_procedures':
            title = "Clinical Report: Completed Procedures"
            headers = ["Patient Name", "Procedure Code / Name", "Completed Date", "Location"]
            rows = []
            # Fetch completed procedures
            for s in schedules:
                if s.get('status') == 'completed':
                    rows.append([
                        f"{s['patient_first_name']} {s['patient_last_name']}",
                        f"{s['procedure_code']} - {s['procedure_name']}",
                        format_datetime_display(s['scheduled_at']),
                        s['location']
                    ])
                    
        elif report_type == 'upcoming_procedures':
            title = "Clinical Report: Upcoming Procedure Schedules"
            headers = ["Patient Name", "Procedure", "Scheduled Date", "Location", "Status"]
            rows = []
            for s in schedules:
                if s.get('status') in ['scheduled', 'delayed']:
                    rows.append([
                        f"{s['patient_first_name']} {s['patient_last_name']}",
                        f"{s['procedure_code']} - {s['procedure_name']}",
                        format_datetime_display(s['scheduled_at']),
                        s['location'],
                        s['status'].upper()
                    ])
                    
        elif report_type == 'risk_alerts':
            title = "Clinical Safety Report: Preoperative Risk Alerts"
            headers = ["Patient Name", "Procedure Code / Name", "Alert Type", "Risk Message", "Severity"]
            alerts = AlertsService.get_active_risk_alerts(doctor_id)
            rows = []
            for a in alerts:
                rows.append([
                    a['patient_name'],
                    a['procedure'],
                    a['type'],
                    a['message'],
                    a['severity'].upper()
                ])
        else:
            raise ValueError(f"Invalid report category type: {report_type}")

        return {
            'title': title,
            'headers': headers,
            'rows': rows
        }

    @staticmethod
    def generate_pdf_stream(doctor_id, report_type, doctor_name):
        """
        Retrieves report metadata, compiles formatted PDF tables,
        and returns a binary BytesIO stream for browser download.
        """
        try:
            # 1. Fetch metadata
            data = ReportsService.get_report_data(doctor_id, report_type)
            
            # 2. Setup document
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=letter,
                rightMargin=36, 
                leftMargin=36, 
                topMargin=54, 
                bottomMargin=54
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # 3. Custom Styles matching corporate dark slate branding
            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#0f172a'),
                spaceAfter=12
            )
            
            meta_style = ParagraphStyle(
                'ReportMeta',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#64748b'),
                spaceAfter=24
            )
            
            header_cell_style = ParagraphStyle(
                'HeaderCell',
                parent=styles['Normal'],
                fontSize=9.5,
                fontName='Helvetica-Bold',
                textColor=colors.white
            )
            
            body_cell_style = ParagraphStyle(
                'BodyCell',
                parent=styles['Normal'],
                fontSize=8.5,
                textColor=colors.HexColor('#334155')
            )
            
            # 4. Header block
            story.append(Paragraph(data['title'], title_style))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            story.append(Paragraph(
                f"Generated by: Dr. {doctor_name} | Date: {timestamp} | System: MediPrep Expert Engine",
                meta_style
            ))
            
            # 5. Build data table
            table_data = []
            
            # Add header row (wrapped in Paragraph to prevent text overflow)
            table_data.append([Paragraph(h, header_cell_style) for h in data['headers']])
            
            # Add body rows
            if not data['rows']:
                # empty state
                colspan = len(data['headers'])
                empty_cell = Paragraph("No medical records match this query.", body_cell_style)
                empty_row = [empty_cell] + ["" for _ in range(colspan - 1)]
                table_data.append(empty_row)
            else:
                for row in data['rows']:
                    table_data.append([Paragraph(str(val), body_cell_style) for val in row])
            
            # Define column widths (scale to fit Letter page width = 612 - 72 margins = 540)
            col_count = len(data['headers'])
            col_width = 540 / col_count
            
            t = Table(table_data, colWidths=[col_width] * col_count)
            
            # 6. Apply professional table styling
            t_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ])
            
            # Add alternating rows background
            if data['rows']:
                for idx in range(1, len(table_data)):
                    if idx % 2 == 0:
                        t_style.add('BACKGROUND', (0, idx), (-1, idx), colors.HexColor('#f8fafc'))
                        
            # Apply spans if empty
            if not data['rows']:
                t_style.add('SPAN', (0, 1), (-1, 1))
                
            t.setStyle(t_style)
            story.append(t)
            
            # 7. Signature Sign-off
            story.append(Spacer(1, 40))
            sig_table = Table([
                [Paragraph("<b>Physician Signature:</b> ___________________________", body_cell_style),
                 Paragraph("<b>Date:</b> ___________________________", body_cell_style)]
            ], colWidths=[270, 270])
            story.append(sig_table)
            
            # 8. Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Failed to generate clinical PDF report: {e}")
            raise e
