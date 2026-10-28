from app.repositories.doctor_repository import DoctorRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.user_repository import UserRepository
from app.utilities.validators import validate_and_parse_datetime, format_datetime_display, is_specialty_matching
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DoctorService:
    """Coordinates business operations for doctor scheduling actions."""

    @staticmethod
    def get_dashboard_summary(doctor_id):
        """Compiles stats and active worklist for a physician."""
        stats = DoctorRepository.get_dashboard_stats(doctor_id)
        schedules = DoctorRepository.get_schedules_by_doctor(doctor_id)
        
        # Dynamically evaluate and update readiness for active schedules
        from app.services.readiness_service import ReadinessService
        for s in schedules:
            s['formatted_scheduled_at'] = format_datetime_display(s.get('scheduled_at'))
            if s.get('status') in ['scheduled', 'delayed']:
                try:
                    res = ReadinessService.evaluate_and_update_readiness(s['id'])
                    s['readiness_status'] = res['readiness_status']
                except Exception as e:
                    logger.error(f"Readiness evaluation error for schedule {s['id']}: {e}")
                    
        today_procedures = DoctorRepository.get_today_procedures(doctor_id)
        for tp in today_procedures:
            tp['formatted_scheduled_at'] = format_datetime_display(tp.get('scheduled_at'))
            if tp.get('scheduled_at'):
                if hasattr(tp['scheduled_at'], 'strftime'):
                    tp['formatted_time'] = tp['scheduled_at'].strftime('%H:%M')
                else:
                    tp['formatted_time'] = str(tp['scheduled_at']).split(' ')[-1][:5]
            else:
                tp['formatted_time'] = ''

        recent_uploads = DoctorRepository.get_recent_uploads(doctor_id)
        
        # Calculate ready vs pending patients for active scheduled/delayed procedures
        active_schedules = [s for s in schedules if s.get('status') in ['scheduled', 'delayed']]
        ready_count = sum(1 for s in active_schedules if s.get('readiness_status') == 'green')
        pending_count = len(active_schedules) - ready_count
        
        # Calculate average readiness percentage across all scheduled procedures
        total_tasks = 0
        completed_tasks = 0
        for s in schedules:
            checklist = DoctorRepository.get_active_checklist_items(s['id'])
            if checklist:
                total_tasks += len(checklist)
                completed_tasks += sum(1 for c in checklist if c['status'] in ['completed', 'verified'])
        avg_readiness = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 100
        
        # Format stats distribution for Chart.js
        distribution_raw = DoctorRepository.get_readiness_distribution(doctor_id)
        distribution = {'green': 0, 'yellow': 0, 'orange': 0, 'red': 0}
        for d in distribution_raw:
            status = d['readiness_status']
            if status in distribution:
                distribution[status] = d['count']
                
        return {
            'stats': stats,
            'today_procedures': today_procedures,
            'recent_uploads': recent_uploads,
            'ready_count': ready_count,
            'pending_count': pending_count,
            'avg_readiness': avg_readiness,
            'readiness_distribution': distribution,
            'schedules': schedules[:5],  # top 5 upcoming
            'total_schedules_count': len(schedules)
        }

    @staticmethod
    def get_schedules_worklist(doctor_id, search_query=None):
        """Fetches patients worklist with optional search filtering."""
        worklist = DoctorRepository.get_schedules_by_doctor(doctor_id, search_query)
        for s in worklist:
            s['formatted_scheduled_at'] = format_datetime_display(s.get('scheduled_at'))
        return worklist

    @staticmethod
    def get_schedule_details(schedule_id):
        """Fetches detailed properties of a scheduled item."""
        schedule = DoctorRepository.get_schedule_by_id(schedule_id)
        if schedule:
            schedule['formatted_scheduled_at'] = format_datetime_display(schedule.get('scheduled_at'))
        return schedule

    @staticmethod
    def get_scheduling_form_data(doctor_id=None):
        """Fetches patients list, specialty-filtered procedures, and procedure room mappings for select dropdowns."""
        patients = DoctorRepository.get_patients_list()
        procedures = DoctorRepository.get_procedures_list()
        procedure_rooms = DoctorRepository.get_procedure_rooms()
        preparation_rooms = DoctorRepository.get_distinct_rooms('preparation')
        procedure_scanning_rooms = DoctorRepository.get_distinct_rooms('procedure')
        
        if doctor_id:
            doctor_specialty = DoctorRepository.get_doctor_specialty(doctor_id)
            if doctor_specialty:
                procedures = [
                    p for p in procedures 
                    if is_specialty_matching(doctor_specialty, p.get('category', ''))
                ]
            else:
                procedures = []

        return {
            'patients': patients,
            'procedures': procedures,
            'procedure_rooms': procedure_rooms,
            'preparation_rooms': preparation_rooms,
            'procedure_scanning_rooms': procedure_scanning_rooms
        }

    @staticmethod
    def check_duplicate_booking(patient_id, procedure_id, scheduled_at_str, exclude_schedule_id=None):
        """
        Checks if an active booking already exists for this patient and procedure across all doctors.
        Returns a tuple: (is_duplicate: bool, message: str, existing_booking: dict or None)
        """
        scheduled_at = validate_and_parse_datetime(scheduled_at_str)
        dup = DoctorRepository.find_duplicate_schedule(patient_id, procedure_id, scheduled_at, exclude_schedule_id)
        if dup:
            proc_name = dup.get('procedure_name', 'Procedure')
            proc_code = dup.get('procedure_code', '')
            ex_sched_dt = dup.get('scheduled_at')
            from app.utilities.validators import format_datetime_display
            ex_time_str = format_datetime_display(ex_sched_dt) if ex_sched_dt else str(ex_sched_dt)
            doc_name = f"Dr. {dup['doctor_first_name']} {dup['doctor_last_name']}" if dup.get('doctor_first_name') else f"Doctor ID {dup.get('doctor_id')}"
            
            if dup.get('is_exact_time_match'):
                msg = f"Duplicate booking skipped: Patient already has an active booking for '{proc_name}' ({proc_code}) at the same scheduled time ({ex_time_str}) with {doc_name}."
            else:
                msg = f"Duplicate booking skipped: Patient already has an active booking for '{proc_name}' ({proc_code}) scheduled at {ex_time_str} with {doc_name}."
            return True, msg, dup
        return False, "", None

    @staticmethod
    def schedule_new_procedure_custom(patient_id, doctor_id, procedure_id, scheduled_at_str, preparation_room, procedure_room, custom_checklist=None):
        """
        Validates inputs and saves the new procedure with doctor-customized or procedure default checklist items.
        """
        # Specialty suitability validation
        doctor_specialty = DoctorRepository.get_doctor_specialty(doctor_id)
        procedure = next((p for p in DoctorRepository.get_procedures_list() if p['id'] == procedure_id), None)
        if not procedure or not is_specialty_matching(doctor_specialty, procedure.get('category', '')):
            raise ValueError("This procedure is not available for your registered specialty.")

        scheduled_at = validate_and_parse_datetime(scheduled_at_str)

        if scheduled_at < datetime.now() + timedelta(hours=24):
            raise ValueError("Procedures must be scheduled at least 24 hours in advance.")

        if not preparation_room or not str(preparation_room).strip():
            raise ValueError("Preparation Room is required. Please select a valid preparation room.")

        if not procedure_room or not str(procedure_room).strip():
            raise ValueError("Procedure / Scanning Room is required. Please select a valid procedure room.")

        # Resolve room names if numeric ID was passed
        preparation_room = DoctorRepository.resolve_room_name(preparation_room, procedure_id, 'preparation')
        procedure_room = DoctorRepository.resolve_room_name(procedure_room, procedure_id, 'procedure')

        # Room suitability validation
        rooms_map = DoctorRepository.get_procedure_rooms()
        p_key = str(procedure_id)
        if p_key in rooms_map:
            allowed_prep = rooms_map[p_key].get('preparation', [])
            allowed_proc = rooms_map[p_key].get('procedure', [])
            if allowed_prep and preparation_room not in allowed_prep:
                raise ValueError(f"Selected Preparation Room '{preparation_room}' is not valid for this procedure.")
            if allowed_proc and procedure_room not in allowed_proc:
                raise ValueError(f"Selected Procedure / Scanning Room '{procedure_room}' is not valid for this procedure.")

        # 1. Validate registered patient
        patient_user = UserRepository.find_by_id(patient_id)
        if not patient_user or patient_user.get('role_name') != 'patient' or not patient_user.get('is_active'):
            raise ValueError("The selected patient is invalid or not registered in the system.")

        # 2. Prevent duplicate scheduling of the same procedure for the same patient across all doctors
        is_dup, dup_msg, _ = DoctorService.check_duplicate_booking(patient_id, procedure_id, scheduled_at_str)
        if is_dup:
            raise ValueError(dup_msg)

        # 3. Build checklist items from customized details or procedure catalog defaults
        checklist_items = []
        if custom_checklist:
            for c in custom_checklist:
                due_days = int(c.get('due_days_before', 0))
                due_by = scheduled_at - timedelta(days=due_days)
                checklist_items.append({
                    'task_name': c['task_name'],
                    'task_type': c['task_type'],
                    'description': c.get('description', ''),
                    'due_by_datetime': due_by.strftime("%Y-%m-%d %H:%M:%S"),
                    'is_critical': bool(c.get('is_critical', False))
                })
        else:
            templates = DoctorRepository.get_checklist_templates(procedure_id)
            for t in templates:
                due_days = int(t.get('due_days_before', 0))
                due_by = scheduled_at - timedelta(days=due_days)
                checklist_items.append({
                    'task_name': t['task_name'],
                    'task_type': t['task_type'],
                    'description': t.get('description', ''),
                    'due_by_datetime': due_by.strftime("%Y-%m-%d %H:%M:%S"),
                    'is_critical': bool(t.get('is_critical', False))
                })

        return DoctorRepository.create_schedule_transaction(
            patient_id=patient_id,
            doctor_id=doctor_id,
            procedure_id=procedure_id,
            scheduled_at=scheduled_at.strftime("%Y-%m-%d %H:%M:%S"),
            preparation_room=preparation_room.strip(),
            procedure_room=procedure_room.strip(),
            checklist_items=checklist_items
        )

    @staticmethod
    def update_procedure_schedule_custom(schedule_id, patient_id, procedure_id, scheduled_at_str, preparation_room, procedure_room, status, rebuild_checklist=False, custom_checklist=None):
        """Updates schedule, optionally rebuilding checklist items from custom physician inputs."""
        schedule_info = DoctorRepository.get_schedule_by_id(schedule_id)
        doctor_id = schedule_info['doctor_id'] if schedule_info else None
        if doctor_id:
            doctor_specialty = DoctorRepository.get_doctor_specialty(doctor_id)
            procedure = next((p for p in DoctorRepository.get_procedures_list() if p['id'] == procedure_id), None)
            if not procedure or not is_specialty_matching(doctor_specialty, procedure.get('category', '')):
                raise ValueError("This procedure is not available for your registered specialty.")

        scheduled_at = validate_and_parse_datetime(scheduled_at_str)

        # Enforce 24 hours advance notice when scheduling or rescheduling
        orig_sched_at = schedule_info.get('scheduled_at') if schedule_info else None
        if status == 'scheduled' and scheduled_at != orig_sched_at:
            if scheduled_at < datetime.now() + timedelta(hours=24):
                raise ValueError("Procedures must be scheduled at least 24 hours in advance.")

        if not preparation_room or not str(preparation_room).strip():
            raise ValueError("Preparation Room is required. Please select a valid preparation room.")

        if not procedure_room or not str(procedure_room).strip():
            raise ValueError("Procedure / Scanning Room is required. Please select a valid procedure room.")

        # Resolve room names if numeric ID was passed
        preparation_room = DoctorRepository.resolve_room_name(preparation_room, procedure_id, 'preparation')
        procedure_room = DoctorRepository.resolve_room_name(procedure_room, procedure_id, 'procedure')

        # Room suitability validation
        rooms_map = DoctorRepository.get_procedure_rooms()
        p_key = str(procedure_id)
        if p_key in rooms_map:
            allowed_prep = rooms_map[p_key].get('preparation', [])
            allowed_proc = rooms_map[p_key].get('procedure', [])
            if allowed_prep and preparation_room not in allowed_prep:
                raise ValueError(f"Selected Preparation Room '{preparation_room}' is not valid for this procedure.")
            if allowed_proc and procedure_room not in allowed_proc:
                raise ValueError(f"Selected Procedure / Scanning Room '{procedure_room}' is not valid for this procedure.")

        # Prevent duplicate scheduling when updating schedule
        if status in ['scheduled', 'delayed']:
            is_dup, dup_msg, _ = DoctorService.check_duplicate_booking(patient_id, procedure_id, scheduled_at_str, exclude_schedule_id=schedule_id)
            if is_dup:
                raise ValueError(dup_msg)

        checklist_items = []
        if rebuild_checklist and custom_checklist:
            for c in custom_checklist:
                due_days = int(c.get('due_days_before', 0))
                due_by = scheduled_at - timedelta(days=due_days)
                checklist_items.append({
                    'task_name': c['task_name'],
                    'task_type': c['task_type'],
                    'description': c.get('description', ''),
                    'due_by_datetime': due_by.strftime("%Y-%m-%d %H:%M:%S"),
                    'is_critical': bool(c.get('is_critical', False))
                })

        DoctorRepository.update_schedule_transaction(
            schedule_id=schedule_id,
            patient_id=patient_id,
            procedure_id=procedure_id,
            scheduled_at=scheduled_at.strftime("%Y-%m-%d %H:%M:%S"),
            preparation_room=preparation_room.strip(),
            procedure_room=procedure_room.strip(),
            status=status,
            rebuild_checklist=rebuild_checklist,
            checklist_items=checklist_items if rebuild_checklist else None
        )

    @staticmethod
    def cancel_procedure_schedule(schedule_id):
        """Cancels/deletes scheduling row cascadedly."""
        DoctorRepository.delete_schedule_transaction(schedule_id)

    @staticmethod
    def evaluate_and_verify_checklist_item(item_id, schedule_id, doctor_id):
        """Verifies a checklist item and recomputes the overall procedure readiness status."""
        # 1. Verify checklist item
        DoctorRepository.verify_checklist_item(item_id, doctor_id)
        
        # 2. Trigger Readiness Engine evaluation
        from app.services.readiness_service import ReadinessService
        res = ReadinessService.evaluate_and_update_readiness(schedule_id)
        return res['readiness_status']

    @staticmethod
    def send_patient_message(schedule_id, doctor_id, message):
        """Validates schedule and saves a clinical message for the patient."""
        if not message or not message.strip():
            raise ValueError("Message content cannot be empty.")
            
        schedule = DoctorRepository.get_schedule_by_id(schedule_id)
        if not schedule:
            raise ValueError("Scheduled procedure not found.")
            
        if schedule['doctor_id'] != doctor_id:
            raise PermissionError("You are not authorized to send messages for this schedule.")
            
        patient_id = schedule['patient_id']
        DoctorRepository.save_patient_message(patient_id, doctor_id, schedule_id, message.strip())

    @staticmethod
    def get_messages_for_schedule(schedule_id):
        """Fetches messages sent by doctor to patient for a specific scheduled procedure."""
        return DoctorRepository.get_messages_for_schedule(schedule_id)
