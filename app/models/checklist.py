class ChecklistItem:
    """A single task checklist item mapped to the 'tbl_checklist_items' table."""
    def __init__(self, id=None, scheduled_procedure_id=None, task_name=None, task_type=None, 
                 description=None, due_by_datetime=None, is_critical=False, status='pending', 
                 completed_by_user_id=None, completed_at=None, verified_by_user_id=None, verified_at=None, notes=None):
        self.id = id
        self.scheduled_procedure_id = scheduled_procedure_id
        self.task_name = task_name
        self.task_type = task_type
        self.description = description
        self.due_by_datetime = due_by_datetime
        self.is_critical = is_critical
        self.status = status
        self.completed_by_user_id = completed_by_user_id
        self.completed_at = completed_at
        self.verified_by_user_id = verified_by_user_id
        self.verified_at = verified_at
        self.notes = notes

class UploadedReport:
    """Document upload metadata linking a patient file to a checklist task."""
    def __init__(self, id=None, checklist_item_id=None, file_name=None, file_path=None, file_size_bytes=None, uploaded_at=None):
        self.id = id
        self.checklist_item_id = checklist_item_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_size_bytes = file_size_bytes
        self.uploaded_at = uploaded_at

class ProcedureReadiness:
    """Evaluated readiness cache values for scheduling cards."""
    def __init__(self, id=None, scheduled_procedure_id=None, readiness_status='red', evaluated_by_user_id=None, last_evaluated_at=None, notes=None, override_reason=None):
        self.id = id
        self.scheduled_procedure_id = scheduled_procedure_id
        self.readiness_status = readiness_status
        self.evaluated_by_user_id = evaluated_by_user_id
        self.last_evaluated_at = last_evaluated_at
        self.notes = notes
        self.override_reason = override_reason

class HealthSuggestion:
    """Health information text mapped to procedure types."""
    def __init__(self, id=None, procedure_id=None, suggestion_text=None, trigger_condition='all', created_at=None):
        self.id = id
        self.procedure_id = procedure_id
        self.suggestion_text = suggestion_text
        self.trigger_condition = trigger_condition
        self.created_at = created_at

class RiskAlert:
    """Active pre-op warnings triggers."""
    def __init__(self, id=None, scheduled_procedure_id=None, alert_type=None, alert_message=None, severity='medium', is_resolved=False, resolved_by_user_id=None, resolved_at=None, created_at=None):
        self.id = id
        self.scheduled_procedure_id = scheduled_procedure_id
        self.alert_type = alert_type
        self.alert_message = alert_message
        self.severity = severity
        self.is_resolved = is_resolved
        self.resolved_by_user_id = resolved_by_user_id
        self.resolved_at = resolved_at
        self.created_at = created_at

class Notification:
    """A message log entry mapped to the 'tbl_notifications' table for users inbox."""
    def __init__(self, id=None, user_id=None, title=None, message=None, type='in_app', status='unread', sent_at=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.type = type
        self.status = status
        self.sent_at = sent_at
