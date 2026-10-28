from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, abort, send_from_directory
from app.services.patient_service import PatientService
from app.repositories.patient_repository import PatientRepository
from app.repositories.audit_repository import AuditRepository
from app.utilities.decorators import login_required, role_required
import logging

logger = logging.getLogger(__name__)

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/dashboard')
@login_required
@role_required('patient')
def dashboard():
    """Renders patient clinical dashboard showing schedules, checklists, suggestions, assessment, consent, and readiness breakdown."""
    patient_id = session['user_id']
    schedule_id = request.args.get('schedule_id', type=int)
    summary = PatientService.get_dashboard_summary(patient_id, selected_schedule_id=schedule_id)
    return render_template('patient/dashboard.html', 
                           procedures=summary['procedures'],
                           procedure=summary['procedure'], 
                           checklist=summary['checklist'], 
                           progress=summary['progress'], 
                           suggestions=summary['suggestions'], 
                           notifications=summary['notifications'],
                           vitals=summary['vitals'],
                           vitals_alerts=summary['vitals_alerts'],
                           reminders=summary['reminders'],
                           assessment=summary['assessment'],
                           consent=summary['consent'],
                           readiness_details=summary['readiness_details'])

@patient_bp.route('/checklist')
@login_required
@role_required('patient')
def checklist():
    """Redirects to main patient dashboard."""
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/checklist/item/<int:item_id>/complete', methods=['POST'])
@login_required
@role_required('patient')
def complete_item(item_id):
    """Patient check-off toggle for allowed patient action checklist instructions."""
    patient_id = session['user_id']
    try:
        PatientService.complete_patient_task(item_id, patient_id)
        flash("Preoperative preparation task updated successfully.", "success")
    except Exception as e:
        flash("Failed to update task status.", "danger")
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/checklist/item/<int:item_id>/upload', methods=['POST'])
@login_required
@role_required('patient')
def upload_report(item_id):
    """Enforces Security Policy: Patients are prohibited from uploading official laboratory reports."""
    patient_id = session['user_id']
    try:
        PatientService.upload_report_document(item_id, None, None, patient_id)
    except PermissionError as perm_err:
        flash(str(perm_err), "danger")
    except Exception:
        flash("Upload access denied. Official laboratory reports must be submitted by authorized laboratory personnel.", "danger")
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/assessment/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def assessment_form(schedule_id):
    """Renders and processes patient Pre-Procedure Assessment."""
    patient_id = session['user_id']
    
    # Patient Data Privacy check: verify schedule ownership
    schedules = PatientRepository.get_assigned_procedures(patient_id)
    schedule = next((s for s in schedules if s['id'] == schedule_id), None)
    if not schedule:
        abort(403) # Access Denied

    assessment = PatientRepository.get_patient_assessment(schedule_id)
    
    if request.method == 'POST':
        # Block modification if already submitted and locked
        if assessment and assessment.get('status') == 'submitted_locked':
            flash("This assessment is locked and cannot be edited after submission.", "warning")
            return redirect(url_for('patient.dashboard'))

        allergies = request.form.get('allergies', '').strip()
        medications = request.form.get('current_medications', '').strip()
        surgeries = request.form.get('previous_surgeries', '').strip()
        anesthesia = request.form.get('anesthesia_problems', '').strip()
        history_notes = request.form.get('medical_history_notes', '').strip()
        emergency_name = request.form.get('emergency_contact_name', '').strip()
        emergency_phone = request.form.get('emergency_contact_phone', '').strip()
        submit_action = request.form.get('action') == 'submit_lock'

        if submit_action and not all([emergency_name, emergency_phone]):
            flash("Emergency Contact Name and Phone are required to submit assessment.", "danger")
            return render_template('patient/assessment_form.html', schedule=schedule, assessment=request.form)

        try:
            PatientRepository.save_patient_assessment(
                scheduled_id=schedule_id,
                allergies=allergies,
                meds=medications,
                surgeries=surgeries,
                anesthesia=anesthesia,
                history_notes=history_notes,
                contact_name=emergency_name,
                contact_phone=emergency_phone,
                submit_and_lock=submit_action
            )
            
            if submit_action:
                AuditRepository.log_audit_action(
                    user_id=patient_id,
                    role_name='patient',
                    action="PATIENT_ASSESSMENT_SUBMITTED",
                    details="Patient completed and locked Pre-Procedure Assessment form.",
                    patient_id=patient_id,
                    scheduled_procedure_id=schedule_id
                )
                from app.services.readiness_service import ReadinessService
                ReadinessService.evaluate_and_update_readiness(schedule_id)
                flash("Pre-Procedure Assessment submitted and locked successfully!", "success")
                return redirect(url_for('patient.dashboard'))
            else:
                flash("Assessment draft saved successfully.", "success")
        except Exception as e:
            logger.error(f"Error saving assessment: {e}")
            flash("Failed to save assessment details.", "danger")

    return render_template('patient/assessment_form.html', schedule=schedule, assessment=assessment)

