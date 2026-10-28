from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from app.repositories.admin_repository import AdminRepository
from app.repositories.user_repository import UserRepository
from app.utilities.decorators import login_required, role_required
from app.utilities.validators import (
    validate_email, 
    validate_phone, 
    validate_password_strength, 
    validate_indian_mobile, 
    validate_date_of_birth
)
import bcrypt
import logging

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """Renders the admin metadata analytics panel."""
    stats = AdminRepository.get_admin_stats()
    upcoming = AdminRepository.get_upcoming_procedures(limit=5)
    
    # Format dates for presentation
    from app.utilities.validators import format_datetime_display
    for item in upcoming:
        dt = item.get('scheduled_at')
        item['formatted_scheduled_at'] = format_datetime_display(dt)

    return render_template('admin/dashboard.html', stats=stats, upcoming=upcoming)

# ==========================================
# DOCTORS MANAGEMENT CRUD
# ==========================================

@admin_bp.route('/doctors', methods=['GET'])
@login_required
@role_required('admin')
def doctors():
    """Lists and searches doctors registered in the system."""
    search_query = request.args.get('search', '').strip()
    doc_list = AdminRepository.get_all_doctors(search_query)
    return render_template('admin/doctors.html', doctors=doc_list, search=search_query)

@admin_bp.route('/doctors/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_doctor():
    """Form and action for adding a new clinician profile."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone_raw = request.form.get('phone', '').strip()
        
        license_number = request.form.get('license_number', '').strip()
        specialty = request.form.get('specialty', '').strip()
        department = request.form.get('department', '').strip()
        
        if not all([username, email, password, first_name, last_name, license_number, specialty, department]):
            flash("All fields are required to register a doctor profile.", "danger")
            return render_template('admin/doctor_form.html', action="Add", doc=request.form)
            
        if not validate_email(email):
            flash("Invalid email address format.", "danger")
            return render_template('admin/doctor_form.html', action="Add", doc=request.form)

        if not validate_password_strength(password):
            flash("Password must contain at least 8 characters and no spaces.", "danger")
            return render_template('admin/doctor_form.html', action="Add", doc=request.form)
            
        phone = None
        if phone_raw:
            is_valid_phone, clean_phone = validate_indian_mobile(phone_raw)
            if not is_valid_phone:
                flash("Invalid phone number format. Please enter a valid 10-digit Indian mobile number.", "danger")
                return render_template('admin/doctor_form.html', action="Add", doc=request.form)
            phone = clean_phone

        if UserRepository.username_exists(username):
            flash("Username already exists. Please choose a different username.", "danger")
            return render_template('admin/doctor_form.html', action="Add", doc=request.form)

        if UserRepository.email_exists(email):
            flash("Email address is already registered.", "danger")
            return render_template('admin/doctor_form.html', action="Add", doc=request.form)

        if AdminRepository.license_exists(license_number):
            flash("Medical license code is already registered to another clinician.", "danger")
            return render_template('admin/doctor_form.html', action="Add", doc=request.form)
            
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone
        }
        
        doc_data = {
            'license_number': license_number,
            'specialty': specialty,
            'department': department
        }
        
        try:
            new_doc_id = AdminRepository.create_doctor_transaction(user_data, doc_data)
            flash(f"Doctor account 'Dr. {first_name} {last_name}' created successfully.", "success")
            try:
                from app.repositories.audit_repository import AuditRepository
                AuditRepository.log_audit_action(
                    user_id=session.get('user_id'),
                    role_name='admin',
                    action='CREATE_DOCTOR',
                    details=f"Doctor account '{username}' (ID {new_doc_id}) created by admin."
                )
            except Exception as audit_err:
                logger.warning(f"Failed to record audit log for doctor creation: {audit_err}")

            return redirect(url_for('admin.doctors'))
        except Exception as e:
            logger.error(f"Error registering doctor: {e}")
            flash("Failed to register doctor. Ensure username, email, and license are unique.", "danger")
            
    return render_template('admin/doctor_form.html', action="Add", doc={})

@admin_bp.route('/doctors/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_doctor(id):
    """Edits clinical details and account details of a doctor."""
    doc = AdminRepository.get_doctor_by_id(id)
    if not doc:
        abort(404)
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone_raw = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        
        license_number = request.form.get('license_number', '').strip()
        specialty = request.form.get('specialty', '').strip()
        department = request.form.get('department', '').strip()

        # Preserve form data including username for re-rendering
        preserved = dict(request.form)
        preserved['username'] = doc.get('username', '')
        
        if not all([email, first_name, last_name, license_number, specialty, department]):
            flash("All fields except phone number and password are required.", "danger")
            return render_template('admin/doctor_form.html', action="Edit", doc=preserved, id=id)
            
        if not validate_email(email):
            flash("Invalid email address format.", "danger")
            return render_template('admin/doctor_form.html', action="Edit", doc=preserved, id=id)

        phone = None
        if phone_raw:
            is_valid_phone, clean_phone = validate_indian_mobile(phone_raw)
            if not is_valid_phone:
                flash("Invalid phone number format. Please enter a valid 10-digit Indian mobile number.", "danger")
                return render_template('admin/doctor_form.html', action="Edit", doc=preserved, id=id)
            phone = clean_phone

        # Check email uniqueness against other users
        if AdminRepository.email_exists_for_other(email, exclude_user_id=id):
            flash("Email address is already in use by another user account.", "danger")
            return render_template('admin/doctor_form.html', action="Edit", doc=preserved, id=id)

        # Check license uniqueness against other doctors
        if AdminRepository.license_exists_for_other(license_number, exclude_user_id=id):
            flash("Medical license code is already registered to another clinician.", "danger")
            return render_template('admin/doctor_form.html', action="Edit", doc=preserved, id=id)
            
        user_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone
        }

        # Optional password update
        if password:
            if not validate_password_strength(password):
                flash("Password must contain at least 8 characters and no spaces.", "danger")
                return render_template('admin/doctor_form.html', action="Edit", doc=preserved, id=id)
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
            user_data['password_hash'] = password_hash
        
        doc_data = {
            'license_number': license_number,
            'specialty': specialty,
            'department': department
        }
        
        try:
            AdminRepository.update_doctor_transaction(id, user_data, doc_data)
            flash(f"Clinician Dr. {first_name} {last_name} profile updated successfully.", "success")
            try:
                from app.repositories.audit_repository import AuditRepository
                AuditRepository.log_audit_action(
                    user_id=session.get('user_id'),
                    role_name='admin',
                    action='UPDATE_DOCTOR',
                    details=f"Doctor account ID {id} was updated by admin."
                )
            except Exception as audit_err:
                logger.warning(f"Failed to record audit log for doctor update: {audit_err}")

            return redirect(url_for('admin.doctors'))
        except Exception as e:
            logger.error(f"Error updating doctor: {e}")
            flash("Failed to update profile details. Please verify the information provided.", "danger")
            return render_template('admin/doctor_form.html', action="Edit", doc=preserved, id=id)
            
    return render_template('admin/doctor_form.html', action="Edit", doc=doc, id=id)

@admin_bp.route('/doctors/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_doctor(id):
    """Deletes doctor profile or safely deactivates if clinical records exist."""
    current_admin_id = session.get('user_id')
    if current_admin_id == id:
        flash("You cannot delete your own administrator account.", "danger")
        return redirect(url_for('admin.doctors'))

    try:
        action, msg = AdminRepository.delete_doctor(id)
        if action in ('deleted', 'deactivated'):
            flash(msg, "success")
            try:
                from app.repositories.audit_repository import AuditRepository
                audit_action = 'DEACTIVATE_DOCTOR' if action == 'deactivated' else 'DELETE_DOCTOR'
                AuditRepository.log_audit_action(
                    user_id=current_admin_id,
                    role_name='admin',
                    action=audit_action,
                    details=f"Doctor account ID {id} was {action} by admin."
                )
            except Exception as audit_err:
                logger.warning(f"Failed to record audit log for doctor deletion: {audit_err}")
        elif action == 'not_found':
            flash(msg, "danger")
        else:
            flash(msg, "warning")
    except Exception as e:
        logger.error(f"Failed to delete doctor: {e}")
        flash(f"Failed to delete user account: {str(e)}", "danger")
    return redirect(url_for('admin.doctors'))

# ==========================================
# PATIENTS MANAGEMENT CRUD
# ==========================================

@admin_bp.route('/patients', methods=['GET'])
@login_required
@role_required('admin')
def patients():
    """Lists and searches patient demographics registered."""
    search_query = request.args.get('search', '').strip()
    pat_list = AdminRepository.get_all_patients(search_query)
    return render_template('admin/patients.html', patients=pat_list, search=search_query)

@admin_bp.route('/patients/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_patient():
    """Form and action for adding a new patient account."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone_raw = request.form.get('phone', '').strip()
        
        date_of_birth = request.form.get('date_of_birth', '').strip()
        gender = request.form.get('gender', 'male')
        blood_type = request.form.get('blood_type', '').strip() or None
        medical_history = request.form.get('medical_history', '').strip() or None
        emergency_contact_name = request.form.get('emergency_contact_name', '').strip()
        emergency_contact_phone = request.form.get('emergency_contact_phone', '').strip()
        
        if not all([username, email, password, first_name, last_name, date_of_birth]):
            flash("Username, email, password, first name, last name, and date of birth are required.", "danger")
            return render_template('admin/patient_form.html', action="Add", pat=request.form)
            
        if not validate_email(email):
            flash("Invalid email address format.", "danger")
            return render_template('admin/patient_form.html', action="Add", pat=request.form)
            
        if not validate_password_strength(password):
            flash("Password must contain at least 8 characters and no spaces.", "danger")
            return render_template('admin/patient_form.html', action="Add", pat=request.form)
            
        is_dob_valid, dob_err, normalized_dob = validate_date_of_birth(date_of_birth)
        if not is_dob_valid:
            flash(dob_err or "Invalid date of birth. Must be a date earlier than today.", "danger")
            return render_template('admin/patient_form.html', action="Add", pat=request.form)
        date_of_birth = normalized_dob
        
        phone = None
        if phone_raw:
            is_valid_phone, clean_phone = validate_indian_mobile(phone_raw)
            if not is_valid_phone:
                flash("Invalid phone number format. Please enter a valid 10-digit Indian mobile number.", "danger")
                return render_template('admin/patient_form.html', action="Add", pat=request.form)
            phone = clean_phone
            
        # Emergency contact defaults to satisfy NOT NULL constraints in DB
        if not emergency_contact_name:
            emergency_contact_name = f"{first_name} {last_name}"
        if not emergency_contact_phone:
            emergency_contact_phone = phone or "0000000000"
        else:
            is_valid_em, clean_em = validate_indian_mobile(emergency_contact_phone)
            if is_valid_em:
                emergency_contact_phone = clean_em

        if UserRepository.username_exists(username):
            flash("Username already exists. Please choose a different username.", "danger")
            return render_template('admin/patient_form.html', action="Add", pat=request.form)
            
        if UserRepository.email_exists(email):
            flash("Email address is already registered.", "danger")
            return render_template('admin/patient_form.html', action="Add", pat=request.form)
            
        # Hash password using bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone
        }
        
        pat_data = {
            'date_of_birth': date_of_birth,
            'gender': gender,
            'blood_type': blood_type,
            'medical_history': medical_history,
            'emergency_contact_name': emergency_contact_name,
            'emergency_contact_phone': emergency_contact_phone
        }
        
        try:
            new_patient_id = AdminRepository.create_patient_transaction(user_data, pat_data)
            flash(f"Patient account '{username}' created successfully.", "success")
            try:
                from app.repositories.audit_repository import AuditRepository
                current_admin_id = session.get('user_id')
                AuditRepository.log_audit_action(
                    user_id=current_admin_id,
                    role_name='admin',
                    action='CREATE_PATIENT',
                    details=f"Patient account '{username}' (ID {new_patient_id}) created by admin.",
                    patient_id=new_patient_id
                )
            except Exception as audit_err:
                logger.warning(f"Failed to record audit log for patient creation: {audit_err}")
                
            return redirect(url_for('admin.patients'))
        except Exception as e:
            logger.error(f"Error registering patient: {e}")
            flash("Failed to register patient account. Please ensure unique credentials.", "danger")
            
    return render_template('admin/patient_form.html', action="Add", pat={})

