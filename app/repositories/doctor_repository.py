import mysql.connector
from database import DBConnectionContext, DBTransactionContext
import logging

logger = logging.getLogger(__name__)

class DoctorRepository:
    """Handles raw SQL operations for doctor operations and scheduling in MySQL."""

    @staticmethod
    def get_dashboard_stats(doctor_id):
        """Fetches counts of patients, pending reports, and active alerts for a doctor."""
        stats = {
            'total_patients': 0,
            'pending_verifications': 0,
            'high_risk_alerts': 0
        }
        
        # 1. Total unique patients assigned to this doctor
        patients_query = """
            SELECT COUNT(DISTINCT sp.patient_id) 
            FROM tbl_scheduled_procedures sp
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            WHERE sp.doctor_id = %s AND u_p.is_active = TRUE AND sp.status = 'scheduled'
        """
        
        # 2. Checklist items requiring verification (document uploads or staff checks)
        # where status is 'completed' (done by patient, but not yet 'verified' by staff)
        pending_query = """
            SELECT COUNT(ci.id)
            FROM tbl_checklist_items ci
            JOIN tbl_scheduled_procedures sp ON ci.scheduled_procedure_id = sp.id
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            WHERE sp.doctor_id = %s AND ci.status = 'completed' AND u_p.is_active = TRUE AND sp.status = 'scheduled'
        """
        
        # 3. High severity unresolved risk alerts
        alerts_query = """
            SELECT COUNT(ra.id)
            FROM tbl_risk_alerts ra
            JOIN tbl_scheduled_procedures sp ON ra.scheduled_procedure_id = sp.id
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            WHERE sp.doctor_id = %s AND ra.is_resolved = FALSE AND ra.severity = 'high' AND u_p.is_active = TRUE AND sp.status = 'scheduled'
        """
        
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    # Execute Patients Count
                    cursor.execute(patients_query, (doctor_id,))
                    row = cursor.fetchone()
                    if row:
                        stats['total_patients'] = row[0]
                        
                    # Execute Pending Review Count
                    cursor.execute(pending_query, (doctor_id,))
                    row = cursor.fetchone()
                    if row:
                        stats['pending_verifications'] = row[0]
                        
                    # Execute Alerts Count
                    cursor.execute(alerts_query, (doctor_id,))
                    row = cursor.fetchone()
                    if row:
                        stats['high_risk_alerts'] = row[0]
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_dashboard_stats: {err}")
            raise err
            
        return stats

    @staticmethod
    def get_schedules_by_doctor(doctor_id, search_query=None):
        """Fetches all scheduled procedures for a doctor, optionally filtering by search."""
        query = """
            SELECT sp.*, 
                   u_p.first_name as patient_first_name, u_p.last_name as patient_last_name, u_p.email as patient_email,
                   p.name as procedure_name, p.code as procedure_code,
                   pr.readiness_status
            FROM tbl_scheduled_procedures sp
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            LEFT JOIN tbl_procedure_readiness pr ON sp.id = pr.scheduled_procedure_id
            WHERE sp.doctor_id = %s AND u_p.is_active = TRUE AND sp.status = 'scheduled'
        """
        params = [doctor_id]
        
        if search_query:
            query += " AND (u_p.first_name LIKE %s OR u_p.last_name LIKE %s OR p.name LIKE %s)"
            like_val = f"%{search_query}%"
            params.extend([like_val, like_val, like_val])
            
        query += " ORDER BY sp.scheduled_at ASC"
        
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, tuple(params))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_schedules_by_doctor: {err}")
            raise err

    @staticmethod
    def get_schedule_by_id(schedule_id):
        """Fetches detailed scheduling record by ID."""
        query = """
            SELECT sp.*, 
                   u_p.first_name as patient_first_name, u_p.last_name as patient_last_name,
                   p.name as procedure_name, p.code as procedure_code
            FROM tbl_scheduled_procedures sp
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            WHERE sp.id = %s
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (schedule_id,))
                    return cursor.fetchone()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_schedule_by_id: {err}")
            raise err

    @staticmethod
    def get_patients_list():
        """Fetches basic records of all patients in the system."""
        query = """
            SELECT id, first_name, last_name, email 
            FROM tbl_users 
            WHERE role_id = (SELECT id FROM tbl_roles WHERE name = 'patient') AND is_active = TRUE
            ORDER BY last_name, first_name
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_patients_list: {err}")
            raise err

    @staticmethod
    def get_procedures_list():
        """Fetches catalog of all procedures."""
        query = "SELECT id, name, code, category FROM tbl_procedures ORDER BY name"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_procedures_list: {err}")
            raise err

    @staticmethod
    def get_checklist_templates(procedure_id):
        """Fetches dynamic checklist templates relative to a procedure type."""
        # Note: If dynamic templates table isn't fully created, fall back to standard pre-op templates
        query = """
            SELECT task_name, task_type, description, due_days_before, is_critical
            FROM tbl_dynamic_checklist_templates
            WHERE procedure_id = %s
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (procedure_id,))
                    rows = cursor.fetchall()
                    if rows:
                        return rows
        except mysql.connector.Error as err:
            logger.warning(f"Error fetching checklist templates, returning default mocks: {err}")
            
        return [
            {"task_name": "NPO Fasting (No food or water)", "task_type": "patient_action", "description": "Fasting is required 8 hours prior to procedure", "due_days_before": 1, "is_critical": True},
            {"task_name": "Confirm Escort Driver", "task_type": "patient_action", "description": "Responsible adult escort to drive you home", "due_days_before": 0, "is_critical": False},
            {"task_name": "Sign Informed Consent Form", "task_type": "patient_action", "description": "Verify signed consent form is scanned and uploaded", "due_days_before": 0, "is_critical": True}
        ]

    @staticmethod
    def ensure_checklist_initialized(scheduled_id):
        """
        Ensures a scheduled procedure has its checklist items populated from templates if empty.
        """
        from datetime import datetime, timedelta
        query_check = "SELECT COUNT(*) FROM tbl_checklist_items WHERE scheduled_procedure_id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query_check, (scheduled_id,))
                    row = cursor.fetchone()
                    if row and row[0] > 0:
                        return

            schedule_info = DoctorRepository.get_schedule_by_id(scheduled_id)
            if not schedule_info:
                return

            procedure_id = schedule_info['procedure_id']
            scheduled_at = schedule_info['scheduled_at']
            if isinstance(scheduled_at, str):
                from app.utilities.validators import validate_and_parse_datetime
                try:
                    scheduled_at = validate_and_parse_datetime(scheduled_at)
                except Exception:
                    scheduled_at = datetime.now()
            elif not scheduled_at:
                scheduled_at = datetime.now()

            templates = DoctorRepository.get_checklist_templates(procedure_id)
            if not templates:
                return

            insert_item_query = """
                INSERT INTO tbl_checklist_items (scheduled_procedure_id, task_name, task_type, description, due_by_datetime, is_critical, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'pending')
            """
            with DBTransactionContext() as cursor:
                for t in templates:
                    due_days = int(t.get('due_days_before', 0))
                    due_by = scheduled_at - timedelta(days=due_days) if hasattr(scheduled_at, '__sub__') else datetime.now()
                    due_by_str = due_by.strftime("%Y-%m-%d %H:%M:%S") if hasattr(due_by, 'strftime') else str(due_by)
                    cursor.execute(insert_item_query, (
                        scheduled_id,
                        t['task_name'],
                        t['task_type'],
                        t.get('description', ''),
                        due_by_str,
                        bool(t.get('is_critical', False))
                    ))
        except mysql.connector.Error as err:
            logger.error(f"Error in ensure_checklist_initialized for schedule {scheduled_id}: {err}")

    @staticmethod
    def get_procedure_rooms():
        """Fetches procedure room options grouped by procedure_id and room_type."""
        query = "SELECT procedure_id, room_type, room_name FROM tbl_procedure_rooms ORDER BY id"
        rooms_map = {}
        all_prep = []
        all_proc = []
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()

                    # Fallback auto-seed if table is empty
                    if not rows:
                        from seed_rooms import seed_rooms
                        seed_rooms()
                        cursor.execute(query)
                        rows = cursor.fetchall()

                    for row in rows:
                        p_id = str(row['procedure_id'])
                        r_type = row['room_type']
                        r_name = row['room_name']

                        if r_type == 'preparation' and r_name not in all_prep:
                            all_prep.append(r_name)
                        elif r_type == 'procedure' and r_name not in all_proc:
                            all_proc.append(r_name)

                        if p_id not in rooms_map:
                            rooms_map[p_id] = {'preparation': [], 'procedure': []}
                        if r_type in rooms_map[p_id] and r_name not in rooms_map[p_id][r_type]:
                            rooms_map[p_id][r_type].append(r_name)

            # Ensure default entry exists
            rooms_map['default'] = {
                'preparation': all_prep if all_prep else [
                    "Pre-Procedure Preparation Room 1",
                    "Pre-Procedure Preparation Room 2",
                    "General Patient Preparation Room"
                ],
                'procedure': all_proc if all_proc else [
                    "MRI Scanning Room 1",
                    "MRI Scanning Room 2",
                    "CT Scanning Room 1",
                    "Endoscopy Room 1",
                    "Cardiac Procedure Room 1",
                    "General Procedure Room 1"
                ]
            }

            return rooms_map
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_procedure_rooms: {err}")
            return {
                'default': {
                    'preparation': [
                        "Pre-Procedure Preparation Room 1",
                        "Pre-Procedure Preparation Room 2",
                        "General Patient Preparation Room"
                    ],
                    'procedure': [
                        "MRI Scanning Room 1",
                        "MRI Scanning Room 2",
                        "CT Scanning Room 1",
                        "Endoscopy Room 1",
                        "Cardiac Procedure Room 1",
                        "General Procedure Room 1"
                    ]
                }
            }

    @staticmethod
    def get_distinct_rooms(room_type=None):
        """Fetches distinct room names from tbl_procedure_rooms, optionally filtered by room_type."""
        if room_type:
            query = "SELECT DISTINCT room_name FROM tbl_procedure_rooms WHERE room_type = %s ORDER BY id"
            params = (room_type,)
        else:
            query = "SELECT DISTINCT room_name FROM tbl_procedure_rooms ORDER BY id"
            params = ()

        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, params)
                    rooms = [row['room_name'] for row in cursor.fetchall()]
                    if rooms:
                        return rooms
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_distinct_rooms: {err}")

        # Fallback defaults if DB empty or error
        if room_type == 'preparation':
            return [
                "Pre-Procedure Preparation Room 1",
                "Pre-Procedure Preparation Room 2",
                "General Patient Preparation Room"
            ]
        elif room_type == 'procedure':
            return [
                "MRI Scanning Room 1",
                "MRI Scanning Room 2",
                "CT Scanning Room 1",
                "Endoscopy Room 1",
                "Cardiac Procedure Room 1",
                "General Procedure Room 1"
            ]
        return [
            "Pre-Procedure Preparation Room 1",
            "Pre-Procedure Preparation Room 2",
            "General Patient Preparation Room",
            "MRI Scanning Room 1",
            "MRI Scanning Room 2",
            "CT Scanning Room 1",
            "Endoscopy Room 1",
            "Cardiac Procedure Room 1",
            "General Procedure Room 1"
        ]

    @staticmethod
    def resolve_room_name(room_input, procedure_id=None, room_type=None):
        """
        Resolves room input (whether passed as integer ID or room name string)
        to the canonical room name stored in tbl_procedure_rooms.
        """
        if not room_input:
            return ""

        input_str = str(room_input).strip()
        if input_str.isdigit():
            # Query by database ID
            query = "SELECT room_name FROM tbl_procedure_rooms WHERE id = %s"
            try:
                with DBConnectionContext() as conn:
                    with conn.cursor(dictionary=True) as cursor:
                        cursor.execute(query, (int(input_str),))
                        row = cursor.fetchone()
                        if row and row.get('room_name'):
                            return row['room_name']
            except mysql.connector.Error as err:
                logger.error(f"DB Error in resolve_room_name: {err}")

        return input_str

    @staticmethod
    def find_duplicate_schedule(patient_id, procedure_id, scheduled_at=None, exclude_schedule_id=None):
        """
        Checks if an active booking already exists for the given patient and procedure across all doctors.
        Returns the existing booking dictionary with details, or None if no duplicate exists.
        """
        query = """
            SELECT sp.id, sp.scheduled_at, sp.status, sp.doctor_id,
                   p.name AS procedure_name, p.code AS procedure_code,
                   u_doc.first_name AS doctor_first_name, u_doc.last_name AS doctor_last_name
            FROM tbl_scheduled_procedures sp
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            LEFT JOIN tbl_users u_doc ON sp.doctor_id = u_doc.id
            WHERE sp.patient_id = %s
              AND sp.procedure_id = %s
              AND sp.status IN ('scheduled', 'delayed')
        """
        params = [patient_id, procedure_id]
        if exclude_schedule_id:
            query += " AND sp.id != %s"
            params.append(exclude_schedule_id)
            
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, tuple(params))
                    rows = cursor.fetchall()
                    if not rows:
                        return None
                    
                    if scheduled_at:
                        s_dt_str = scheduled_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(scheduled_at, 'strftime') else str(scheduled_at)
                        for r in rows:
                            r_dt_str = r['scheduled_at'].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r['scheduled_at'], 'strftime') else str(r['scheduled_at'])
                            if r_dt_str == s_dt_str:
                                r['is_exact_time_match'] = True
                                return r
                                
                    rows[0]['is_exact_time_match'] = False
                    return rows[0]
        except mysql.connector.Error as err:
            logger.error(f"DB Error in find_duplicate_schedule: {err}")
            return None

    @staticmethod
    def create_schedule_transaction(patient_id, doctor_id, procedure_id, scheduled_at, preparation_room, procedure_room, checklist_items):
        """
        Creates a scheduled procedure, inserts its dynamic checklist items,
        and initializes readiness cache in a safe database transaction.
        """
        insert_schedule_query = """
            INSERT INTO tbl_scheduled_procedures (patient_id, doctor_id, procedure_id, scheduled_at, preparation_room, procedure_room, location, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'scheduled')
        """
        
        insert_item_query = """
            INSERT INTO tbl_checklist_items (scheduled_procedure_id, task_name, task_type, description, due_by_datetime, is_critical, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
        """
        
        insert_readiness_query = """
            INSERT INTO tbl_procedure_readiness (scheduled_procedure_id, readiness_status, notes)
            VALUES (%s, 'red', 'Initial scheduling setup. Dynamic checklist initialized.')
        """

        try:
            with DBTransactionContext() as cursor:
                # 0. Check duplicate booking inside transaction with lock
                cursor.execute("""
                    SELECT sp.id, sp.scheduled_at, sp.doctor_id, p.name AS procedure_name, p.code AS procedure_code,
                           u_doc.first_name AS doctor_first_name, u_doc.last_name AS doctor_last_name
                    FROM tbl_scheduled_procedures sp
                    JOIN tbl_procedures p ON sp.procedure_id = p.id
                    LEFT JOIN tbl_users u_doc ON sp.doctor_id = u_doc.id
                    WHERE sp.patient_id = %s
                      AND sp.procedure_id = %s
                      AND sp.status IN ('scheduled', 'delayed')
                    FOR UPDATE
                """, (patient_id, procedure_id))
                existing_active = cursor.fetchall()
                if existing_active:
                    target_dt_str = scheduled_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(scheduled_at, 'strftime') else str(scheduled_at)
                    for ex in existing_active:
                        ex_dt_str = ex['scheduled_at'].strftime("%Y-%m-%d %H:%M:%S") if hasattr(ex['scheduled_at'], 'strftime') else str(ex['scheduled_at'])
                        doc_name = f"Dr. {ex['doctor_first_name']} {ex['doctor_last_name']}" if ex.get('doctor_first_name') else f"Doctor ID {ex['doctor_id']}"
                        if ex_dt_str == target_dt_str:
                            raise ValueError(f"Duplicate booking skipped: Patient already has an active booking for '{ex['procedure_name']}' ({ex['procedure_code']}) at the same scheduled time ({ex_dt_str}) with {doc_name}.")
                        else:
                            raise ValueError(f"Duplicate booking skipped: Patient already has an active booking for '{ex['procedure_name']}' ({ex['procedure_code']}) scheduled at {ex_dt_str} with {doc_name}.")

                # 1. Insert schedule row
                cursor.execute(insert_schedule_query, (patient_id, doctor_id, procedure_id, scheduled_at, preparation_room, procedure_room, procedure_room))
                new_schedule_id = cursor.lastrowid
                
                # 2. Insert checklist items
                for item in checklist_items:
                    cursor.execute(insert_item_query, (
                        new_schedule_id,
                        item['task_name'],
                        item['task_type'],
                        item['description'],
                        item['due_by_datetime'],
                        item['is_critical']
                    ))
                    
                # 3. Create readiness status placeholder
                cursor.execute(insert_readiness_query, (new_schedule_id,))
                
                return new_schedule_id
        except mysql.connector.Error as err:
            logger.error(f"Transaction failed in create_schedule: {err}")
            raise err

    @staticmethod
    def update_schedule_transaction(schedule_id, patient_id, procedure_id, scheduled_at, preparation_room, procedure_room, status, rebuild_checklist=False, checklist_items=None):
        """Updates scheduling parameters, optionally rebuilding the checklist items."""
        update_query = """
            UPDATE tbl_scheduled_procedures 
            SET patient_id = %s, procedure_id = %s, scheduled_at = %s, preparation_room = %s, procedure_room = %s, location = %s, status = %s
            WHERE id = %s
        """
        
        delete_items_query = "DELETE FROM tbl_checklist_items WHERE scheduled_procedure_id = %s"
        insert_item_query = """
            INSERT INTO tbl_checklist_items (scheduled_procedure_id, task_name, task_type, description, due_by_datetime, is_critical, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
        """
        
        try:
            with DBTransactionContext() as cursor:
                # 0. Check duplicate booking inside transaction with lock if status is active
                if status in ['scheduled', 'delayed']:
                    cursor.execute("""
                        SELECT sp.id, sp.scheduled_at, sp.doctor_id, p.name AS procedure_name, p.code AS procedure_code,
                               u_doc.first_name AS doctor_first_name, u_doc.last_name AS doctor_last_name
                        FROM tbl_scheduled_procedures sp
                        JOIN tbl_procedures p ON sp.procedure_id = p.id
                        LEFT JOIN tbl_users u_doc ON sp.doctor_id = u_doc.id
                        WHERE sp.patient_id = %s
                          AND sp.procedure_id = %s
                          AND sp.status IN ('scheduled', 'delayed')
                          AND sp.id != %s
                        FOR UPDATE
                    """, (patient_id, procedure_id, schedule_id))
                    existing_active = cursor.fetchall()
                    if existing_active:
                        target_dt_str = scheduled_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(scheduled_at, 'strftime') else str(scheduled_at)
                        for ex in existing_active:
                            ex_dt_str = ex['scheduled_at'].strftime("%Y-%m-%d %H:%M:%S") if hasattr(ex['scheduled_at'], 'strftime') else str(ex['scheduled_at'])
                            doc_name = f"Dr. {ex['doctor_first_name']} {ex['doctor_last_name']}" if ex.get('doctor_first_name') else f"Doctor ID {ex['doctor_id']}"
                            if ex_dt_str == target_dt_str:
                                raise ValueError(f"Duplicate booking skipped: Patient already has an active booking for '{ex['procedure_name']}' ({ex['procedure_code']}) at the same scheduled time ({ex_dt_str}) with {doc_name}.")
                            else:
                                raise ValueError(f"Duplicate booking skipped: Patient already has an active booking for '{ex['procedure_name']}' ({ex['procedure_code']}) scheduled at {ex_dt_str} with {doc_name}.")

                # Update main schedule record
                cursor.execute(update_query, (patient_id, procedure_id, scheduled_at, preparation_room, procedure_room, procedure_room, status, schedule_id))
                
                if rebuild_checklist and checklist_items:
                    # Clean existing checklist items
                    cursor.execute(delete_items_query, (schedule_id,))
                    # Insert new ones
                    for item in checklist_items:
                        cursor.execute(insert_item_query, (
                            schedule_id,
                            item['task_name'],
                            item['task_type'],
                            item['description'],
                            item['due_by_datetime'],
                            item['is_critical']
                        ))
                    
                    # Reset readiness status to red upon rebuild
                    reset_readiness = "UPDATE tbl_procedure_readiness SET readiness_status = 'red', notes = 'Checklist rebuilt due to scheduling update.' WHERE scheduled_procedure_id = %s"
                    cursor.execute(reset_readiness, (schedule_id,))
        except mysql.connector.Error as err:
            logger.error(f"Transaction failed in update_schedule: {err}")
            raise err

    @staticmethod
    def get_active_checklist_items(scheduled_id):
        """Fetches current checklist items for a scheduled procedure with lab report details."""
        DoctorRepository.ensure_checklist_initialized(scheduled_id)
        query = """
            SELECT ci.*, 
                   ur.id as report_id, ur.file_name, ur.file_path, 
                   COALESCE(ur.lab_name, lp.lab_name, ci.lab_name, 'Hospital Laboratory') as report_lab_name,
                   COALESCE(ur.lab_type, CASE WHEN ci.is_external THEN 'external' ELSE 'hospital' END) as report_lab_type,
                   ur.external_report_id, ur.report_date,
                   ur.verification_status as report_verification_status, ur.verification_notes as report_verification_notes,
                   ur.uploaded_by_user_id, ur.is_locked, ur.uploaded_at as report_uploaded_at,
                   u_up.first_name as uploader_first_name, u_up.last_name as uploader_last_name,
                   r_up.name as uploader_role_name
            FROM tbl_checklist_items ci
            LEFT JOIN tbl_uploaded_reports ur ON ci.id = ur.checklist_item_id AND ur.is_current = TRUE
            LEFT JOIN tbl_users u_up ON ur.uploaded_by_user_id = u_up.id
            LEFT JOIN tbl_roles r_up ON u_up.role_id = r_up.id
            LEFT JOIN tbl_lab_profiles lp ON u_up.id = lp.user_id
            WHERE ci.scheduled_procedure_id = %s
            ORDER BY ci.id
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (scheduled_id,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_active_checklist_items: {err}")
            raise err

    @staticmethod
    def delete_schedule_transaction(schedule_id):
        """Deletes a scheduled procedure and associated checklists cascadedly in a transaction."""
        query = "DELETE FROM tbl_scheduled_procedures WHERE id = %s"
        try:
            with DBTransactionContext() as cursor:
                cursor.execute(query, (schedule_id,))
        except mysql.connector.Error as err:
            logger.error(f"Transaction failed in delete_schedule: {err}")
            raise err

    @staticmethod
    def verify_checklist_item(item_id, doctor_id):
        """Marks a checklist item as verified by doctor/staff."""
        query = """
            UPDATE tbl_checklist_items 
            SET status = 'verified', verified_by_user_id = %s, verified_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (doctor_id, item_id))
                    conn.commit()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in verify_checklist_item: {err}")
            raise err

    @staticmethod
    def update_procedure_readiness(schedule_id, readiness_status, notes):
        """Inserts or updates readiness status cache."""
        query = """
            INSERT INTO tbl_procedure_readiness (scheduled_procedure_id, readiness_status, notes)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                readiness_status = VALUES(readiness_status), 
                notes = VALUES(notes), 
                last_evaluated_at = CURRENT_TIMESTAMP
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (schedule_id, readiness_status, notes))
                    conn.commit()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in update_procedure_readiness: {err}")
            raise err

    @staticmethod
    def get_today_procedures(doctor_id):
        """Retrieves procedures scheduled for the current date."""
        query = """
            SELECT sp.*, u_p.first_name as patient_first_name, u_p.last_name as patient_last_name,
                   p.name as procedure_name, p.code as procedure_code, pr.readiness_status
            FROM tbl_scheduled_procedures sp
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            LEFT JOIN tbl_procedure_readiness pr ON sp.id = pr.scheduled_procedure_id
            WHERE sp.doctor_id = %s AND u_p.is_active = TRUE AND sp.status = 'scheduled' AND DATE(sp.scheduled_at) = CURRENT_DATE()
            ORDER BY sp.scheduled_at ASC
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (doctor_id,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_today_procedures: {err}")
            raise err

    @staticmethod
    def get_recent_uploads(doctor_id):
        """Fetches distinct current official report file uploads for a doctor's patients."""
        query = """
            SELECT ur.*, ci.task_name, sp.id as schedule_id,
                   u_p.first_name as patient_first_name, u_p.last_name as patient_last_name,
                   COALESCE(ur.lab_name, CASE WHEN ur.lab_type = 'external' THEN 'External Laboratory' ELSE 'Hospital Laboratory' END) as display_lab_name,
                   u_up.first_name as uploader_first_name, u_up.last_name as uploader_last_name,
                   r_up.name as uploader_role_name
            FROM tbl_uploaded_reports ur
            JOIN tbl_checklist_items ci ON ur.checklist_item_id = ci.id
            JOIN tbl_scheduled_procedures sp ON ci.scheduled_procedure_id = sp.id
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            LEFT JOIN tbl_users u_up ON ur.uploaded_by_user_id = u_up.id
            LEFT JOIN tbl_roles r_up ON u_up.role_id = r_up.id
            WHERE sp.doctor_id = %s AND u_p.is_active = TRUE AND sp.status = 'scheduled' AND ur.is_current = TRUE
            ORDER BY ur.uploaded_at DESC, ur.id DESC
            LIMIT 5
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (doctor_id,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_recent_uploads: {err}")
            raise err

    @staticmethod
    def get_readiness_distribution(doctor_id):
        """Counts schedules by readiness status color levels."""
        query = """
            SELECT pr.readiness_status, COUNT(sp.id) as count
            FROM tbl_scheduled_procedures sp
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            JOIN tbl_procedure_readiness pr ON sp.id = pr.scheduled_procedure_id
            WHERE sp.doctor_id = %s AND u_p.is_active = TRUE AND sp.status IN ('scheduled', 'delayed')
            GROUP BY pr.readiness_status
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (doctor_id,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_readiness_distribution: {err}")
            raise err

    @staticmethod
    def get_procedure_stats(doctor_id):
        """Counts schedules grouped by procedure definition."""
        query = """
            SELECT p.name as procedure_name, COUNT(sp.id) as count
            FROM tbl_scheduled_procedures sp
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            WHERE sp.doctor_id = %s AND u_p.is_active = TRUE AND sp.status IN ('scheduled', 'delayed')
            GROUP BY p.id, p.name
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (doctor_id,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_procedure_stats: {err}")
            raise err

    @staticmethod
    def save_patient_message(patient_id, doctor_id, schedule_id, message):
        """Saves a message sent from a doctor to a patient for a specific schedule."""
        query = """
            INSERT INTO tbl_notifications (user_id, sender_id, scheduled_procedure_id, title, message, type, status)
            VALUES (%s, %s, %s, 'Clinical Message', %s, 'in_app', 'unread')
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (patient_id, doctor_id, schedule_id, message))
                    conn.commit()
                    return cursor.lastrowid
        except mysql.connector.Error as err:
            logger.error(f"Error saving clinical message: {err}")
            raise err

    @staticmethod
    def get_messages_for_schedule(schedule_id):
        """Fetches messages sent by doctor to patient for a specific scheduled procedure."""
        query = """
            SELECT n.*, u.first_name AS doctor_first_name, u.last_name AS doctor_last_name
            FROM tbl_notifications n
            JOIN tbl_users u ON n.sender_id = u.id
            WHERE n.scheduled_procedure_id = %s
            ORDER BY n.sent_at DESC
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (schedule_id,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"Error fetching schedule messages: {err}")
            return []

    @staticmethod
    def get_unresolved_risk_alerts(doctor_id):
        """Fetches unresolved risk alerts for a doctor's scheduled procedures."""
        query = """
            SELECT ra.*, 
                   u_p.first_name as patient_first_name, u_p.last_name as patient_last_name,
                   p.name as procedure_name, p.code as procedure_code
            FROM tbl_risk_alerts ra
            JOIN tbl_scheduled_procedures sp ON ra.scheduled_procedure_id = sp.id
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            WHERE sp.doctor_id = %s AND u_p.is_active = TRUE AND sp.status = 'scheduled' AND ra.is_resolved = FALSE
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (doctor_id,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_unresolved_risk_alerts: {err}")
            raise err

    @staticmethod
    def update_check_in_status(schedule_id, check_in_status):
        """Updates procedure-day check-in status (scheduled -> arrived -> checked_in -> ready_for_procedure)."""
        query = "UPDATE tbl_scheduled_procedures SET check_in_status = %s WHERE id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (check_in_status, schedule_id))
                    conn.commit()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in update_check_in_status: {err}")
            raise err

    @staticmethod
    def verify_patient_consent(consent_id, doctor_id):
        """Doctor verifies confirmed patient consent form."""
        query = """
            UPDATE tbl_patient_consents 
            SET status = 'verified', verified_by_doctor_id = %s, verified_at = NOW() 
            WHERE id = %s AND status = 'confirmed_locked'
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (doctor_id, consent_id))
                    conn.commit()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in verify_patient_consent: {err}")
            raise err

    @staticmethod
    def get_todays_procedures(doctor_id):
        """Fetches procedure-day board list for a doctor with full readiness & requirement breakdowns."""
        query = """
            SELECT sp.*, 
                   u_p.id as patient_user_id, u_p.first_name as patient_first_name, u_p.last_name as patient_last_name, u_p.email as patient_email,
                   p.name as procedure_name, p.code as procedure_code,
                   pr.readiness_status, pr.notes as readiness_notes,
                   pa.status as assessment_status,
                   pc.status as consent_status
            FROM tbl_scheduled_procedures sp
            JOIN tbl_users u_p ON sp.patient_id = u_p.id
            JOIN tbl_procedures p ON sp.procedure_id = p.id
            LEFT JOIN tbl_procedure_readiness pr ON sp.id = pr.scheduled_procedure_id
            LEFT JOIN tbl_patient_assessments pa ON sp.id = pa.scheduled_procedure_id
            LEFT JOIN tbl_patient_consents pc ON sp.id = pc.scheduled_procedure_id AND pc.is_current = TRUE
            WHERE sp.doctor_id = %s AND u_p.is_active = TRUE AND sp.status = 'scheduled'
            ORDER BY sp.scheduled_at ASC
        """
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (doctor_id,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"DB Error in get_todays_procedures: {err}")
            return []

    @staticmethod
    def get_doctor_specialty(doctor_id):
        """Fetches registered specialty for a physician by user_id."""
        query = "SELECT specialty FROM tbl_doctor_profiles WHERE user_id = %s"
        try:
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (doctor_id,))
                    row = cursor.fetchone()
                    if row and row.get('specialty'):
                        return row['specialty']
        except mysql.connector.Error as err:
            logger.error(f"Error fetching doctor specialty: {err}")
        return ''

