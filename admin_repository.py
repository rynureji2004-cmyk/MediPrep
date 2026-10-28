import mysql.connector
from database import DBConnectionContext, DBTransactionContext
import logging

logger = logging.getLogger(__name__)

class AdminRepository:
    """Handles raw SQL operations for administrative tasks in MySQL."""

    @staticmethod
    def get_admin_stats():
        """Fetches metadata count stats for the Admin Dashboard."""
        stats = {'doctors': 0, 'patients': 0, 'procedures': 0, 'schedules': 0}
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM tbl_doctor_profiles dp JOIN tbl_users u ON dp.user_id = u.id WHERE u.is_active = TRUE")
                    stats['doctors'] = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM tbl_patient_profiles pp JOIN tbl_users u ON pp.user_id = u.id WHERE u.is_active = TRUE")
                    stats['patients'] = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM tbl_procedures")
                    stats['procedures'] = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM tbl_scheduled_procedures sp 
                        JOIN tbl_users u_p ON sp.patient_id = u_p.id 
                        LEFT JOIN tbl_users u_d ON sp.doctor_id = u_d.id
                        WHERE u_p.is_active = TRUE 
                          AND (u_d.id IS NULL OR u_d.is_active = TRUE) 
                          AND sp.status = 'scheduled'
                    """)
                    stats['schedules'] = cursor.fetchone()[0]
        except mysql.connector.Error as err:
            logger.error(f"Error fetching admin stats: {err}")
        return stats

    @staticmethod
    def get_all_doctors(search_query=''):
        """Fetches doctor list with details, supporting search."""
        query = """
            SELECT u.id, u.username, u.email, u.first_name, u.last_name, u.phone, 
                   dp.license_number, dp.specialty, dp.department
            FROM tbl_users u
            JOIN tbl_doctor_profiles dp ON u.id = dp.user_id
            WHERE u.is_active = TRUE
        """
        params = []
        if search_query:
            query += " AND (u.first_name LIKE %s OR u.last_name LIKE %s OR dp.specialty LIKE %s OR dp.department LIKE %s)"
            like_str = f"%{search_query}%"
            params.extend([like_str, like_str, like_str, like_str])
            
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, tuple(params))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"Error fetching doctors list: {err}")
            return []

    @staticmethod
    def get_all_patients(search_query=''):
        """Fetches patient list with details, supporting search."""
        query = """
            SELECT u.id, u.username, u.email, u.first_name, u.last_name, u.phone, 
                   pp.date_of_birth, pp.gender, pp.blood_type, pp.medical_history, 
                   pp.emergency_contact_name, pp.emergency_contact_phone
            FROM tbl_users u
            JOIN tbl_patient_profiles pp ON u.id = pp.user_id
            WHERE u.is_active = TRUE
        """
        params = []
        if search_query:
            query += " AND (u.first_name LIKE %s OR u.last_name LIKE %s OR u.email LIKE %s)"
            like_str = f"%{search_query}%"
            params.extend([like_str, like_str, like_str])
            
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, tuple(params))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"Error fetching patients list: {err}")
            return []

    @staticmethod
    def get_all_procedures(search_query=''):
        """Fetches procedure type catalog, supporting search."""
        query = "SELECT * FROM tbl_procedures WHERE 1=1"
        params = []
        if search_query:
            query += " AND (code LIKE %s OR name LIKE %s OR category LIKE %s)"
            like_str = f"%{search_query}%"
            params.extend([like_str, like_str, like_str])
            
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, tuple(params))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"Error fetching procedures list: {err}")
            return []

    @staticmethod
    def get_doctor_by_id(doctor_user_id):
        """Fetches a specific doctor profile by user ID."""
        query = """
            SELECT u.id, u.username, u.email, u.first_name, u.last_name, u.phone, 
                   dp.license_number, dp.specialty, dp.department
            FROM tbl_users u
            JOIN tbl_doctor_profiles dp ON u.id = dp.user_id
            WHERE u.id = %s AND u.is_active = TRUE
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (doctor_user_id,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"Error getting doctor profile: {err}")
            return None

    @staticmethod
    def get_patient_by_id(patient_user_id):
        """Fetches a specific patient profile by user ID."""
        query = """
            SELECT u.id, u.username, u.email, u.first_name, u.last_name, u.phone, 
                   pp.date_of_birth, pp.gender, pp.blood_type, pp.medical_history, 
                   pp.emergency_contact_name, pp.emergency_contact_phone
            FROM tbl_users u
            JOIN tbl_patient_profiles pp ON u.id = pp.user_id
            WHERE u.id = %s AND u.is_active = TRUE
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (patient_user_id,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"Error getting patient profile: {err}")
            return None

    @staticmethod
    def get_procedure_by_id(proc_id):
        """Fetches a specific procedure template by ID."""
        query = "SELECT * FROM tbl_procedures WHERE id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (proc_id,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"Error getting procedure details: {err}")
            return None

    @staticmethod
    def create_doctor_transaction(user_data, doc_data):
        """Inserts user and doctor_profile records in a single transaction."""
        user_query = """
            INSERT INTO tbl_users (role_id, username, email, password_hash, first_name, last_name, phone)
            VALUES (3, %s, %s, %s, %s, %s, %s)
        """
        doc_query = """
            INSERT INTO tbl_doctor_profiles (user_id, license_number, specialty, department)
            VALUES (%s, %s, %s, %s)
        """
        try:
            with DBTransactionContext() as cursor:
                cursor.execute(user_query, (
                    user_data['username'],
                    user_data['email'],
                    user_data['password_hash'],
                    user_data['first_name'],
                    user_data['last_name'],
                    user_data.get('phone')
                ))
                new_user_id = cursor.lastrowid
                
                cursor.execute(doc_query, (
                    new_user_id,
                    doc_data['license_number'],
                    doc_data['specialty'],
                    doc_data['department']
                ))
                return new_user_id
        except mysql.connector.Error as err:
            logger.error(f"Transaction failed during doctor creation: {err}")
            raise err

    @staticmethod
    def email_exists_for_other(email, exclude_user_id):
        """Checks if an email is already registered to another user account."""
        query = "SELECT id FROM tbl_users WHERE LOWER(email) = LOWER(%s) AND id != %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (email, exclude_user_id))
                    return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            logger.error(f"DB Error in email_exists_for_other: {err}")
            raise err

    @staticmethod
    def license_exists(license_number):
        """Checks if a medical license number is already registered."""
        query = "SELECT id FROM tbl_doctor_profiles WHERE LOWER(license_number) = LOWER(%s)"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (license_number,))
                    return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            logger.error(f"DB Error in license_exists: {err}")
            raise err

    @staticmethod
    def license_exists_for_other(license_number, exclude_user_id):
        """Checks if a medical license code is registered to another clinician."""
        query = "SELECT id FROM tbl_doctor_profiles WHERE LOWER(license_number) = LOWER(%s) AND user_id != %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (license_number, exclude_user_id))
                    return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            logger.error(f"DB Error in license_exists_for_other: {err}")
            raise err

    @staticmethod
    def update_doctor_transaction(user_id, user_data, doc_data):
        """Updates user details and doctor_profile records in a transaction."""
        if user_data.get('password_hash'):
            user_query = """
                UPDATE tbl_users 
                SET email = %s, first_name = %s, last_name = %s, phone = %s, password_hash = %s
                WHERE id = %s
            """
            user_params = (
                user_data['email'],
                user_data['first_name'],
                user_data['last_name'],
                user_data.get('phone'),
                user_data['password_hash'],
                user_id
            )
        else:
            user_query = """
                UPDATE tbl_users 
                SET email = %s, first_name = %s, last_name = %s, phone = %s
                WHERE id = %s
            """
            user_params = (
                user_data['email'],
                user_data['first_name'],
                user_data['last_name'],
                user_data.get('phone'),
                user_id
            )

        doc_query = """
            UPDATE tbl_doctor_profiles 
            SET license_number = %s, specialty = %s, department = %s
            WHERE user_id = %s
        """
        try:
            with DBTransactionContext() as cursor:
                cursor.execute(user_query, user_params)
                cursor.execute(doc_query, (
                    doc_data['license_number'],
                    doc_data['specialty'],
                    doc_data['department'],
                    user_id
                ))
                return True
        except mysql.connector.Error as err:
            logger.error(f"Transaction failed during doctor update: {err}")
            raise err

    @staticmethod
    def create_patient_transaction(user_data, pat_data):
        """Inserts user and patient_profile records in a single transaction."""
        user_query = """
            INSERT INTO tbl_users (role_id, username, email, password_hash, first_name, last_name, phone)
            VALUES (COALESCE((SELECT id FROM tbl_roles WHERE name = 'patient'), 4), %s, %s, %s, %s, %s, %s)
        """
        pat_query = """
            INSERT INTO tbl_patient_profiles (user_id, date_of_birth, gender, blood_type, medical_history, emergency_contact_name, emergency_contact_phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            with DBTransactionContext() as cursor:
                cursor.execute(user_query, (
                    user_data['username'],
                    user_data['email'],
                    user_data['password_hash'],
                    user_data['first_name'],
                    user_data['last_name'],
                    user_data.get('phone')
                ))
                new_user_id = cursor.lastrowid
                
                cursor.execute(pat_query, (
                    new_user_id,
                    pat_data['date_of_birth'],
                    pat_data['gender'],
                    pat_data.get('blood_type'),
                    pat_data.get('medical_history'),
                    pat_data['emergency_contact_name'],
                    pat_data['emergency_contact_phone']
                ))
                return new_user_id
        except mysql.connector.Error as err:
            logger.error(f"Transaction failed during patient creation: {err}")
            raise err

    @staticmethod
    def update_patient_transaction(user_id, user_data, pat_data):
        """Updates user details and patient_profile records in a transaction."""
        user_query = """
            UPDATE tbl_users 
            SET email = %s, first_name = %s, last_name = %s, phone = %s
            WHERE id = %s
        """
        pat_query = """
            UPDATE tbl_patient_profiles 
            SET date_of_birth = %s, gender = %s, blood_type = %s, medical_history = %s, 
                emergency_contact_name = %s, emergency_contact_phone = %s
            WHERE user_id = %s
        """
        try:
            with DBTransactionContext() as cursor:
                cursor.execute(user_query, (
                    user_data['email'],
                    user_data['first_name'],
                    user_data['last_name'],
                    user_data.get('phone'),
                    user_id
                ))
                cursor.execute(pat_query, (
                    pat_data['date_of_birth'],
                    pat_data['gender'],
                    pat_data.get('blood_type'),
                    pat_data.get('medical_history'),
                    pat_data['emergency_contact_name'],
                    pat_data['emergency_contact_phone'],
                    user_id
                ))
                return True
        except mysql.connector.Error as err:
            logger.error(f"Transaction failed during patient update: {err}")
            raise err

    @staticmethod
    def has_patient_dependent_records(user_id):
        """
        Checks whether a patient has medical records that must be retained,
        such as scheduled procedures or clinical audit logs.
        """
        query = """
            SELECT 
                (SELECT COUNT(*) FROM tbl_scheduled_procedures WHERE patient_id = %s) +
                (SELECT COUNT(*) FROM tbl_audit_logs WHERE patient_id = %s) AS total_records
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (user_id, user_id))
                    row = cursor.fetchone()
                    return (row[0] if row else 0) > 0
        except mysql.connector.Error as err:
            logger.error(f"Error checking patient dependent records: {err}")
            raise err

    @staticmethod
    def has_doctor_dependent_records(user_id):
        """
        Checks whether a clinician has dependent medical records that must be retained,
        such as scheduled procedures, lab clarifications, or item verifications.
        """
        query = """
            SELECT 
                (SELECT COUNT(*) FROM tbl_scheduled_procedures WHERE doctor_id = %s) +
                (SELECT COUNT(*) FROM tbl_lab_clarifications WHERE doctor_id = %s) +
                (SELECT COUNT(*) FROM tbl_checklist_items WHERE completed_by_user_id = %s OR verified_by_user_id = %s) +
                (SELECT COUNT(*) FROM tbl_procedure_readiness WHERE evaluated_by_user_id = %s) +
                (SELECT COUNT(*) FROM tbl_audit_logs WHERE user_id = %s) AS total_records
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (user_id, user_id, user_id, user_id, user_id, user_id))
                    row = cursor.fetchone()
                    return (row[0] if row else 0) > 0
        except mysql.connector.Error as err:
            logger.error(f"Error checking clinician dependent records: {err}")
            raise err

    @staticmethod
    def deactivate_user(user_id):
        """Safely deactivates user account while retaining historical and medical data."""
        query = "UPDATE tbl_users SET is_active = FALSE WHERE id = %s"
        try:
            with DBTransactionContext() as cursor:
                cursor.execute(query, (user_id,))
                return True
        except mysql.connector.Error as err:
            logger.error(f"Error deactivating user account {user_id}: {err}")
            raise err

    @staticmethod
    def delete_user_permanently(user_id):
        """Permanently deletes a user core account and cascaded profiles."""
        query = "DELETE FROM tbl_users WHERE id = %s"
        try:
            with DBTransactionContext() as cursor:
                cursor.execute(query, (user_id,))
                return True
        except mysql.connector.Error as err:
            logger.error(f"Failed to permanently delete user account {user_id}: {err}")
            raise err

    @staticmethod
    def delete_patient(user_id):
        """
        Deletes a patient account:
        - If the patient has medical records (e.g. scheduled procedures), safely deactivates
          the account to retain clinical history without violating foreign key constraints.
        - If the patient has no dependent medical records, permanently deletes the account.
        Returns tuple: (action, message) where action is 'deleted' or 'deactivated'.
        """
        check_query = "SELECT u.id, u.is_active, r.name FROM tbl_users u JOIN tbl_roles r ON u.role_id = r.id WHERE u.id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(check_query, (user_id,))
                    user = cursor.fetchone()
            
            if not user:
                return ('not_found', "Patient record not found.")

            if AdminRepository.has_patient_dependent_records(user_id):
                AdminRepository.deactivate_user(user_id)
                # Cancel pending scheduled procedures for the deactivated patient
                cancel_query = "UPDATE tbl_scheduled_procedures SET status = 'cancelled' WHERE patient_id = %s AND status = 'scheduled'"
                with DBTransactionContext() as cursor:
                    cursor.execute(cancel_query, (user_id,))
                logger.info(f"Patient ID {user_id} has existing medical records; safely deactivated account and cancelled pending bookings.")
                return ('deactivated', "Patient account has existing medical records and was safely deactivated to preserve clinical history.")
            else:
                AdminRepository.delete_user_permanently(user_id)
                logger.info(f"Patient ID {user_id} had no dependent records; permanently deleted.")
                return ('deleted', "Patient account deleted successfully.")
        except mysql.connector.Error as err:
            logger.error(f"Error in delete_patient for user {user_id}: {err}")
            raise err

    @staticmethod
    def delete_doctor(user_id):
        """
        Deletes a clinician account:
        - If the clinician has associated procedure or clinical records, safely deactivates
          the account to retain records without violating foreign key constraints.
        - If the clinician has no dependent records, permanently deletes the account.
        Returns tuple: (action, message) where action is 'deleted' or 'deactivated'.
        """
        check_query = "SELECT u.id, u.is_active, r.name FROM tbl_users u JOIN tbl_roles r ON u.role_id = r.id WHERE u.id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(check_query, (user_id,))
                    user = cursor.fetchone()
            
            if not user:
                return ('not_found', "Clinician record not found.")

            if AdminRepository.has_doctor_dependent_records(user_id):
                AdminRepository.deactivate_user(user_id)
                # Cancel pending scheduled procedures for the deactivated doctor
                cancel_query = "UPDATE tbl_scheduled_procedures SET status = 'cancelled' WHERE doctor_id = %s AND status = 'scheduled'"
                with DBTransactionContext() as cursor:
                    cursor.execute(cancel_query, (user_id,))
                logger.info(f"Doctor ID {user_id} has associated procedure records; safely deactivated account and cancelled pending bookings.")
                return ('deactivated', "Doctor account has associated procedure records and was safely deactivated to preserve clinical history.")
            else:
                AdminRepository.delete_user_permanently(user_id)
                logger.info(f"Doctor ID {user_id} had no dependent records; permanently deleted.")
                return ('deleted', "Doctor account deleted successfully.")
        except mysql.connector.Error as err:
            logger.error(f"Error in delete_doctor for user {user_id}: {err}")
            raise err

    @staticmethod
    def delete_user_transaction(user_id):
        """
        Deletes user core account if no dependent records exist;
        otherwise safely deactivates the account to retain medical records.
        """
        role_query = "SELECT r.name FROM tbl_users u JOIN tbl_roles r ON u.role_id = r.id WHERE u.id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(role_query, (user_id,))
                    row = cursor.fetchone()
                    role_name = row[0] if row else None

            if role_name == 'patient':
                action, msg = AdminRepository.delete_patient(user_id)
                return True
            elif role_name == 'doctor':
                action, msg = AdminRepository.delete_doctor(user_id)
                return True
            else:
                has_schedules_query = "SELECT COUNT(*) FROM tbl_scheduled_procedures WHERE patient_id = %s OR doctor_id = %s"
                with DBConnectionContext() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(has_schedules_query, (user_id, user_id))
                        cnt = cursor.fetchone()[0]
                if cnt > 0:
                    AdminRepository.deactivate_user(user_id)
                else:
                    AdminRepository.delete_user_permanently(user_id)
                return True
        except mysql.connector.Error as err:
            logger.error(f"Failed to process user account deletion: {err}")
            raise err

    @staticmethod
    def get_procedure_by_code(code):
        """Fetches a specific procedure template by CPT/procedure code."""
        query = "SELECT * FROM tbl_procedures WHERE code = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (code,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"Error getting procedure by code: {err}")
            return None

    @staticmethod
    def create_procedure(proc_data):
        """Creates a new predefined procedure type."""
        query = """
            INSERT INTO tbl_procedures (code, name, description, category, est_duration_mins)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (
                        proc_data['code'],
                        proc_data['name'],
                        proc_data.get('description'),
                        proc_data['category'],
                        proc_data.get('est_duration_mins', 60)
                    ))
                    conn.commit()
                    return cursor.lastrowid
        except mysql.connector.Error as err:
            logger.error(f"Error creating procedure: {err}")
            raise err

    @staticmethod
    def update_procedure(proc_id, proc_data):
        """Updates a predefined procedure type catalog definition."""
        query = """
            UPDATE tbl_procedures 
            SET code = %s, name = %s, description = %s, category = %s, est_duration_mins = %s
            WHERE id = %s
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (
                        proc_data['code'],
                        proc_data['name'],
                        proc_data.get('description'),
                        proc_data['category'],
                        proc_data.get('est_duration_mins', 60),
                        proc_id
                    ))
                    conn.commit()
                    return True
        except mysql.connector.Error as err:
            logger.error(f"Error updating procedure: {err}")
            raise err

    @staticmethod
    def delete_procedure(proc_id):
        """Deletes a procedure definition from catalog."""
        query = "DELETE FROM tbl_procedures WHERE id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (proc_id,))
                    conn.commit()
                    return True
        except mysql.connector.Error as err:
            logger.error(f"Error deleting procedure: {err}")
            raise err

    @staticmethod
    def get_upcoming_procedures(limit=5):
        """Fetches a list of upcoming scheduled procedures across all clinicians."""
        query = """
            SELECT sp.*, 
                   u_p.first_name as patient_first_name, u_p.last_name as patient_last_name, u_p.email as patient_email,
                   u_d.first_name as doctor_first_name, u_d.last_name as doctor_last_name,
                   p.name as procedure_name, p.code as procedure_code,
                   pr.readiness_status
            FROM tbl_scheduled_procedures sp
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            LEFT JOIN tbl_users u_d ON sp.doctor_id = u_d.id
            LEFT JOIN tbl_procedure_readiness pr ON sp.id = pr.scheduled_procedure_id
            WHERE u_p.is_active = TRUE 
              AND (u_d.id IS NULL OR u_d.is_active = TRUE)
              AND sp.status = 'scheduled'
            ORDER BY sp.scheduled_at ASC
            LIMIT %s
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (limit,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"Error fetching upcoming procedures: {err}")
            return []