@admin_bp.route('/patients/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_patient(id):
    """Edits patient core metadata and clinical background."""
    pat = AdminRepository.get_patient_by_id(id)
    if not pat:
        abort(404)
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip() or None
        
        date_of_birth = request.form.get('date_of_birth', '')
        gender = request.form.get('gender', 'male')
        blood_type = request.form.get('blood_type', '').strip() or None
        medical_history = request.form.get('medical_history', '').strip() or None
        emergency_contact_name = request.form.get('emergency_contact_name', '').strip()
        emergency_contact_phone = request.form.get('emergency_contact_phone', '').strip()
        
        if not all([email, first_name, last_name, date_of_birth, emergency_contact_name, emergency_contact_phone]):
            flash("Required patient fields are missing.", "danger")
            return render_template('admin/patient_form.html', action="Edit", pat=request.form, id=id)
            
        user_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone
        }
        
        pat_data = {
            'date_of_birth': date_of_birth,
            'gender': gender,
            'blood_type': blood_type,
            'medical_history': medical_history,
            'emergency_contact_name': emergency_contact_name,
            'emergency_contact_phone': emergency_contact_phone
        }
        
        try:
            AdminRepository.update_patient_transaction(id, user_data, pat_data)
            flash("Patient demographic file updated successfully.", "success")
            return redirect(url_for('admin.patients'))
        except Exception as e:
            logger.error(f"Error updating patient: {e}")
            flash("Failed to update patient details.", "danger")
            
    return render_template('admin/patient_form.html', action="Edit", pat=pat, id=id)

