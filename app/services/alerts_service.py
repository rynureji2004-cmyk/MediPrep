from datetime import datetime, timedelta
from app.repositories.doctor_repository import DoctorRepository
import logging

logger = logging.getLogger(__name__)

class AlertsService:
    """Clinical Risk Alert Engine (No AI). Evaluates procedure checklists for pre-op safety violations."""

    @staticmethod
    def get_active_risk_alerts(doctor_id):
        """
        Scans all scheduled procedures for a doctor, runs rule evaluations on checklists,
        and compiles active pre-operative safety risk alerts.
        """
        alerts = []
        try:
            # 0. Fetch unresolved risk alerts from database (tbl_risk_alerts)
            try:
                db_alerts = DoctorRepository.get_unresolved_risk_alerts(doctor_id)
                for row in db_alerts:
                    if isinstance(row, dict):
                        alerts.append({
                            'schedule_id': row.get('scheduled_procedure_id'),
                            'patient_name': f"{row.get('patient_first_name', '')} {row.get('patient_last_name', '')}".strip(),
                            'procedure': f"{row.get('procedure_code', '')} ({row.get('procedure_name', '')})",
                            'type': row.get('alert_type', 'Risk Alert'),
                            'severity': row.get('severity', 'medium'),
                            'message': row.get('alert_message', '')
                        })
            except Exception as e:
                logger.error(f"Error fetching DB risk alerts: {e}")

            # 1. Fetch upcoming schedules for the doctor
            schedules = DoctorRepository.get_schedules_by_doctor(doctor_id)
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            
            for s in schedules:
                schedule_id = s['id']
                scheduled_at = s['scheduled_at']
                
                # Convert scheduled_at to datetime if it is a string
                if isinstance(scheduled_at, str):
                    try:
                        scheduled_at_dt = datetime.strptime(scheduled_at, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        scheduled_at_dt = datetime.strptime(scheduled_at.replace('T', ' '), "%Y-%m-%d %H:%M:%S")
                else:
                    scheduled_at_dt = scheduled_at
                
                # Fetch active checklist items
                items = DoctorRepository.get_active_checklist_items(schedule_id)
                
                # Track checklist components
                has_blood_test = False
                blood_test_done = False
                
                has_ecg = False
                ecg_done = False
                
                has_consent = False
                consent_done = False
                
                has_medication = False
                medication_done = False
                
                has_incomplete_tasks = False
                
                for item in items:
                    task_name_lower = item['task_name'].lower()
                    status = item['status']
                    
                    if status != 'verified':
                        has_incomplete_tasks = True
                        
                    # Check Blood Test
                    if 'blood test' in task_name_lower or 'cbc' in task_name_lower or 'hematology' in task_name_lower or 'blood' in task_name_lower:
                        has_blood_test = True
                        if status in ['completed', 'verified']:
                            blood_test_done = True
                            
                    # Check ECG
                    if 'ecg' in task_name_lower or 'electrocardiogram' in task_name_lower:
                        has_ecg = True
                        if status in ['completed', 'verified']:
                            ecg_done = True
                            
                    # Check Consent Form
                    if 'consent' in task_name_lower:
                        has_consent = True
                        if status == 'verified':
                            consent_done = True
                            
                    # Check Medication
                    if 'medication' in task_name_lower or 'drug' in task_name_lower or 'aspirin' in task_name_lower or 'thinners' in task_name_lower or 'fasting' in task_name_lower:
                        has_medication = True
                        if status in ['completed', 'verified']:
                            medication_done = True

                patient_name = f"{s['patient_first_name']} {s['patient_last_name']}"
                procedure_info = f"{s['procedure_code']} ({s['procedure_name']})"
                
                # Rule 1: Procedure Tomorrow
                is_tomorrow = now.date() < scheduled_at_dt.date() <= tomorrow.date()
                if is_tomorrow:
                    alerts.append({
                        'schedule_id': schedule_id,
                        'patient_name': patient_name,
                        'procedure': procedure_info,
                        'type': 'Procedure Tomorrow',
                        'severity': 'high',
                        'message': f"Surgery scheduled for tomorrow ({scheduled_at_dt.strftime('%H:%M')}). Final checks required."
                    })
                    
                # Rule 2: Blood Test Missing
                if has_blood_test and not blood_test_done:
                    alerts.append({
                        'schedule_id': schedule_id,
                        'patient_name': patient_name,
                        'procedure': procedure_info,
                        'type': 'Blood Test Missing',
                        'severity': 'high' if is_tomorrow else 'medium',
                        'message': "Required pre-op blood test report is missing or unverified."
                    })
                    
                # Rule 3: ECG Missing
                if has_ecg and not ecg_done:
                    alerts.append({
                        'schedule_id': schedule_id,
                        'patient_name': patient_name,
                        'procedure': procedure_info,
                        'type': 'ECG Missing',
                        'severity': 'high' if is_tomorrow else 'medium',
                        'message': "Required pre-op ECG tracing is missing or unverified."
                    })
                    
                # Rule 4: Consent Form Missing
                if has_consent and not consent_done:
                    alerts.append({
                        'schedule_id': schedule_id,
                        'patient_name': patient_name,
                        'procedure': procedure_info,
                        'type': 'Consent Form Missing',
                        'severity': 'high',
                        'message': "Preoperative consent documentation has not been signed off by staff."
                    })
                    
                # Rule 5: Medication Not Followed
                if has_medication and not medication_done:
                    alerts.append({
                        'schedule_id': schedule_id,
                        'patient_name': patient_name,
                        'procedure': procedure_info,
                        'type': 'Medication Not Followed',
                        'severity': 'high' if is_tomorrow else 'medium',
                        'message': "Pre-op medication directives (suspensions or dosages) have not been checked."
                    })
                    
                # Rule 6: Checklist Incomplete
                if has_incomplete_tasks:
                    alerts.append({
                        'schedule_id': schedule_id,
                        'patient_name': patient_name,
                        'procedure': procedure_info,
                        'type': 'Checklist Incomplete',
                        'severity': 'medium',
                        'message': "One or more preoperative preparation tasks are still outstanding."
                    })

            return alerts
        except Exception as e:
            logger.error(f"Error scanning risk alerts: {e}")
            raise e
