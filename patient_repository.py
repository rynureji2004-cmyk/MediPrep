import mysql.connector
from database import DBConnectionContext, DBTransactionContext
import logging

logger = logging.getLogger(__name__)

class PatientRepository:
    """Handles raw SQL operations for patients viewing their compliance checklists and uploading files."""

    @staticmethod
    def get_assigned_procedures(patient_id):
        """Fetches scheduled procedures for a patient, joining doctor, procedure, and readiness details."""
        query = """
            SELECT sp.*, 
                   p.code AS procedure_code, p.name AS procedure_name,
                   u_doc.first_name AS doctor_first_name, u_doc.last_name AS doctor_last_name, u_doc.email AS doctor_email,
                   pr.readiness_status, pr.notes AS readiness_notes
            FROM tbl_scheduled_procedures sp
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            LEFT JOIN tbl_users u_doc ON sp.doctor_id = u_doc.id
            LEFT JOIN tbl_procedure_readiness pr ON sp.id = pr.scheduled_procedure_id
            WHERE sp.patient_id = %s
            ORDER BY sp.scheduled_at ASC
        """

        try:
            with DBConnectionContext() as conn:
              with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, (patient_id,))
                return cursor.fetchall()

        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_assigned_procedures: {err}")
            raise err

    @staticmethod
    def get_checklist_items(scheduled_id):
        """Fetches all checklist items for a scheduled procedure, including uploaded files."""
        from app.repositories.doctor_repository import DoctorRepository
        DoctorRepository.ensure_checklist_initialized(scheduled_id)
        query = """
            SELECT ci.*, 
                   ur.file_name, ur.file_path, ur.id as report_id, ur.file_size_bytes,
                   COALESCE(ur.lab_name, ci.lab_name, 'Hospital Laboratory') as report_lab_name,
                   COALESCE(ur.lab_type, CASE WHEN ci.is_external THEN 'external' ELSE 'hospital' END) as report_lab_type,
                   ur.external_report_id, ur.report_date,
                   ur.verification_status as report_verification_status, ur.verification_notes as report_verification_notes,
                   ur.uploaded_by_user_id, ur.uploaded_at as report_uploaded_at,
                   u_up.first_name as uploader_first_name, u_up.last_name as uploader_last_name,
                   r_up.name as uploader_role_name
            FROM tbl_checklist_items ci
            LEFT JOIN tbl_uploaded_reports ur ON ci.id = ur.checklist_item_id AND ur.is_current = TRUE
            LEFT JOIN tbl_users u_up ON ur.uploaded_by_user_id = u_up.id
            LEFT JOIN tbl_roles r_up ON u_up.role_id = r_up.id
            WHERE ci.scheduled_procedure_id = %s
            ORDER BY ci.due_by_datetime ASC
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (scheduled_id,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_checklist_items: {err}")
            raise err

    @staticmethod
    def save_report_upload_transaction(item_id, file_name, file_path, file_size, user_id):
        """
        Saves file upload metadata and updates checklist item state to 'completed'
        in a database transaction context.
        """
        insert_report_query = """
            INSERT INTO tbl_uploaded_reports (checklist_item_id, file_name, file_path, file_size_bytes)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                file_name = VALUES(file_name), 
                file_path = VALUES(file_path), 
                file_size_bytes = VALUES(file_size_bytes),
                uploaded_at = CURRENT_TIMESTAMP
        """
        
        update_item_query = """
            UPDATE tbl_checklist_items 
            SET status = 'completed', completed_by_user_id = %s, completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        
        try:
            with DBTransactionContext() as cursor:
                # 1. Insert/Update report metadata
                cursor.execute(insert_report_query, (item_id, file_name, file_path, file_size))
                
                # 2. Update checklist status
                cursor.execute(update_item_query, (user_id, item_id))
        except mysql.connector.Error as err:
            logger.error(f"Transaction failed in save_report_upload: {err}")
            raise err

    @staticmethod
    def get_health_suggestions(procedure_id, medical_history_keywords):
        """Fetches suggestions matching procedure type and filtering by patient condition keyword matching."""
        query = "SELECT suggestion_text FROM tbl_health_suggestions WHERE procedure_id = %s"
        params = [procedure_id]
        
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, tuple(params))
                    rows = cursor.fetchall()
                    
                    # If patient has medical history keywords (e.g. 'diabetic'), filter recommendations
                    suggestions = []
                    for row in rows:
                        suggestions.append(row['suggestion_text'])
                    return suggestions
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_health_suggestions: {err}")
            raise err

    @staticmethod
    def get_patient_notifications(patient_id):
        """Fetches notifications list for a patient with doctor and procedure details."""
        query = """
            SELECT n.*, 
                   u_send.first_name AS sender_first_name, u_send.last_name AS sender_last_name,
                   p.name AS procedure_name
            FROM tbl_notifications n
            LEFT JOIN tbl_users u_send ON n.sender_id = u_send.id
            LEFT JOIN tbl_scheduled_procedures sp ON n.scheduled_procedure_id = sp.id
            LEFT JOIN tbl_procedures p ON sp.procedure_id = p.id
            WHERE n.user_id = %s 
            ORDER BY n.sent_at DESC
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (patient_id,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_patient_notifications: {err}")
            raise err

    @staticmethod
    def complete_task_item(item_id, user_id):
        """Marks a standard non-document task as completed by patient."""
        query = """
            UPDATE tbl_checklist_items 
            SET status = 'completed', completed_by_user_id = %s, completed_at = CURRENT_TIMESTAMP
            WHERE id = %s AND task_type = 'patient_action'
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (user_id, item_id))
                    conn.commit()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in complete_task_item: {err}")
            raise err

    @staticmethod
    def get_schedule_id_by_item(item_id):
        """Fetches scheduled procedure ID for a checklist item."""
        query = "SELECT scheduled_procedure_id FROM tbl_checklist_items WHERE id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (item_id,))
                    row = cursor.fetchone()
                    if row:
                        return row[0]
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_schedule_id_by_item: {err}")
            raise err
        return None

    @staticmethod
    def save_patient_vitals(scheduled_id, vitals):
        """Inserts or updates patient pre-op vitals in MySQL."""
        query = """
            INSERT INTO tbl_patient_vitals (scheduled_procedure_id, blood_sugar, hemoglobin, systolic_bp, diastolic_bp, temperature, creatinine)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                blood_sugar = VALUES(blood_sugar),
                hemoglobin = VALUES(hemoglobin),
                systolic_bp = VALUES(systolic_bp),
                diastolic_bp = VALUES(diastolic_bp),
                temperature = VALUES(temperature),
                creatinine = VALUES(creatinine),
                recorded_at = CURRENT_TIMESTAMP
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (
                        scheduled_id,
                        vitals.get('blood_sugar'),
                        vitals.get('hemoglobin'),
                        vitals.get('systolic_bp'),
                        vitals.get('diastolic_bp'),
                        vitals.get('temperature'),
                        vitals.get('creatinine')
                    ))
                    conn.commit()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in save_patient_vitals: {err}")
            raise err

    @staticmethod
    def get_patient_vitals(scheduled_id):
        """Retrieves patient pre-op vitals by scheduled procedure ID."""
        query = "SELECT * FROM tbl_patient_vitals WHERE scheduled_procedure_id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (scheduled_id,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_patient_vitals: {err}")
            raise err

    @staticmethod
    def get_patient_assessment(scheduled_id):
        """Fetches Pre-Procedure Assessment for a scheduled procedure."""
        query = "SELECT * FROM tbl_patient_assessments WHERE scheduled_procedure_id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (scheduled_id,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_patient_assessment: {err}")
            return None

    @staticmethod
    def save_patient_assessment(scheduled_id, allergies, meds, surgeries, anesthesia, history_notes, contact_name, contact_phone, submit_and_lock=False):
        """Saves patient assessment. Locking prevents patient modification after submission."""
        status_val = 'submitted_locked' if submit_and_lock else 'draft'
        query = """
            INSERT INTO tbl_patient_assessments 
            (scheduled_procedure_id, allergies, current_medications, previous_surgeries, anesthesia_problems, medical_history_notes, emergency_contact_name, emergency_contact_phone, status, submitted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, IF(%s = 'submitted_locked', NOW(), NULL))
            ON DUPLICATE KEY UPDATE
                allergies = VALUES(allergies),
                current_medications = VALUES(current_medications),
                previous_surgeries = VALUES(previous_surgeries),
                anesthesia_problems = VALUES(anesthesia_problems),
                medical_history_notes = VALUES(medical_history_notes),
                emergency_contact_name = VALUES(emergency_contact_name),
                emergency_contact_phone = VALUES(emergency_contact_phone),
                status = IF(tbl_patient_assessments.status = 'submitted_locked', 'submitted_locked', VALUES(status)),
                submitted_at = IF(tbl_patient_assessments.status = 'submitted_locked', tbl_patient_assessments.submitted_at, VALUES(submitted_at))
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (scheduled_id, allergies, meds, surgeries, anesthesia, history_notes, contact_name, contact_phone, status_val, status_val))
                    conn.commit()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in save_patient_assessment: {err}")
            raise err

    @staticmethod
    def get_patient_consent(scheduled_id):
        """Fetches active system consent record for a scheduled procedure."""
        query = "SELECT * FROM tbl_patient_consents WHERE scheduled_procedure_id = %s AND is_current = TRUE"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (scheduled_id,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_patient_consent: {err}")
            return None

    @staticmethod
    def create_or_get_system_consent(scheduled_id):
        """Generates system consent record from database data if not present."""
        existing = PatientRepository.get_patient_consent(scheduled_id)
        if existing:
            return existing
        
        query = """
            SELECT sp.*, p.name as procedure_name, u_p.first_name as patient_first_name, u_p.last_name as patient_last_name,
                   u_d.first_name as doctor_first_name, u_d.last_name as doctor_last_name
            FROM tbl_scheduled_procedures sp
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            JOIN tbl_users u_d ON sp.doctor_id = u_d.id
            WHERE sp.id = %s
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (scheduled_id,))
                    info = cursor.fetchone()
            if not info:
                return None
            
            consent_text = (
                f"INFORMED CONSENT FOR MEDICAL PROCEDURE:\n\n"
                f"Patient Name: {info['patient_first_name']} {info['patient_last_name']}\n"
                f"Procedure: {info['procedure_name']}\n"
                f"Attending Surgeon: Dr. {info['doctor_first_name']} {info['doctor_last_name']}\n"
                f"Scheduled Location & Date: {info['location']} on {info['scheduled_at']}\n\n"
                f"ACKNOWLEDGEMENT & CONSENT STATEMENT:\n"
                f"I confirm that I have been fully informed regarding the procedure, risks, benefits, and preoperative preparation requirements. "
                f"I hereby authorize Dr. {info['doctor_first_name']} {info['doctor_last_name']} and the clinical team to perform the scheduled procedure. "
                f"By confirming below using my authenticated electronic account, I electronically sign and lock this consent form."
            )
            
            insert_query = """
                INSERT INTO tbl_patient_consents (scheduled_procedure_id, consent_text, version, is_current, status)
                VALUES (%s, %s, 1, TRUE, 'generated')
            """
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_query, (scheduled_id, consent_text))
                    conn.commit()
                    
            return PatientRepository.get_patient_consent(scheduled_id)
        except mysql.connector.Error as err:
            logger.error(f"DB Error in create_or_get_system_consent: {err}")
            return None

    @staticmethod
    def confirm_patient_consent(consent_id, patient_id):
        """Records patient electronic signature confirmation and locks consent."""
        query = """
            UPDATE tbl_patient_consents 
            SET status = 'confirmed_locked', confirmed_by_patient_id = %s, confirmed_at = NOW() 
            WHERE id = %s AND status = 'generated'
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (patient_id, consent_id))
                    conn.commit()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in confirm_patient_consent: {err}")
            raise err

