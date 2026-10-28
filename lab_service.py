import os
import hashlib
from werkzeug.utils import secure_filename
from app.repositories.lab_repository import LabRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.patient_repository import PatientRepository
from app.utilities.validators import allowed_file
import logging

logger = logging.getLogger(__name__)

class LabService:
    """Business operations for Hospital and External Laboratory report uploads and verification."""

    @staticmethod
    def upload_official_lab_report(item_id, file, upload_folder, user_id, role_name, lab_name=None, external_report_id=None, report_date=None, notes=None, task_name=None):
        """
        Validates, calculates SHA-256 file hash, saves file securely, 
        creates new independent report metadata record, and triggers readiness evaluation.
        """
        if task_name and task_name.strip():
            from database import DBConnectionContext
            try:
                with DBConnectionContext() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("UPDATE tbl_checklist_items SET task_name = %s WHERE id = %s", (task_name.strip(), item_id))
                        conn.commit()
            except Exception as e:
                logger.error(f"Failed to update task_name: {e}")

        # Fetch investigation to get patient_id for duplicate check
        investigation = LabRepository.get_investigation_by_id(item_id)
        if not investigation:
            raise ValueError("Investigation task not found.")

        patient_id = investigation.get('patient_id')

        # Check Duplicate Report Reference Number for this patient
        if external_report_id and external_report_id.strip():
            if LabRepository.check_duplicate_report_reference(patient_id, external_report_id.strip()):
                raise ValueError("This report reference number already exists for this patient and investigation.")

        # 1. Fetch lab profile for user or default
        lab_profile = LabRepository.get_lab_profile_by_user_id(user_id)
        if lab_name and lab_name.strip():
            final_lab_name = lab_name.strip()
        elif lab_profile:
            final_lab_name = lab_profile['lab_name']
        else:
            final_lab_name = 'Central Hospital Clinical Laboratory'
        lab_type = 'hospital'

        # If file is not provided, check if updating existing metadata
        if not file or file.filename == '':
            history = LabRepository.get_report_history(item_id)
            if history:
                sched_id = LabRepository.update_lab_report_metadata(
                    item_id=item_id,
                    user_id=user_id,
                    lab_name=final_lab_name,
                    external_report_id=external_report_id.strip() if external_report_id else None,
                    report_date=report_date if report_date else None,
                    notes=notes.strip() if notes else None,
                    task_name=task_name.strip() if task_name else None
                )
                if sched_id:
                    from app.services.readiness_service import ReadinessService
                    ReadinessService.evaluate_and_update_readiness(sched_id)
                return history[0]['id']
            else:
                raise ValueError("No report file selected.")

        if not allowed_file(file.filename):
            raise ValueError("File type not allowed. Upload PDF or image (PNG, JPG, JPEG).")

        # 2. Secure file saving and hash computation
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        
        file_bytes = file.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        file.seek(0)

        unique_name = f"official_report_item_{item_id}_{file_hash[:12]}.{ext}"
        file_path = os.path.join(upload_folder, unique_name)

        try:
            os.makedirs(upload_folder, exist_ok=True)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"Failed to save lab report file: {e}")
            raise RuntimeError("Error writing report file to storage.")

        verification_status = 'pending_verification'

        # 3. Save database transaction record as a new independent report record
        try:
            report_id = LabRepository.save_lab_report_transaction(
                item_id=item_id,
                user_id=user_id,
                lab_name=final_lab_name,
                lab_type=lab_type,
                file_name=filename,
                file_path=unique_name,
                file_size=file_size,
                file_hash=file_hash,
                external_report_id=external_report_id.strip() if external_report_id else None,
                report_date=report_date if report_date else None,
                verification_status=verification_status,
                notes=notes.strip() if notes else None
            )

            sched_id = investigation['schedule_id'] if investigation else None

            AuditRepository.log_audit_action(
                user_id=user_id,
                role_name=role_name,
                action="OFFICIAL_REPORT_UPLOADED",
                details=f"Uploaded official report '{filename}' from '{final_lab_name}' for item {item_id}. Hash: {file_hash[:16]}",
                patient_id=investigation['patient_id'] if investigation else None,
                scheduled_procedure_id=sched_id
            )

            if sched_id:
                from app.services.readiness_service import ReadinessService
                ReadinessService.evaluate_and_update_readiness(sched_id)

            return report_id
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"DB Error saving lab report: {e}")
            raise e

    @staticmethod
    def upload_external_lab_report(item_id, file, upload_folder, doctor_id, lab_name, external_report_id=None, report_date=None, verification_status='external_received', notes=None):
        """
        Doctor uploads an external laboratory report provided by a patient.
        Validates file, computes SHA-256 hash, records metadata with lab_type='external',
        stores external_report_id & report_date, logs audit trail, and updates readiness.
        """
        if not file or file.filename == '':
            raise ValueError("No report file selected.")

        if not allowed_file(file.filename):
            raise ValueError("File type not allowed. Upload PDF or image (PNG, JPG, JPEG).")

        if not lab_name or not lab_name.strip():
            raise ValueError("Laboratory Name is required for external reports.")

        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()

        file_bytes = file.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        file.seek(0)

        unique_name = f"external_report_item_{item_id}_{file_hash[:12]}.{ext}"
        file_path = os.path.join(upload_folder, unique_name)

        try:
            os.makedirs(upload_folder, exist_ok=True)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"Failed to save external lab report file: {e}")
            raise RuntimeError("Error writing report file to storage.")

        try:
            report_id = LabRepository.save_lab_report_transaction(
                item_id=item_id,
                user_id=doctor_id,
                lab_name=lab_name.strip(),
                lab_type='external',
                file_name=filename,
                file_path=unique_name,
                file_size=file_size,
                file_hash=file_hash,
                external_report_id=external_report_id.strip() if external_report_id else None,
                report_date=report_date if report_date else None,
                verification_status=verification_status,
                notes=notes
            )

            investigation = LabRepository.get_investigation_by_id(item_id)
            sched_id = investigation['schedule_id'] if investigation else None

            AuditRepository.log_audit_action(
                user_id=doctor_id,
                role_name='doctor',
                action="EXTERNAL_REPORT_UPLOADED_BY_DOCTOR",
                details=f"Doctor uploaded external report '{filename}' from '{lab_name}' (ID: {external_report_id or 'N/A'}) for item {item_id}.",
                patient_id=investigation['patient_id'] if investigation else None,
                scheduled_procedure_id=sched_id
            )

            if sched_id:
                from app.services.readiness_service import ReadinessService
                ReadinessService.evaluate_and_update_readiness(sched_id)

            return report_id
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"DB Error saving external lab report: {e}")
            raise e

