from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort, jsonify, send_from_directory, current_app
from app.services.doctor_service import DoctorService
from app.repositories.doctor_repository import DoctorRepository
from app.utilities.decorators import login_required, role_required
import json
import logging

logger = logging.getLogger(__name__)

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard')
@login_required
@role_required('doctor')
def dashboard():
    """Renders doctor main dashboard summarizing patient statuses and alerts."""
    doctor_id = session['user_id']
    summary = DoctorService.get_dashboard_summary(doctor_id)
    
    # Retrieve pre-op risk alerts dynamically (No AI)
    from app.services.alerts_service import AlertsService
    risk_alerts = AlertsService.get_active_risk_alerts(doctor_id)
    
    return render_template('doctor/dashboard.html', 
                           stats=summary['stats'], 
                           today_procedures=summary['today_procedures'],
                           recent_uploads=summary['recent_uploads'],
                           ready_count=summary['ready_count'],
                           pending_count=summary['pending_count'],
                           avg_readiness=summary['avg_readiness'],
                           readiness_distribution=summary['readiness_distribution'],
                           schedules=summary['schedules'], 
                           total_count=summary['total_schedules_count'],
                           risk_alerts=risk_alerts)

@doctor_bp.route('/schedules', methods=['GET'])
@login_required
@role_required('doctor')
def schedules():
    """Renders searchable worklist table of scheduled procedures."""
    doctor_id = session['user_id']
    search_query = request.args.get('search', '').strip()
    worklist = DoctorService.get_schedules_worklist(doctor_id, search_query)
    return render_template('doctor/schedule.html', schedules=worklist, search=search_query)

