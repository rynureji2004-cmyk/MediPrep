import mysql.connector
from database import DBConnectionContext, DBTransactionContext
import logging

logger = logging.getLogger(__name__)

class LabRepository:
    """Handles SQL operations for Hospital and External Laboratory report uploads, locking, and verification."""

    @staticmethod
    def get_lab_profile_by_user_id(user_id):
        """Fetches lab profile details for a given user ID."""
        query = "SELECT * FROM tbl_lab_profiles WHERE user_id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (user_id,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_lab_profile_by_user_id: {err}")
            raise err

    @staticmethod
    def get_registered_external_labs():
        """Fetches distinct registered external laboratory profiles."""
        query = "SELECT * FROM tbl_lab_profiles WHERE lab_type = 'external' ORDER BY lab_name ASC"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_registered_external_labs: {err}")
            raise err

    @staticmethod
    def get_assigned_investigations(lab_type=None, lab_name=None, search_query=None, include_inactive=False):
        """
        Fetches all document upload investigation requests assigned to labs.
        Filters by active procedure requirements (Procedure 1: Left Heart Cath -> ECG, Procedure 10: CT Scan -> Renal Function).
        Excludes cancelled bookings and inactive patient accounts by default.
        """
        query = """
            SELECT ci.*, 
                   sp.id as schedule_id, sp.scheduled_at, sp.location, sp.status as schedule_status,
                   u_p.id as patient_user_id, u_p.first_name as patient_first_name, u_p.last_name as patient_last_name, u_p.email as patient_email,
                   u_d.first_name as doctor_first_name, u_d.last_name as doctor_last_name,
                   p.id as procedure_id, p.name as procedure_name, p.code as procedure_code,
                   ur.id as latest_report_id, ur.file_name as report_file_name, ur.file_path as report_file_path, 
                   ur.verification_status, ur.verification_notes, ur.is_locked, ur.uploaded_at as report_uploaded_at,
                   ur.version as report_version, u_up.first_name as uploader_first_name, u_up.last_name as uploader_last_name
            FROM tbl_checklist_items ci
            JOIN tbl_scheduled_procedures sp ON ci.scheduled_procedure_id = sp.id
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            JOIN tbl_users u_d ON sp.doctor_id = u_d.id
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            LEFT JOIN tbl_uploaded_reports ur ON ci.id = ur.checklist_item_id AND ur.is_current = TRUE
            LEFT JOIN tbl_users u_up ON ur.uploaded_by_user_id = u_up.id
            WHERE ci.task_type = 'document_upload'
              AND (
                  (sp.procedure_id = 1 AND ci.task_name = 'Upload Recent ECG Lab Report')
                  OR
                  (sp.procedure_id = 10 AND ci.task_name = 'Upload Renal Function (Creatinine) Lab Report')
              )
        """
        params = []

        if not include_inactive:
            query += " AND sp.status IN ('scheduled', 'delayed') AND u_p.is_active = TRUE"

        if lab_type == 'external':
            query += " AND (ci.is_external = TRUE OR ci.lab_name IS NOT NULL)"
            if lab_name:
                query += " AND (ci.lab_name = %s OR ci.lab_name IS NULL OR ci.lab_name = '')"
                params.append(lab_name)
        elif lab_type == 'hospital':
            query += " AND (ci.is_external = FALSE OR ci.is_external IS NULL)"

        if search_query:
            query += " AND (CONCAT(u_p.first_name, ' ', u_p.last_name) LIKE %s OR u_p.email LIKE %s OR p.name LIKE %s OR ci.task_name LIKE %s)"
            pattern = f"%{search_query}%"
            params.extend([pattern, pattern, pattern, pattern])

        query += " GROUP BY ci.id ORDER BY sp.scheduled_at DESC, ci.id DESC"

        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, tuple(params))
                    rows = cursor.fetchall()
                    from app.utilities.validators import format_datetime_display
                    for row in rows:
                        row['formatted_scheduled_at'] = format_datetime_display(row.get('scheduled_at'))
                        if row.get('latest_report_id'):
                            row['report_status'] = 'Uploaded'
                            if row.get('verification_status') == 'verified':
                                row['display_verification_status'] = 'Verified'
                            elif row.get('verification_status') in ['needs_review', 'needs_clarification']:
                                row['display_verification_status'] = 'Needs Clarification'
                            else:
                                row['display_verification_status'] = 'Pending Review'
                        else:
                            row['report_status'] = 'Pending Upload'
                            row['display_verification_status'] = 'Unverified'
                    return rows
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_assigned_investigations: {err}")
            raise err

    @staticmethod
    def get_investigation_by_id(item_id):
        """Fetches investigation item details by ID."""
        query = """
            SELECT ci.*, 
                   sp.id as schedule_id, sp.patient_id, sp.doctor_id, sp.scheduled_at, sp.location,
                   u_p.first_name as patient_first_name, u_p.last_name as patient_last_name,
                   p.name as procedure_name
            FROM tbl_checklist_items ci
            JOIN tbl_scheduled_procedures sp ON ci.scheduled_procedure_id = sp.id
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            WHERE ci.id = %s
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (item_id,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_investigation_by_id: {err}")
            raise err

    @staticmethod
    def check_duplicate_report_reference(patient_id, external_report_id):
        """Checks if a report reference number already exists for a specific patient."""
        if not external_report_id or not str(external_report_id).strip():
            return False
        query = """
            SELECT ur.id 
            FROM tbl_uploaded_reports ur
            JOIN tbl_checklist_items ci ON ur.checklist_item_id = ci.id
            JOIN tbl_scheduled_procedures sp ON ci.scheduled_procedure_id = sp.id
            WHERE sp.patient_id = %s AND TRIM(ur.external_report_id) = %s
            LIMIT 1
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (patient_id, str(external_report_id).strip()))
                    return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            logger.error(f"DB Error in check_duplicate_report_reference: {err}")
            return False

    @staticmethod
    def save_lab_report_transaction(item_id, user_id, lab_name, lab_type, file_name, file_path, file_size, file_hash=None, external_report_id=None, report_date=None, verification_status='pending_verification', notes=None):
        """
        Saves a new independent laboratory report record.
        Does NOT mark previous reports as superseded or locked.
        """
        try:
            with DBTransactionContext() as cursor:
                insert_query = """
                    INSERT INTO tbl_uploaded_reports (
                        checklist_item_id, uploaded_by_user_id, lab_name, lab_type, external_report_id, report_date,
                        file_name, file_path, file_size_bytes, verification_status, verification_notes,
                        is_locked, version, is_current, file_hash
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE, 1, TRUE, %s)
                """
                cursor.execute(insert_query, (
                    item_id, user_id, lab_name, lab_type, external_report_id, report_date,
                    file_name, file_path, file_size, verification_status, notes, file_hash
                ))
                new_report_id = cursor.lastrowid

                item_status = 'verified' if verification_status == 'verified' else 'completed'
                cursor.execute("""
                    UPDATE tbl_checklist_items 
                    SET status = %s, completed_by_user_id = %s, completed_at = NOW(),
                        verified_by_user_id = IF(%s = 'verified', %s, verified_by_user_id),
                        verified_at = IF(%s = 'verified', NOW(), verified_at)
                    WHERE id = %s
                """, (item_status, user_id, verification_status, user_id, verification_status, item_id))

                return new_report_id
        except mysql.connector.Error as err:
            logger.error(f"DB Error in save_lab_report_transaction: {err}")
            raise err

    @staticmethod
    def get_report_history(checklist_item_id):
        """Fetches all uploaded reports for a checklist item ordered by upload date."""
        query = """
            SELECT ur.*, u.first_name as uploader_first_name, u.last_name as uploader_last_name,
                   r.name as uploader_role
            FROM tbl_uploaded_reports ur
            LEFT JOIN tbl_users u ON ur.uploaded_by_user_id = u.id
            LEFT JOIN tbl_roles r ON u.role_id = r.id
            WHERE ur.checklist_item_id = %s
            ORDER BY ur.uploaded_at DESC, ur.id DESC
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (checklist_item_id,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_report_history: {err}")
            raise err

    @staticmethod
    def get_report_by_id(report_id):
        """Fetches detailed report metadata by report ID."""
        query = """
            SELECT ur.*, ci.task_name, ci.scheduled_procedure_id,
                   sp.patient_id, sp.doctor_id
            FROM tbl_uploaded_reports ur
            JOIN tbl_checklist_items ci ON ur.checklist_item_id = ci.id
            JOIN tbl_scheduled_procedures sp ON ci.scheduled_procedure_id = sp.id
            WHERE ur.id = %s
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (report_id,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_report_by_id: {err}")
            raise err

    @staticmethod
    def update_report_verification(report_id, doctor_id, verification_status, verification_notes=None):
        """
        Updates doctor verification status ('verified', 'needs_clarification', 'external_received', 'pending_verification') and notes.
        Also updates the associated checklist item status accordingly.
        """
        try:
            with DBTransactionContext() as cursor:
                cursor.execute("SELECT checklist_item_id FROM tbl_uploaded_reports WHERE id = %s", (report_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError("Report not found.")
                item_id = row['checklist_item_id']

                cursor.execute("""
                    UPDATE tbl_uploaded_reports 
                    SET verification_status = %s, verification_notes = %s, 
                        verified_by_doctor_id = %s, verified_at = NOW() 
                    WHERE id = %s
                """, (verification_status, verification_notes, doctor_id, report_id))

                if verification_status == 'verified':
                    new_item_status = 'verified'
                elif verification_status in ['needs_review', 'needs_clarification']:
                    new_item_status = 'pending'
                else:
                    new_item_status = 'completed'

                cursor.execute("""
                    UPDATE tbl_checklist_items 
                    SET status = %s, verified_by_user_id = %s, verified_at = NOW(), notes = %s 
                    WHERE id = %s
                """, (new_item_status, doctor_id, verification_notes, item_id))

        except mysql.connector.Error as err:
            logger.error(f"DB Error in update_report_verification: {err}")
            raise err

    @staticmethod
    def update_lab_report_metadata(item_id, user_id, lab_name, external_report_id=None, report_date=None, notes=None, task_name=None):
        """Updates metadata of the current official report and checklist item without changing file."""
        try:
            with DBTransactionContext() as cursor:
                if task_name:
                    cursor.execute("""
                        UPDATE tbl_checklist_items
                        SET task_name = %s
                        WHERE id = %s
                    """, (task_name, item_id))
                    
                cursor.execute("""
                    UPDATE tbl_uploaded_reports
                    SET lab_name = %s,
                        external_report_id = %s,
                        report_date = %s,
                        verification_notes = %s,
                        uploaded_by_user_id = %s
                    WHERE checklist_item_id = %s AND is_current = TRUE
                """, (lab_name, external_report_id, report_date, notes, user_id, item_id))
                
                cursor.execute("SELECT scheduled_procedure_id FROM tbl_checklist_items WHERE id = %s", (item_id,))
                row = cursor.fetchone()
                return row['scheduled_procedure_id'] if row else None
        except mysql.connector.Error as err:
            logger.error(f"DB Error in update_lab_report_metadata: {err}")
            raise err

    @staticmethod
    def get_report_by_file_path(file_path):
        """Fetches detailed report metadata by file_path or basename."""
        if not file_path:
            return None
        import os
        safe_name = os.path.basename(file_path.replace('\\', '/'))
        query = """
            SELECT ur.*, ci.task_name, ci.scheduled_procedure_id,
                   sp.patient_id, sp.doctor_id
            FROM tbl_uploaded_reports ur
            JOIN tbl_checklist_items ci ON ur.checklist_item_id = ci.id
            JOIN tbl_scheduled_procedures sp ON ci.scheduled_procedure_id = sp.id
            WHERE ur.file_path = %s OR ur.file_path = %s
            ORDER BY ur.id DESC
            LIMIT 1
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (file_path, safe_name))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_report_by_file_path: {err}")
            return None


