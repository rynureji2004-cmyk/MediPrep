import os
import uuid
from werkzeug.utils import secure_filename
from app.repositories.patient_repository import PatientRepository
from app.repositories.doctor_repository import DoctorRepository
from app.services.readiness_service import ReadinessService
from app.utilities.validators import allowed_file
import logging

logger = logging.getLogger(__name__)

from app.utilities.validators import format_datetime_display, validate_and_parse_datetime

class PatientService:
    """Manages business operations for patient checklists, task updates, assessments, and consent."""

    @staticmethod
    def get_dashboard_summary(patient_id, selected_schedule_id=None):
        """Compiles patient dashboard statistics, instructions, schedules, assessments, consent, and readiness."""
        schedules = PatientRepository.get_assigned_procedures(patient_id)
        
        # Format dates, times, and evaluate readiness for ALL patient procedures
        for s in schedules:
            scheduled_dt = s.get('scheduled_at')
            if scheduled_dt:
                s['formatted_scheduled_at'] = format_datetime_display(scheduled_dt)
                if hasattr(scheduled_dt, 'strftime'):
                    s['formatted_date'] = scheduled_dt.strftime('%d-%m-%Y')
                    s['formatted_time'] = scheduled_dt.strftime('%H:%M')
                else:
                    try:
                        dt = validate_and_parse_datetime(scheduled_dt)
                        s['formatted_date'] = dt.strftime('%d-%m-%Y')
                        s['formatted_time'] = dt.strftime('%H:%M')
                    except Exception:
                        s['formatted_date'] = str(scheduled_dt)
                        s['formatted_time'] = ''
            else:
                s['formatted_scheduled_at'] = 'Not Available'
                s['formatted_date'] = 'Not Available'
                s['formatted_time'] = ''
                
            try:
                rd = ReadinessService.evaluate_and_update_readiness(s['id'])
                s['readiness_status'] = rd.get('readiness_status', s.get('readiness_status', 'red'))
            except Exception as e:
                logger.error(f"Readiness evaluation error for schedule {s['id']}: {e}")

        assigned_procedure = None
        if selected_schedule_id:
            assigned_procedure = next((s for s in schedules if s['id'] == selected_schedule_id), None)
            
        if not assigned_procedure and schedules:
            assigned_procedure = schedules[0]

        checklist = []
        progress = 0
        suggestions = []
        vitals = {}
        vitals_alerts = []
        reminders = []
        assessment = None
        consent = None
        readiness_details = None
        
        if assigned_procedure:
            sched_id = assigned_procedure['id']
            checklist = PatientRepository.get_checklist_items(sched_id)
            
            # Retrieve assessment and system consent
            assessment = PatientRepository.get_patient_assessment(sched_id)
            consent = PatientRepository.create_or_get_system_consent(sched_id)
            
            # Compute readiness breakdown
            readiness_details = ReadinessService.evaluate_and_update_readiness(sched_id)
            progress = readiness_details.get('progress', 0)

            vitals = PatientRepository.get_patient_vitals(sched_id)
            if vitals:
                from app.services.rules_engine import RulesEngine
                vitals_alerts = RulesEngine.evaluate_vitals(vitals)
                
            suggestions = PatientRepository.get_health_suggestions(assigned_procedure['procedure_id'], '')
            
            from app.services.reminders_service import RemindersService
            reminders = RemindersService.get_active_reminders(checklist, assigned_procedure['scheduled_at'])

        notifications = PatientRepository.get_patient_notifications(patient_id)
        
        return {
            'procedures': schedules,
            'procedure': assigned_procedure,
            'checklist': checklist,
            'progress': progress,
            'suggestions': suggestions,
            'notifications': notifications[:5],
            'vitals': vitals,
            'vitals_alerts': vitals_alerts,
            'reminders': reminders,
            'assessment': assessment,
            'consent': consent,
            'readiness_details': readiness_details
        }

    @staticmethod
    def upload_report_document(item_id, file, upload_folder, user_id):
        """
        Official laboratory reports MUST be uploaded by authorized laboratory personnel.
        Patient upload access is restricted per Security & Authenticity Policy.
        """
        raise PermissionError("Security Policy Violation: Patients are not permitted to upload official laboratory reports. Reports must be uploaded directly by an authorized Hospital or External Laboratory Technician.")

    @staticmethod
    def complete_patient_task(item_id, user_id):
        """Marks patient action checklist items as completed."""
        PatientRepository.complete_task_item(item_id, user_id)
        sched_id = PatientRepository.get_schedule_id_by_item(item_id)
        if sched_id:
            ReadinessService.evaluate_and_update_readiness(sched_id)

    @staticmethod
    def record_vitals(scheduled_id, vitals_dict):
        """Saves patient preoperative lab values to database."""
        vitals = {}
        try:
            for key in ['blood_sugar', 'hemoglobin', 'temperature', 'creatinine']:
                val = vitals_dict.get(key, '').strip()
                vitals[key] = float(val) if val else None
                
            for key in ['systolic_bp', 'diastolic_bp']:
                val = vitals_dict.get(key, '').strip()
                vitals[key] = int(val) if val else None
        except ValueError:
            raise ValueError("Vitals and lab values must be valid numeric numbers.")
            
        PatientRepository.save_patient_vitals(scheduled_id, vitals)
        ReadinessService.evaluate_and_update_readiness(scheduled_id)