@doctor_bp.route('/api/procedures/<int:procedure_id>/templates')
@login_required
@role_required('doctor')
def get_templates(procedure_id):
    """API endpoint returning default checklist templates for a procedure type."""
    try:
        templates = DoctorRepository.get_checklist_templates(procedure_id)
        return jsonify({"success": True, "templates": templates})
    except Exception as e:
        logger.error(f"Error in API templates fetch: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@doctor_bp.route('/schedules/add', methods=['GET', 'POST'])
@login_required
@role_required('doctor')
def add_schedule():
    """Renders scheduling form and logs new procedure schedules in MySQL."""
    doctor_id = session['user_id']
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        procedure_id = request.form.get('procedure_id')
        scheduled_at = request.form.get('scheduled_at')
        preparation_room = request.form.get('preparation_room', '').strip()
        procedure_room = request.form.get('procedure_room', '').strip()
        checklist_json = request.form.get('checklist_json')
        
        if not all([patient_id, procedure_id, scheduled_at, preparation_room, procedure_room]):
            flash("All form fields are required. Please select Patient Account, Procedure Type, Scheduled Date & Time, Preparation Room, and Procedure / Scanning Room.", "danger")
            form_data = DoctorService.get_scheduling_form_data(doctor_id=doctor_id)
            return render_template('doctor/schedule_form.html', 
                                   patients=form_data['patients'], 
                                   procedures=form_data['procedures'], 
                                   procedure_rooms=form_data['procedure_rooms'],
                                   preparation_rooms=form_data['preparation_rooms'],
                                   procedure_scanning_rooms=form_data['procedure_scanning_rooms'],
                                   patient_id=int(patient_id) if patient_id and str(patient_id).isdigit() else None,
                                   procedure_id=int(procedure_id) if procedure_id and str(procedure_id).isdigit() else None,
                                   scheduled_at=scheduled_at,
                                   preparation_room=preparation_room,
                                   procedure_room=procedure_room,
                                   action="Add")
            
        try:
            # Parse custom checklist items from JSON submitted by client
            custom_checklist = json.loads(checklist_json) if checklist_json else []
            
            DoctorService.schedule_new_procedure_custom(
                patient_id=int(patient_id),
                doctor_id=doctor_id,
                procedure_id=int(procedure_id),
                scheduled_at_str=scheduled_at,
                preparation_room=preparation_room,
                procedure_room=procedure_room,
                custom_checklist=custom_checklist
            )
            flash("Procedure scheduled and custom preparation checklist initialized successfully.", "success")
            return redirect(url_for('doctor.schedules'))
        except ValueError as val_err:
            flash(str(val_err), "danger")
            form_data = DoctorService.get_scheduling_form_data(doctor_id=doctor_id)
            return render_template('doctor/schedule_form.html', 
                                   patients=form_data['patients'], 
                                   procedures=form_data['procedures'],
                                   procedure_rooms=form_data['procedure_rooms'],
                                   preparation_rooms=form_data['preparation_rooms'],
                                   procedure_scanning_rooms=form_data['procedure_scanning_rooms'],
                                   patient_id=int(patient_id) if patient_id and str(patient_id).isdigit() else None,
                                   procedure_id=int(procedure_id) if procedure_id and str(procedure_id).isdigit() else None,
                                   scheduled_at=scheduled_at,
                                   preparation_room=preparation_room,
                                   procedure_room=procedure_room,
                                   action="Add")
        except Exception as e:
            logger.error(f"Error in add_schedule: {e}")
            flash("An error occurred while saving the procedure schedule.", "danger")
            form_data = DoctorService.get_scheduling_form_data(doctor_id=doctor_id)
            return render_template('doctor/schedule_form.html', 
                                   patients=form_data['patients'], 
                                   procedures=form_data['procedures'],
                                   procedure_rooms=form_data['procedure_rooms'],
                                   preparation_rooms=form_data['preparation_rooms'],
                                   procedure_scanning_rooms=form_data['procedure_scanning_rooms'],
                                   patient_id=int(patient_id) if patient_id and str(patient_id).isdigit() else None,
                                   procedure_id=int(procedure_id) if procedure_id and str(procedure_id).isdigit() else None,
                                   scheduled_at=scheduled_at,
                                   preparation_room=preparation_room,
                                   procedure_room=procedure_room,
                                   action="Add")

    form_data = DoctorService.get_scheduling_form_data(doctor_id=doctor_id)
    return render_template('doctor/schedule_form.html', 
                           patients=form_data['patients'], 
                           procedures=form_data['procedures'], 
                           procedure_rooms=form_data['procedure_rooms'],
                           preparation_rooms=form_data['preparation_rooms'],
                           procedure_scanning_rooms=form_data['procedure_scanning_rooms'],
                           action="Add")

@doctor_bp.route('/schedules/edit/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
@role_required('doctor')
def edit_schedule(schedule_id):
    """Edits scheduled procedure details or cancels checklists."""
    schedule = DoctorService.get_schedule_details(schedule_id)
    if not schedule:
        abort(404)
        
    # Ensure doctor can only edit their own schedules
    if schedule['doctor_id'] != session['user_id']:
        abort(403)
        
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        procedure_id = request.form.get('procedure_id')
        scheduled_at = request.form.get('scheduled_at')
        preparation_room = request.form.get('preparation_room', '').strip()
        procedure_room = request.form.get('procedure_room', '').strip()
        status = request.form.get('status', 'scheduled')
        
        if not all([patient_id, procedure_id, scheduled_at, preparation_room, procedure_room]):
            flash("All form fields are required. Please select Patient Account, Procedure Type, Scheduled Date & Time, Preparation Room, and Procedure / Scanning Room.", "danger")
            form_data = DoctorService.get_scheduling_form_data(doctor_id=session['user_id'])
            return render_template('doctor/schedule_form.html', 
                                   patients=form_data['patients'], 
                                   procedures=form_data['procedures'], 
                                   procedure_rooms=form_data['procedure_rooms'],
                                   preparation_rooms=form_data['preparation_rooms'],
                                   procedure_scanning_rooms=form_data['procedure_scanning_rooms'],
                                   schedule=schedule, 
                                   action="Edit")

        try:
            DoctorService.update_procedure_schedule_custom(
                schedule_id=schedule_id,
                patient_id=int(patient_id),
                procedure_id=int(procedure_id),
                scheduled_at_str=scheduled_at,
                preparation_room=preparation_room,
                procedure_room=procedure_room,
                status=status
            )
            
            # Save readiness notes
            readiness_notes = request.form.get('readiness_notes', '').strip()
            from database import DBConnectionContext
            with DBConnectionContext() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT readiness_status FROM tbl_procedure_readiness WHERE scheduled_procedure_id = %s", (schedule_id,))
                    row = cursor.fetchone()
                    readiness_status = row['readiness_status'] if row else 'red'
            DoctorRepository.update_procedure_readiness(schedule_id, readiness_status, readiness_notes)
            
            # Save procedure guidelines
            procedure_guidelines = request.form.get('procedure_guidelines')
            if procedure_guidelines is not None:
                lines = [line.strip() for line in procedure_guidelines.split('\n') if line.strip()]
                with DBConnectionContext() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("DELETE FROM tbl_health_suggestions WHERE procedure_id = %s", (int(procedure_id),))
                        for line in lines:
                            cursor.execute("""
                                INSERT INTO tbl_health_suggestions (procedure_id, suggestion_text, trigger_condition)
                                VALUES (%s, %s, 'all')
                            """, (int(procedure_id), line))
                        conn.commit()
            
            flash("Procedure scheduling details updated successfully.", "success")
            return redirect(url_for('doctor.schedules'))
        except ValueError as val_err:
            flash(str(val_err), "danger")
        except Exception as e:
            logger.error(f"Error in edit_schedule: {e}")
            flash("An error occurred during update operations.", "danger")

    form_data = DoctorService.get_scheduling_form_data(doctor_id=session['user_id'])
    
    # Retrieve readiness notes and status
    from database import DBConnectionContext
    with DBConnectionContext() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT notes, readiness_status FROM tbl_procedure_readiness WHERE scheduled_procedure_id = %s", (schedule_id,))
            row = cursor.fetchone()
            if row:
                schedule['readiness_notes'] = row['notes']
                schedule['readiness_status'] = row['readiness_status']
            else:
                schedule['readiness_notes'] = ''
                schedule['readiness_status'] = 'red'

    # Format datetime for picker input tag (DD-MM-YYYY hh:mm AM/PM)
    from app.utilities.validators import validate_and_parse_datetime
    dt_val = schedule.get('scheduled_at')
    if dt_val:
        if hasattr(dt_val, 'strftime'):
            schedule['html_scheduled_at'] = dt_val.strftime("%d-%m-%Y %I:%M %p")
        else:
            try:
                parsed_dt = validate_and_parse_datetime(dt_val)
                schedule['html_scheduled_at'] = parsed_dt.strftime("%d-%m-%Y %I:%M %p")
            except Exception:
                schedule['html_scheduled_at'] = str(dt_val)
    else:
        schedule['html_scheduled_at'] = ''
    
    # Retrieve current active checklist items to render in edit mode
    current_items = DoctorRepository.get_active_checklist_items(schedule_id)
    
    # Retrieve patient pre-op vitals & rule-based suggestions (No AI)
    from app.repositories.patient_repository import PatientRepository
    from app.services.rules_engine import RulesEngine
    vitals = PatientRepository.get_patient_vitals(schedule_id)
    vitals_alerts = []
    if vitals:
        vitals_alerts = RulesEngine.evaluate_vitals(vitals)
        
    # Retrieve procedure guidelines
    suggestions = PatientRepository.get_health_suggestions(schedule['procedure_id'], '')
    procedure_guidelines_text = "\n".join(suggestions)
        
    # Retrieve clinical board messages history sent by doctor
    messages = DoctorService.get_messages_for_schedule(schedule_id)
    
    return render_template('doctor/schedule_form.html', 
                           patients=form_data['patients'], 
                           procedures=form_data['procedures'], 
                           procedure_rooms=form_data['procedure_rooms'],
                           preparation_rooms=form_data['preparation_rooms'],
                           procedure_scanning_rooms=form_data['procedure_scanning_rooms'],
                           schedule=schedule, 
                           current_items=current_items,
                           vitals=vitals,
                           vitals_alerts=vitals_alerts,
                           procedure_guidelines_text=procedure_guidelines_text,
                           messages=messages,
                           action="Edit")

@doctor_bp.route('/schedules/delete/<int:schedule_id>', methods=['POST'])
@login_required
@role_required('doctor')
def delete_schedule(schedule_id):
    """Cancels and deletes a scheduled procedure."""
    schedule = DoctorService.get_schedule_details(schedule_id)
    if not schedule:
        abort(404)
        
    if schedule['doctor_id'] != session['user_id']:
        abort(403)
        
    try:
        DoctorService.cancel_procedure_schedule(schedule_id)
        flash("Procedure scheduled slot has been cancelled.", "success")
    except Exception as e:
        flash("Failed to delete database record.", "danger")
        
    return redirect(url_for('doctor.schedules'))

@doctor_bp.route('/schedules/<int:schedule_id>/verify/<int:item_id>', methods=['POST'])
@login_required
@role_required('doctor')
def verify_item(schedule_id, item_id):
    """Clinic/Doctor signs off and verifies patient checklist completions or report uploads."""
    doctor_id = session['user_id']
    try:
        DoctorService.evaluate_and_verify_checklist_item(item_id, schedule_id, doctor_id)
        flash("Checklist item successfully verified and signed off.", "success")
    except Exception as e:
        logger.error(f"Error in verify_item: {e}")
        flash("Failed to verify checklist item.", "danger")
    return redirect(url_for('doctor.edit_schedule', schedule_id=schedule_id))

@doctor_bp.route('/reports/view/<path:filename>', methods=['GET'])
@login_required
@role_required('doctor')
def view_uploaded_report(filename):
    """Securely downloads/streams clinical reports from uploads folder to authorized staff."""
    import os
    from flask import current_app, send_from_directory, flash, redirect, url_for, session
    from app.repositories.lab_repository import LabRepository

    clean_filename = filename.replace('\\', '/')
    safe_filename = os.path.basename(clean_filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    doctor_id = session.get('user_id')
    report = LabRepository.get_report_by_file_path(safe_filename)
    if report and report.get('doctor_id') and report['doctor_id'] != doctor_id:
        logger.warning(f"Doctor {doctor_id} requested report {safe_filename} for doctor {report.get('doctor_id')}")

    target_path = os.path.join(upload_folder, safe_filename)
    if not os.path.exists(target_path) or not os.path.isfile(target_path):
        logger.error(f"Report file not found on storage: {target_path}")
        flash("Report file is unavailable. Please contact the laboratory administrator.", "danger")
        return redirect(url_for('doctor.dashboard'))

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

@doctor_bp.route('/reports', methods=['GET'])
@login_required
@role_required('doctor')
def reports():
    """Renders the preoperative reports dashboard query panel."""
    doctor_id = session['user_id']
    report_type = request.args.get('type', 'ready_patients')
    
    from app.services.reports_service import ReportsService
    try:
        report_data = ReportsService.get_report_data(doctor_id, report_type)
    except Exception as e:
        flash("Failed to retrieve report data.", "danger")
        return redirect(url_for('doctor.dashboard'))
        
    return render_template('doctor/reports.html', 
                           report_type=report_type, 
                           report_title=report_data['title'],
                           headers=report_data['headers'], 
                           rows=report_data['rows'])

@doctor_bp.route('/reports/download/<report_type>', methods=['GET'])
@login_required
@role_required('doctor')
def download_pdf_report(report_type):
    """Streams a generated PDF report for pre-op compliance verification."""
    doctor_id = session['user_id']
    doctor_name = session.get('first_name', '') + " " + session.get('last_name', '')
    
    from app.services.reports_service import ReportsService
    from flask import send_file
    from datetime import datetime
    try:
        pdf_stream = ReportsService.generate_pdf_stream(doctor_id, report_type, doctor_name)
        return send_file(
            pdf_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{report_type}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
    except Exception as e:
        logger.error(f"Error serving report PDF download: {e}")
        flash("Failed to generate PDF download stream.", "danger")
        return redirect(url_for('doctor.reports'))

@doctor_bp.route('/schedules/edit/<int:schedule_id>/message', methods=['POST'])
@login_required
@role_required('doctor')
def send_patient_message(schedule_id):
    """Sends preoperative message to the patient for a specific scheduled procedure."""
    doctor_id = session['user_id']
    message_text = request.form.get('message_text', '').strip()
    
    try:
        DoctorService.send_patient_message(schedule_id, doctor_id, message_text)
        flash("Message sent to the patient's Clinical Board successfully.", "success")
    except ValueError as val_err:
        flash(str(val_err), "danger")
    except PermissionError:
        abort(403)
    except Exception as e:
        logger.error(f"Error sending message from doctor: {e}")
        flash("Failed to send the message.", "danger")
        
    return redirect(url_for('doctor.edit_schedule', schedule_id=schedule_id))

@doctor_bp.route('/reports/<int:report_id>/verify', methods=['POST'])
@login_required
@role_required('doctor')
def verify_report(report_id):
    """Doctor verifies an official laboratory report."""
    doctor_id = session['user_id']
    from app.repositories.lab_repository import LabRepository
    from app.repositories.audit_repository import AuditRepository
    from app.services.readiness_service import ReadinessService

    report = LabRepository.get_report_by_id(report_id)
    if not report:
        flash("Report not found.", "danger")
        return redirect(url_for('doctor.dashboard'))

    try:
        notes = request.form.get('verification_notes', '').strip() or "Verified by attending physician."
        LabRepository.update_report_verification(report_id, doctor_id, 'verified', notes)
        AuditRepository.log_audit_action(
            user_id=doctor_id,
            role_name='doctor',
            action="REPORT_VERIFIED",
            details=f"Verified report ID {report_id} for checklist item '{report['task_name']}'. Notes: {notes}",
            patient_id=report['patient_id'],
            scheduled_procedure_id=report['scheduled_procedure_id']
        )
        ReadinessService.evaluate_and_update_readiness(report['scheduled_procedure_id'])
        flash("Official Laboratory Report successfully VERIFIED!", "success")
    except Exception as e:
        logger.error(f"Error verifying report: {e}")
        flash("Failed to verify report.", "danger")

    return redirect(request.referrer or url_for('doctor.dashboard'))

@doctor_bp.route('/reports/<int:report_id>/reject', methods=['POST'])
@login_required
@role_required('doctor')
def reject_report(report_id):
    """Doctor marks a report as needing clarification."""
    doctor_id = session['user_id']
    from app.repositories.lab_repository import LabRepository
    from app.repositories.audit_repository import AuditRepository
    from app.services.readiness_service import ReadinessService

    report = LabRepository.get_report_by_id(report_id)
    if not report:
        flash("Report not found.", "danger")
        return redirect(url_for('doctor.dashboard'))

    reason = request.form.get('rejection_reason', '').strip() or request.form.get('verification_notes', '').strip()
    if not reason:
        flash("Please provide a reason for clarification.", "warning")
        return redirect(request.referrer or url_for('doctor.dashboard'))

    try:
        LabRepository.update_report_verification(report_id, doctor_id, 'needs_clarification', reason)
        AuditRepository.log_audit_action(
            user_id=doctor_id,
            role_name='doctor',
            action="REPORT_MARKED_NEEDS_CLARIFICATION",
            details=f"Marked report ID {report_id} as NEEDS CLARIFICATION. Reason: {reason}",
            patient_id=report['patient_id'],
            scheduled_procedure_id=report['scheduled_procedure_id']
        )
        ReadinessService.evaluate_and_update_readiness(report['scheduled_procedure_id'])
        flash("Report marked as NEEDS CLARIFICATION.", "warning")
    except Exception as e:
        logger.error(f"Error updating report: {e}")
        flash("Failed to update report status.", "danger")

    return redirect(request.referrer or url_for('doctor.dashboard'))

@doctor_bp.route('/schedules/<int:schedule_id>/upload_external_report', methods=['POST'])
@login_required
@role_required('doctor')
def upload_external_report(schedule_id):
    """Doctor uploads an external laboratory report received from a patient."""
    doctor_id = session['user_id']
    schedule = DoctorService.get_schedule_details(schedule_id)
    if not schedule:
        abort(404)

    if schedule['doctor_id'] != doctor_id:
        abort(403)

    item_id = request.form.get('checklist_item_id')
    lab_name = request.form.get('lab_name', '').strip()
    external_report_id = request.form.get('external_report_id', '').strip()
    report_date = request.form.get('report_date', '').strip()
    verification_status = request.form.get('verification_status', 'external_received')
    notes = request.form.get('notes', '').strip()

    if not item_id:
        flash("Please select an investigation task.", "danger")
        return redirect(request.referrer or url_for('doctor.edit_schedule', schedule_id=schedule_id))

    if 'report_file' not in request.files or not request.files['report_file'].filename:
        flash("Please attach an official report file (PDF or Image).", "danger")
        return redirect(request.referrer or url_for('doctor.edit_schedule', schedule_id=schedule_id))

    file = request.files['report_file']
    upload_folder = current_app.config['UPLOAD_FOLDER']

    try:
        from app.services.lab_service import LabService
        LabService.upload_external_lab_report(
            item_id=int(item_id),
            file=file,
            upload_folder=upload_folder,
            doctor_id=doctor_id,
            lab_name=lab_name,
            external_report_id=external_report_id,
            report_date=report_date,
            verification_status=verification_status,
            notes=notes
        )
        flash(f"External Laboratory Report from '{lab_name}' uploaded successfully!", "success")
    except ValueError as val_err:
        flash(str(val_err), "danger")
    except Exception as e:
        logger.error(f"Error uploading external report: {e}")
        flash("Failed to upload external laboratory report.", "danger")

    return redirect(request.referrer or url_for('doctor.edit_schedule', schedule_id=schedule_id))

@doctor_bp.route('/reports/<int:report_id>/status', methods=['POST'])
@login_required
@role_required('doctor')
def update_report_status(report_id):
    """Doctor updates report status (Verified, Needs Clarification, External Report – Received)."""
    doctor_id = session['user_id']
    from app.repositories.lab_repository import LabRepository
    from app.repositories.audit_repository import AuditRepository
    from app.services.readiness_service import ReadinessService

    report = LabRepository.get_report_by_id(report_id)
    if not report:
        flash("Report not found.", "danger")
        return redirect(url_for('doctor.dashboard'))

    new_status = request.form.get('status', 'verified')
    notes = request.form.get('verification_notes', '').strip()

    if new_status not in ['verified', 'needs_clarification', 'needs_review', 'external_received', 'pending_verification']:
        flash("Invalid report status selected.", "danger")
        return redirect(request.referrer or url_for('doctor.dashboard'))

    try:
        LabRepository.update_report_verification(report_id, doctor_id, new_status, notes)
        AuditRepository.log_audit_action(
            user_id=doctor_id,
            role_name='doctor',
            action=f"REPORT_STATUS_UPDATED_{new_status.upper()}",
            details=f"Doctor updated report ID {report_id} status to '{new_status}'. Notes: {notes}",
            patient_id=report['patient_id'],
            scheduled_procedure_id=report['scheduled_procedure_id']
        )
        ReadinessService.evaluate_and_update_readiness(report['scheduled_procedure_id'])
        flash(f"Report status updated successfully.", "success")
    except Exception as e:
        logger.error(f"Error updating report status: {e}")
        flash("Failed to update report status.", "danger")

    return redirect(request.referrer or url_for('doctor.dashboard'))

@doctor_bp.route('/consent/<int:consent_id>/verify', methods=['POST'])
@login_required
@role_required('doctor')
def verify_consent(consent_id):
    """Doctor verifies confirmed patient system consent."""
    doctor_id = session['user_id']
    from app.repositories.audit_repository import AuditRepository
    from app.services.readiness_service import ReadinessService
    from database import DBConnectionContext

    with DBConnectionContext() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM tbl_patient_consents WHERE id = %s", (consent_id,))
            consent = cursor.fetchone()

    if not consent:
        flash("Consent record not found.", "danger")
        return redirect(url_for('doctor.dashboard'))

    try:
        DoctorRepository.verify_patient_consent(consent_id, doctor_id)
        AuditRepository.log_audit_action(
            user_id=doctor_id,
            role_name='doctor',
            action="CONSENT_VERIFIED_BY_DOCTOR",
            details=f"Doctor verified patient consent record ID {consent_id}.",
            scheduled_procedure_id=consent['scheduled_procedure_id']
        )
        ReadinessService.evaluate_and_update_readiness(consent['scheduled_procedure_id'])
        flash("Patient Informed Consent VERIFIED by attending physician!", "success")
    except Exception as e:
        logger.error(f"Error verifying consent: {e}")
        flash("Failed to verify consent.", "danger")

    return redirect(request.referrer or url_for('doctor.dashboard'))

@doctor_bp.route('/schedules/<int:schedule_id>/checkin', methods=['POST'])
@login_required
@role_required('doctor')
def update_check_in(schedule_id):
    """Doctor / Staff updates procedure-day check-in status (scheduled -> arrived -> checked_in -> ready_for_procedure)."""
    user_id = session['user_id']
    role_name = session.get('role_name', 'doctor')
    check_in_status = request.form.get('check_in_status', 'scheduled')

    try:
        DoctorRepository.update_check_in_status(schedule_id, check_in_status)
        from app.repositories.audit_repository import AuditRepository
        AuditRepository.log_audit_action(
            user_id=user_id,
            role_name=role_name,
            action="PROCEDURE_CHECK_IN_UPDATED",
            details=f"Updated procedure-day check-in status to '{check_in_status}'",
            scheduled_procedure_id=schedule_id
        )
        flash(f"Procedure check-in status updated to '{check_in_status.replace('_', ' ').title()}'.", "success")
    except Exception as e:
        logger.error(f"Error updating check-in status: {e}")
        flash("Failed to update check-in status.", "danger")

    return redirect(request.referrer or url_for('doctor.dashboard'))