@admin_bp.route('/patients/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_patient(id):
    """Deletes patient account or safely deactivates if clinical records exist."""
    current_admin_id = session.get('user_id')
    if current_admin_id == id:
        flash("You cannot delete your own administrator account.", "danger")
        return redirect(url_for('admin.patients'))

    try:
        action, msg = AdminRepository.delete_patient(id)
        if action in ('deleted', 'deactivated'):
            flash(msg, "success")
            try:
                from app.repositories.audit_repository import AuditRepository
                audit_action = 'DEACTIVATE_PATIENT' if action == 'deactivated' else 'DELETE_PATIENT'
                AuditRepository.log_audit_action(
                    user_id=current_admin_id,
                    role_name='admin',
                    action=audit_action,
                    details=f"Patient account ID {id} was {action} by admin.",
                    patient_id=id
                )
            except Exception as audit_err:
                logger.warning(f"Failed to record audit log for patient deletion: {audit_err}")
        elif action == 'not_found':
            flash(msg, "danger")
        else:
            flash(msg, "warning")
    except Exception as e:
        logger.error(f"Failed to delete patient: {e}")
        flash(f"Failed to delete user account: {str(e)}", "danger")
    return redirect(url_for('admin.patients'))

# ==========================================
# PROCEDURES CATALOG CRUD
# ==========================================

@admin_bp.route('/procedures', methods=['GET'])
@login_required
@role_required('admin')
def procedures():
    """Lists and searches procedure catalogs templates."""
    search_query = request.args.get('search', '').strip()
    proc_list = AdminRepository.get_all_procedures(search_query)
    return render_template('admin/procedures.html', procedures=proc_list, search=search_query)

@admin_bp.route('/procedures/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_procedure():
    """Adds a new predefined surgery type definition."""
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        est_duration_mins = request.form.get('est_duration_mins', '60')
        
        if not all([code, name, category]):
            flash("Code, Name, and Category fields are required.", "danger")
            return render_template('admin/procedure_form.html', action="Add", proc=request.form)
            
        existing_proc = AdminRepository.get_procedure_by_code(code)
        if existing_proc:
            flash(f"Procedure with code '{code}' already exists in catalog ('{existing_proc['name']}', ID: {existing_proc['id']}). Please reuse the existing catalog entry.", "warning")
            return render_template('admin/procedure_form.html', action="Add", proc=request.form)

        proc_data = {
            'code': code,
            'name': name,
            'category': category,
            'description': description,
            'est_duration_mins': int(est_duration_mins) if est_duration_mins.isdigit() else 60
        }
        
        try:
            AdminRepository.create_procedure(proc_data)
            flash("Procedure catalog template created successfully.", "success")
            return redirect(url_for('admin.procedures'))
        except Exception as e:
            logger.error(f"Error creating procedure: {e}")
            flash("Failed to save template. Ensure the CPT code is unique.", "danger")
            
    return render_template('admin/procedure_form.html', action="Add", proc={})

@admin_bp.route('/procedures/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_procedure(id):
    """Edits predefined surgery catalog parameters."""
    proc = AdminRepository.get_procedure_by_id(id)
    if not proc:
        abort(404)
        
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        est_duration_mins = request.form.get('est_duration_mins', '60')
        
        if not all([code, name, category]):
            flash("Code, Name, and Category fields are required.", "danger")
            return render_template('admin/procedure_form.html', action="Edit", proc=request.form, id=id)
            
        existing_proc = AdminRepository.get_procedure_by_code(code)
        if existing_proc and existing_proc['id'] != id:
            flash(f"Another procedure with code '{code}' already exists in catalog ('{existing_proc['name']}', ID: {existing_proc['id']}). Duplicate catalog entries are not permitted.", "danger")
            return render_template('admin/procedure_form.html', action="Edit", proc=request.form, id=id)

        proc_data = {
            'code': code,
            'name': name,
            'category': category,
            'description': description,
            'est_duration_mins': int(est_duration_mins) if est_duration_mins.isdigit() else 60
        }
        
        try:
            AdminRepository.update_procedure(id, proc_data)
            flash("Procedure definition updated successfully.", "success")
            return redirect(url_for('admin.procedures'))
        except Exception as e:
            logger.error(f"Error updating procedure: {e}")
            flash("Failed to update procedure definition.", "danger")
            
    return render_template('admin/procedure_form.html', action="Edit", proc=proc, id=id)

@admin_bp.route('/procedures/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_procedure(id):
    """Deletes procedure category from active definitions."""
    try:
        AdminRepository.delete_procedure(id)
        flash("Procedure category deleted from catalog.", "success")
    except Exception as e:
        logger.error(f"Failed to delete procedure: {e}")
        flash("Failed to delete procedure. (Note: active scheduled surgeries prevent deletion).", "danger")
    return redirect(url_for('admin.procedures'))
