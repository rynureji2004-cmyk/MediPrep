class Procedure:
    """Procedure metadata catalog representation."""
    def __init__(self, id=None, code=None, name=None, description=None, category=None, est_duration_mins=60):
        self.id = id
        self.code = code
        self.name = name
        self.description = description
        self.category = category
        self.est_duration_mins = est_duration_mins

class ScheduledProcedure:
    """A scheduled procedure instance for a patient attended by a doctor."""
    def __init__(self, id=None, patient_id=None, doctor_id=None, procedure_id=None, 
                 scheduled_at=None, location=None, status='scheduled', created_at=None):
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.procedure_id = procedure_id
        self.scheduled_at = scheduled_at
        self.location = location
        self.status = status
        self.created_at = created_at
