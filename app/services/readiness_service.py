from app.repositories.doctor_repository import DoctorRepository
from app.repositories.patient_repository import PatientRepository
from app.services.rules_engine import RulesEngine
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ReadinessService:
    """Procedure Readiness Engine: Computes compliance breakdown and readiness status from actual DB records."""

    @staticmethod
    def evaluate_and_update_readiness(schedule_id):
        """
        Evaluates full procedure readiness considering:
        - Patient Assessment status
        - Required Reports verification status
        - System Consent confirmation and verification
        - Preparation Checklist completion
        - Clinical Safety Rules / Vitals
        - Risk Alerts
        Saves calculated readiness status (green, yellow, orange, red) to MySQL.
        """
        try:
            reasons = []
            blockers = []
            warnings = []

            # 1. Pre-Procedure Assessment Check
            assessment = PatientRepository.get_patient_assessment(schedule_id)
            assessment_complete = False
            if assessment and assessment.get('status') == 'submitted_locked':
                assessment_complete = True
            else:
                blockers.append("Pre-Procedure Assessment not submitted or locked")

            # 2. Checklist Items & Official Reports Check
            items = DoctorRepository.get_active_checklist_items(schedule_id)
            reports_verified = True

            unverified_reports_count = 0
            missing_reports_count = 0
            pending_tasks_count = 0

            for item in items:
                if item['task_type'] == 'document_upload':
                    # Check report verification status
                    from database import DBConnectionContext
                    with DBConnectionContext() as conn:
                        cursor = conn.cursor(dictionary=True)
                        try:
                            cursor.execute("""
                                SELECT * FROM tbl_uploaded_reports 
                                WHERE checklist_item_id = %s
                                ORDER BY id DESC LIMIT 1
                            """, (item['id'],))
                            report = cursor.fetchone()
                        finally:
                            cursor.close()

                    if not report:
                        reports_verified = False
                        missing_reports_count += 1
                        if item['is_critical']:
                            blockers.append(f"Required report missing: {item['task_name']}")
                    elif report['verification_status'] != 'verified':
                        reports_verified = False
                        unverified_reports_count += 1
                        if item['is_critical']:
                            blockers.append(f"Report unverified: {item['task_name']} (Awaiting Doctor Verification)")
                else:
                    if item['status'] not in ['completed', 'verified']:
                        pending_tasks_count += 1
                        if item['is_critical']:
                            blockers.append(f"Critical task pending: {item['task_name']}")

            # 3. System-Generated Consent Check
            consent = PatientRepository.get_patient_consent(schedule_id)
            consent_complete = False
            if consent:
                if consent['status'] in ['confirmed_locked', 'verified']:
                    consent_complete = True
                    if consent['status'] == 'confirmed_locked':
                        warnings.append("System Consent confirmed by patient, pending final doctor verification sign-off")
                else:
                    blockers.append("Informed Consent pending patient confirmation")
            else:
                # Generate system consent if missing
                PatientRepository.create_or_get_system_consent(schedule_id)
                blockers.append("Informed Consent pending patient confirmation")

            # 4. Clinical Safety Rules Engine Check (Vitals)
            vitals = PatientRepository.get_patient_vitals(schedule_id)
            vitals_alerts = RulesEngine.evaluate_vitals(vitals) if vitals else []
            if vitals_alerts:
                for alert in vitals_alerts:
                    warnings.append(alert)

            # 5. Risk Alerts Check
            schedule_info = DoctorRepository.get_schedule_by_id(schedule_id)
            doctor_id = schedule_info['doctor_id'] if schedule_info else None
            active_alerts = []
            if doctor_id:
                from app.services.alerts_service import AlertsService
                try:
                    all_alerts = AlertsService.get_active_risk_alerts(doctor_id)
                    active_alerts = [a for a in all_alerts if a['schedule_id'] == schedule_id]
                    for a in active_alerts:
                        msg = a.get('alert_message') or a.get('message', '')
                        if a.get('severity') == 'high':
                            blockers.append(f"High Severity Alert: {msg}")
                        else:
                            warnings.append(f"Alert: {msg}")
                except Exception as e:
                    logger.error(f"Error fetching risk alerts: {e}")

            # Calculate progress percentage and checklist completion from actual items
            total_items = len(items)
            completed_items = sum(1 for i in items if i['status'] in ['completed', 'verified'])
            progress_pct = int((completed_items / total_items) * 100) if total_items > 0 else 0
            checklist_complete = (completed_items == total_items) if total_items > 0 else False

            # Determine Overall Readiness Status
            if blockers:
                status = 'red'
                notes = "🔴 NOT READY: " + "; ".join(blockers)
            elif warnings:
                status = 'yellow'
                notes = "🟡 PENDING / CLINICAL REVIEW REQUIRED: " + "; ".join(warnings)
            else:
                status = 'green'
                notes = "🟢 READY FOR PROCEDURE: All pre-operative assessments, verified reports, consent, and safety checks complete."

            # Save status to database
            DoctorRepository.update_procedure_readiness(schedule_id, status, notes)

            return {
                'readiness_status': status,
                'progress': progress_pct,
                'notes': notes,
                'assessment_complete': assessment_complete,
                'reports_verified': reports_verified,
                'consent_complete': consent_complete,
                'checklist_complete': checklist_complete,
                'vitals_alerts': vitals_alerts,
                'blockers': blockers,
                'warnings': warnings
            }
        except Exception as e:
            logger.error(f"Error in evaluate_and_update_readiness: {e}")
            raise e