@patient_bp.route('/consent/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def consent_view(schedule_id):
    """Renders System-Generated Consent record for patient electronic confirmation."""
    patient_id = session['user_id']
    
    # Patient Data Privacy check: verify schedule ownership
    schedules = PatientRepository.get_assigned_procedures(patient_id)
    schedule = next((s for s in schedules if s['id'] == schedule_id), None)
    if not schedule:
        abort(403)

    consent = PatientRepository.create_or_get_system_consent(schedule_id)

    if request.method == 'POST':
        if not consent:
            flash("Consent record not available.", "danger")
            return redirect(url_for('patient.dashboard'))

        if consent['status'] in ['confirmed_locked', 'verified']:
            flash("System Consent has already been confirmed and locked.", "warning")
            return redirect(url_for('patient.dashboard'))

        try:
            PatientRepository.confirm_patient_consent(consent['id'], patient_id)
            AuditRepository.log_audit_action(
                user_id=patient_id,
                role_name='patient',
                action="SYSTEM_CONSENT_CONFIRMED",
                details=f"Patient electronically confirmed and locked consent record (v{consent['version']}).",
                patient_id=patient_id,
                scheduled_procedure_id=schedule_id
            )
            from app.services.readiness_service import ReadinessService
            ReadinessService.evaluate_and_update_readiness(schedule_id)
            flash("System Consent confirmed and locked successfully!", "success")
            return redirect(url_for('patient.dashboard'))
        except Exception as e:
            logger.error(f"Error confirming consent: {e}")
            flash("Failed to confirm consent.", "danger")

    return render_template('patient/consent_view.html', schedule=schedule, consent=consent)

@patient_bp.route('/vitals/record/<int:schedule_id>', methods=['POST'])
@login_required
@role_required('patient')
def record_vitals(schedule_id):
    """Handles patient saving their pre-op vitals/lab values."""
    patient_id = session['user_id']
    
    # Privacy Check
    schedules = PatientRepository.get_assigned_procedures(patient_id)
    if not any(s['id'] == schedule_id for s in schedules):
        abort(403)

    try:
        PatientService.record_vitals(schedule_id, request.form)
        flash("Pre-operative vitals and lab metrics logged successfully.", "success")
    except ValueError as val_err:
        flash(str(val_err), "danger")
    except Exception as e:
        flash("Failed to log clinical vitals.", "danger")
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/reports/view/<path:filename>', methods=['GET'])
@login_required
@role_required('patient')
def view_uploaded_report(filename):
    """Securely streams verified clinical reports to authorized patient."""
    import os
    from flask import current_app, send_from_directory, flash, redirect, url_for, session
    from app.repositories.lab_repository import LabRepository

    clean_filename = filename.replace('\\', '/')
    safe_filename = os.path.basename(clean_filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']

    patient_id = session.get('user_id')
    report = LabRepository.get_report_by_file_path(safe_filename)
    if report and report.get('patient_id') and report['patient_id'] != patient_id:
        flash("Unauthorized access to report file.", "danger")
        return redirect(url_for('patient.dashboard'))

    target_path = os.path.join(upload_folder, safe_filename)
    if not os.path.exists(target_path) or not os.path.isfile(target_path):
        logger.error(f"Patient report file missing on disk: {target_path}")
        flash("Report file is unavailable. Please contact the laboratory administrator.", "danger")
        return redirect(url_for('patient.dashboard'))

    mimetype = 'application/pdf'
    if safe_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        ext = safe_filename.rsplit('.', 1)[1].lower()
        mimetype = f'image/{ext}' if ext != 'jpg' else 'image/jpeg'

    return send_from_directory(
        upload_folder,
        safe_filename,
        mimetype=mimetype,
        as_attachment=False
    )
