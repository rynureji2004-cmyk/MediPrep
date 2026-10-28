import mysql.connector
from database import DBConnectionContext, DBTransactionContext
from app.models.user import User, DoctorProfile, PatientProfile
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    """Handles raw SQL operations for user records in MySQL."""

    @staticmethod
    def find_by_username(username):
        """Fetches a user and their role name by username."""
        query = """
            SELECT u.*, r.name as role_name 
            FROM tbl_users u
            JOIN tbl_roles r ON u.role_id = r.id
            WHERE u.username = %s AND u.is_active = TRUE
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (username,))
                    row = cursor.fetchone()
                    if row:
                        return row
        except mysql.connector.Error as err:
            logger.error(f"DB Error in find_by_username: {err}")
            raise err
        return None

    @staticmethod
    def find_by_email(email):
        """Fetches a user and their role name by email address."""
        query = """
            SELECT u.*, r.name as role_name 
            FROM tbl_users u
            JOIN tbl_roles r ON u.role_id = r.id
            WHERE u.email = %s AND u.is_active = TRUE
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (email,))
                    row = cursor.fetchone()
                    if row:
                        return row
        except mysql.connector.Error as err:
            logger.error(f"DB Error in find_by_email: {err}")
            raise err
        return None

    @staticmethod
    def username_exists(username):
        """Checks if a username already exists in tbl_users (case-insensitive)."""
        query = "SELECT id FROM tbl_users WHERE LOWER(username) = LOWER(%s)"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (username,))
                    return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            logger.error(f"DB Error in username_exists: {err}")
            raise err

    @staticmethod
    def email_exists(email):
        """Checks if an email address already exists in tbl_users (case-insensitive)."""
        query = "SELECT id FROM tbl_users WHERE LOWER(email) = LOWER(%s)"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (email,))
                    return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            logger.error(f"DB Error in email_exists: {err}")
            raise err

    @staticmethod
    def phone_exists(phone):
        """Checks if a phone number exists in tbl_users."""
        if not phone:
            return False
        query = "SELECT id FROM tbl_users WHERE phone = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (phone,))
                    return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            logger.error(f"DB Error in phone_exists: {err}")
            raise err

    @staticmethod
    def find_by_id(user_id):
        """Fetches a user and their role name by user ID."""
        query = """
            SELECT u.*, r.name as role_name 
            FROM tbl_users u
            JOIN tbl_roles r ON u.role_id = r.id
            WHERE u.id = %s AND u.is_active = TRUE
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (user_id,))
                    row = cursor.fetchone()
                    if row:
                        return row
        except mysql.connector.Error as err:
            logger.error(f"DB Error in find_by_id: {err}")
            raise err
        return None

    @staticmethod
    def update_password(user_id, password_hash):
        """Updates password hash for a given user ID."""
        query = "UPDATE tbl_users SET password_hash = %s WHERE id = %s AND is_active = TRUE"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (password_hash, user_id))
                    conn.commit()
                    return cursor.rowcount > 0
        except mysql.connector.Error as err:
            logger.error(f"DB Error in update_password: {err}")
            raise err


    @staticmethod
    def get_role_id_by_name(role_name):
        """Helper to get a role ID from its name."""
        query = "SELECT id FROM tbl_roles WHERE name = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (role_name,))
                    row = cursor.fetchone()
                    if row:
                        return row[0]
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_role_id_by_name: {err}")
            raise err
        return None

    @staticmethod
    def create_user_transaction(user_data, profile_data=None):
        """
        Creates a user and their role profile inside a transactional context.
        Rolls back if any statement fails.
        """
        user_insert_query = """
            INSERT INTO tbl_users (role_id, username, email, password_hash, first_name, last_name, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            with DBTransactionContext() as cursor:
                # 1. Insert Core User Record
                cursor.execute(user_insert_query, (
                    user_data['role_id'],
                    user_data['username'],
                    user_data['email'],
                    user_data['password_hash'],
                    user_data['first_name'],
                    user_data['last_name'],
                    user_data.get('phone')
                ))
                new_user_id = cursor.lastrowid
                
                # 2. Insert Role-Specific Profile (Doctor or Patient) if provided
                if profile_data and user_data['role_name'] == 'doctor':
                    doc_query = """
                        INSERT INTO tbl_doctor_profiles (user_id, license_number, specialty, department)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(doc_query, (
                        new_user_id,
                        profile_data['license_number'],
                        profile_data['specialty'],
                        profile_data['department']
                    ))
                elif profile_data and user_data['role_name'] == 'patient':
                    pat_query = """
                        INSERT INTO tbl_patient_profiles (user_id, date_of_birth, gender, blood_type, medical_history, emergency_contact_name, emergency_contact_phone)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(pat_query, (
                        new_user_id,
                        profile_data['date_of_birth'],
                        profile_data['gender'],
                        profile_data.get('blood_type'),
                        profile_data.get('medical_history'),
                        profile_data['emergency_contact_name'],
                        profile_data['emergency_contact_phone']
                    ))
                elif profile_data and user_data['role_name'] == 'lab_tech':
                    lab_query = """
                        INSERT INTO tbl_lab_profiles (user_id, lab_name, lab_type)
                        VALUES (%s, %s, 'hospital')
                    """
                    cursor.execute(lab_query, (
                        new_user_id,
                        profile_data.get('lab_name', 'Central Hospital Clinical Laboratory')
                    ))
                
                return new_user_id

        except mysql.connector.Error as err:
            logger.error(f"Transaction failed during user creation: {err}")
            raise err
