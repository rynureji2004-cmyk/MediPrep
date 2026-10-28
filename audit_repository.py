import mysql.connector
from database import DBConnectionContext
import logging

logger = logging.getLogger(__name__)

class AuditRepository:
    """Handles logging security and clinical audit trail entries."""

    @staticmethod
    def log_audit_action(user_id, role_name, action, details=None, patient_id=None, scheduled_procedure_id=None):
        """Logs an event to tbl_audit_logs."""
        query = """
            INSERT INTO tbl_audit_logs (user_id, role_name, action, details, patient_id, scheduled_procedure_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (user_id, role_name, action, details, patient_id, scheduled_procedure_id))
                    conn.commit()
        except mysql.connector.Error as err:
            logger.error(f"DB Error logging audit action: {err}")

    @staticmethod
    def get_audit_trail(scheduled_procedure_id=None, limit=50):
        """Fetches audit trail logs."""
        query = """
            SELECT al.*, u.first_name, u.last_name
            FROM tbl_audit_logs al
            LEFT JOIN tbl_users u ON al.user_id = u.id
        """
        params = []
        if scheduled_procedure_id:
            query += " WHERE al.scheduled_procedure_id = %s"
            params.append(scheduled_procedure_id)

        query += " ORDER BY al.id DESC LIMIT %s"
        params.append(limit)

        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, tuple(params))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_audit_trail: {err}")
            return []
