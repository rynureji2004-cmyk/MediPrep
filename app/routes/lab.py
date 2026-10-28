from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, send_from_directory, abort
from app.repositories.lab_repository import LabRepository
from app.services.lab_service import LabService
from app.utilities.decorators import login_required, role_required
import logging

logger = logging.getLogger(__name__)

lab_bp = Blueprint('lab', __name__)

@lab_bp.route('/dashboard')
@login_required
@role_required('lab_tech')
def dashboard():
    """Renders Hospital Lab Technician dashboard listing assigned investigations."""
    user_id = session['user_id']
    lab_profile = LabRepository.get_lab_profile_by_user_id(user_id)
    lab_name = lab_profile['lab_name'] if lab_profile else 'Central Hospital Clinical Laboratory'
    
    search_query = request.args.get('search', '').strip()
    investigations = LabRepository.get_assigned_investigations(lab_type='hospital', search_query=search_query)
    return render_template('lab/dashboard.html', 
                           lab_name=lab_name, 
                           investigations=investigations,
                           search_query=search_query)

@lab_bp.route('/upload/<int:item_id>', methods=['GET', 'POST'])
@login_required
@role_required('lab_tech')
def upload_report(item_id):
    """Hospital Lab Tech uploads official laboratory report (LOCKED on upload)."""
    user_id = session['user_id']
    role_name = session.get('role_name', 'lab_tech')
    investigation = LabRepository.get_investigation_by_id(item_id)
    
    if not investigation:
        flash("Investigation task not found.", "danger")
        return redirect(url_for('lab.dashboard'))

    history = LabRepository.get_report_history(item_id)
    latest_report = history[0] if history else None

    if request.method == 'POST':
        file = request.files.get('report_file')
        lab_name = request.form.get('lab_name', '').strip() or 'Central Hospital Clinical Laboratory'
        external_report_id = request.form.get('external_report_id', '').strip() or request.form.get('report_ref_no', '').strip()
        report_date = request.form.get('report_date', '').strip()
        notes = request.form.get('notes', '').strip()
        task_name = request.form.get('task_name', '').strip()

        upload_folder = current_app.config['UPLOAD_FOLDER']

        try:
            LabService.upload_official_lab_report(
                item_id=item_id,
                file=file,
                upload_folder=upload_folder,
                user_id=user_id,
                role_name=role_name,
                lab_name=lab_name,
                external_report_id=external_report_id,
                report_date=report_date,
                notes=notes,
                task_name=task_name
            )
            flash("Official Hospital Laboratory Report saved and locked successfully! Queued for Doctor Verification.", "success")
            return redirect(url_for('lab.dashboard'))
        except ValueError as val_err:
            flash(str(val_err), "danger")
        except Exception as e:
            logger.error(f"Error uploading lab report: {e}")
            flash(f"Failed to save report: {e}", "danger")

    return render_template('lab/upload_form.html', investigation=investigation, history=history, latest_report=latest_report)

@lab_bp.route('/reports/view/<path:filename>')
@login_required
@role_required('lab_tech', 'doctor', 'patient', 'admin')
def view_report_file(filename):
    """Securely streams uploaded lab report to authorized users."""
    import os
    from flask import current_app, send_from_directory, flash, redirect, url_for

    clean_filename = filename.replace('\\', '/')
    safe_filename = os.path.basename(clean_filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']

    target_path = os.path.join(upload_folder, safe_filename)
    if not os.path.exists(target_path) or not os.path.isfile(target_path):
        logger.error(f"Lab report file missing on disk: {target_path}")
        flash("Report file is unavailable. Please contact the laboratory administrator.", "danger")
        return redirect(url_for('dashboard.index'))

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

@lab_bp.route('/requirement-pdf/<int:item_id>')
@login_required
@role_required('lab_tech', 'doctor', 'patient', 'admin')
def download_requirement_pdf(item_id):
    """Securely downloads the individual patient laboratory requirement PDF."""
    import os
    from app.services.lab_requirement_pdf_service import get_or_generate_patient_pdf

    pdf_path, filename = get_or_generate_patient_pdf(item_id)
    if not pdf_path or not os.path.exists(pdf_path):
        flash("Laboratory requirement PDF is not available for this procedure.", "warning")
        return redirect(url_for('lab.dashboard'))

    return send_from_directory(
        os.path.dirname(pdf_path),
        filename,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@lab_bp.route('/sample-report-pdf/<int:item_id>')
@login_required
@role_required('lab_tech', 'doctor', 'patient', 'admin')
def download_sample_report_pdf(item_id):
    """Securely downloads the individual patient sample test report PDF (SAMPLE - NOT FOR CLINICAL USE)."""
    import os
    from app.services.sample_report_pdf_service import get_or_generate_sample_report_pdf

    pdf_path, filename = get_or_generate_sample_report_pdf(item_id)
    if not pdf_path or not os.path.exists(pdf_path):
        flash("Sample test report PDF is not available for this procedure.", "warning")
        return redirect(url_for('lab.dashboard'))

    return send_from_directory(
        os.path.dirname(pdf_path),
        filename,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
