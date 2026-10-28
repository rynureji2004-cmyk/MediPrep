class User:
    """User data object mapping fields to the database 'tbl_users' table."""
    def __init__(self, id=None, role_id=None, username=None, email=None, password_hash=None, 
                 first_name=None, last_name=None, phone=None, is_active=True, created_at=None):
        self.id = id
        self.role_id = role_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.is_active = is_active
        self.created_at = created_at

class DoctorProfile:
    """Doctor details mapping fields to the 'tbl_doctor_profiles' table."""
    def __init__(self, id=None, user_id=None, license_number=None, specialty=None, department=None):
        self.id = id
        self.user_id = user_id
        self.license_number = license_number
        self.specialty = specialty
        self.department = department

class PatientProfile:
    """Patient clinical detail mapping fields to 'tbl_patient_profiles' table."""
    def __init__(self, id=None, user_id=None, date_of_birth=None, gender=None, 
                 blood_type=None, medical_history=None, emergency_contact_name=None, emergency_contact_phone=None):
        self.id = id
        self.user_id = user_id
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.blood_type = blood_type
        self.medical_history = medical_history
        self.emergency_contact_name = emergency_contact_name
        self.emergency_contact_phone = emergency_contact_phone

class LabProfile:
    """Laboratory details mapping fields to 'tbl_lab_profiles' table."""
    def __init__(self, id=None, user_id=None, lab_name=None, lab_type='hospital', license_number=None, accreditation=None):
        self.id = id
        self.user_id = user_id
        self.lab_name = lab_name
        self.lab_type = lab_type
        self.license_number = license_number
        self.accreditation = accreditation

