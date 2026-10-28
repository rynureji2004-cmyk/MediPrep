from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.utilities.validators import validate_email, validate_password_strength, validate_phone, validate_indian_mobile, validate_date_of_birth

auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Renders login view and handles user session authentication."""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')

        # Basic verification
        if not username_or_email or not password:
            flash("Please enter both username/email and password.", "danger")
            return render_template('auth/login.html')

        user = UserService.authenticate_user(username_or_email, password)
        if user:
            if user['role_name'] == 'external_lab_tech':
                flash("External Laboratory login is not required or supported. External reports are uploaded directly by attending doctors upon receipt from patients.", "warning")
                return render_template('auth/login.html')

            # Set Session Values
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            session['role_name'] = user['role_name']
            
            flash(f"Welcome back, {user['first_name']}! Logged in successfully.", "success")
            return redirect(url_for('dashboard.index'))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Renders registration form and saves new user accounts."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone_raw = request.form.get('phone', '').strip()
        role_name = request.form.get('role_name', 'patient')

        errors = {}

        # 1. Core Validations
        if not username:
            errors['username'] = "Username is required."
        if not email:
            errors['email'] = "Email address is required."
        if not first_name:
            errors['first_name'] = "First name is required."
        if not last_name:
            errors['last_name'] = "Last name is required."

        if not password:
            errors['password'] = "Password is required."
        elif not validate_password_strength(password):
            errors['password'] = "Password must contain at least 8 characters."

        if not confirm_password:
            errors['confirm_password'] = "Confirm your password."
        elif password and password != confirm_password:
            errors['confirm_password'] = "Passwords do not match."

        if email and 'email' not in errors and not validate_email(email):
            errors['email'] = "Please enter a valid email address."

        phone = None
        if phone_raw:
            is_valid_phone, clean_phone = validate_indian_mobile(phone_raw)
            if not is_valid_phone:
                errors['phone'] = "Enter a valid 10-digit Indian mobile number."
            else:
                phone = clean_phone

        # 2. Role-specific profile fields
        profile_data = {}
        if role_name == 'doctor':
            license_number = request.form.get('license_number', '').strip()
            specialty = request.form.get('specialty', '').strip()
            department = request.form.get('department', '').strip()
            
            allowed_specializations = [
                "Cardiology", "Neurology", "Orthopedics", "Gastroenterology",
                "General Medicine", "General Surgery", "Pulmonology", "Nephrology",
                "Urology", "Dermatology", "Pediatrics", "Obstetrics & Gynecology",
                "Oncology", "Radiology", "Anesthesiology"
            ]
            
            allowed_departments = [
                "Cardiology Department", "Neurology Department", "Orthopedics Department", "Gastroenterology Department",
                "General Medicine Department", "General Surgery Department", "Pulmonology Department", "Nephrology Department",
                "Urology Department", "Dermatology Department", "Pediatrics Department", "Obstetrics & Gynecology Department",
                "Oncology Department", "Radiology Department", "Anesthesiology Department"
            ]
            
            if not license_number:
                errors['license_number'] = "Medical license code is required."
            if not specialty or specialty not in allowed_specializations:
                errors['specialty'] = "Please select a specialization."
            if not department or department not in allowed_departments:
                errors['department'] = "Please select a medical department."
                
            profile_data = {
                'license_number': license_number,
                'specialty': specialty,
                'department': department
            }
        elif role_name == 'patient':
            date_of_birth = request.form.get('date_of_birth', '').strip()
            gender = request.form.get('gender', 'other')
            blood_type = request.form.get('blood_type', '').strip() or None
            medical_history = request.form.get('medical_history', '').strip() or None
            emergency_name = request.form.get('emergency_contact_name', '').strip()
            emergency_phone_raw = request.form.get('emergency_contact_phone', '').strip()

            is_dob_valid, dob_err, normalized_dob = validate_date_of_birth(date_of_birth)
            if not is_dob_valid:
                errors['date_of_birth'] = dob_err
            else:
                date_of_birth = normalized_dob

            if not emergency_name:
                errors['emergency_contact_name'] = "Emergency contact name is required."
            if not emergency_phone_raw:
                errors['emergency_contact_phone'] = "Emergency contact phone is required."
            else:
                is_valid_em_phone, clean_em_phone = validate_indian_mobile(emergency_phone_raw)
                if not is_valid_em_phone:
                    errors['emergency_contact_phone'] = "Enter a valid 10-digit Indian mobile number."
                else:
                    emergency_phone_raw = clean_em_phone

            profile_data = {
                'date_of_birth': date_of_birth,
                'gender': gender,
                'blood_type': blood_type,
                'medical_history': medical_history,
                'emergency_contact_name': emergency_name,
                'emergency_contact_phone': emergency_phone_raw
            }

        # 3. Uniqueness checks in DB
        if username and 'username' not in errors:
            if UserRepository.username_exists(username):
                errors['username'] = "Username already exists."

        if email and 'email' not in errors:
            if UserRepository.email_exists(email):
                errors['email'] = "Email address is already registered."

        # Return preserved form data & errors if validation failed
        if errors:
            return render_template('auth/register.html', form_data=request.form, errors=errors)

        # 4. Create user in system
        try:
            new_uid = UserService.register_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role_name=role_name,
                phone=phone,
                profile_data=profile_data
            )
            if role_name == 'patient':
                flash(f"Patient account created successfully. Username: {username}", "success")
            else:
                flash("Account registered successfully. Please log in.", "success")
            return redirect(url_for('auth.login'))
        except ValueError as err:
            err_msg = str(err)
            if "Username" in err_msg:
                errors['username'] = err_msg
            elif "Email" in err_msg:
                errors['email'] = err_msg
            else:
                flash(err_msg, "danger")
            return render_template('auth/register.html', form_data=request.form, errors=errors)
        except Exception as err:
            err_text = str(err).lower()
            if "1062" in err_text or "duplicate" in err_text:
                if "username" in err_text or "uq_username" in err_text:
                    errors['username'] = "Username already exists."
                elif "email" in err_text or "uq_email" in err_text:
                    errors['email'] = "Email address is already registered."
                else:
                    flash("An account with these details already exists.", "danger")
            else:
                flash("An unexpected error occurred during database registration.", "danger")
            return render_template('auth/register.html', form_data=request.form, errors=errors)

    return render_template('auth/register.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Renders forgot password view and verifies registered user email."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash("Please enter your registered email address.", "danger")
            return render_template('auth/forgot_password.html')
            
        if not validate_email(email):
            flash("Please enter a valid email address.", "danger")
            return render_template('auth/forgot_password.html', email=email)

        user = UserRepository.find_by_email(email)
        if not user:
            flash("No registered account found with that email address.", "danger")
            return render_template('auth/forgot_password.html', email=email)

        # Generate secure time-limited reset token for the user
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='mediprep-password-reset')
        token = serializer.dumps({'user_id': user['id'], 'email': user['email']})
        
        flash(f"Account verified for {user['email']}. Please enter your new password below.", "success")
        return redirect(url_for('auth.reset_password', token=token))

    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Verifies reset token and updates user password."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='mediprep-password-reset')
    try:
        data = serializer.loads(token, max_age=3600)  # Valid for 1 hour
    except (SignatureExpired, BadSignature):
        flash("The password reset link is invalid or has expired. Please request a new password reset.", "danger")
        return redirect(url_for('auth.forgot_password'))

    user_id = data.get('user_id')
    email = data.get('email')
    
    user = UserRepository.find_by_id(user_id)
    if not user or user['email'] != email:
        flash("Invalid user request.", "danger")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not new_password or not confirm_password:
            flash("Please fill in both password fields.", "danger")
            return render_template('auth/reset_password.html', token=token, email=email)

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('auth/reset_password.html', token=token, email=email)

        try:
            UserService.reset_user_password(user_id, new_password)
            flash("Your password has been reset successfully. Please sign in with your new password.", "success")
            return redirect(url_for('auth.login'))
        except ValueError as err:
            flash(str(err), "danger")
        except Exception as err:
            flash("An error occurred while resetting your password. Please try again.", "danger")

    return render_template('auth/reset_password.html', token=token, email=email)

@auth_bp.route('/logout')

def logout():
    """Clears local flask session and logs user out."""
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('auth.login'))
