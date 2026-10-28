from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.utilities.decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Redirects the logged-in user to their respective dashboard view."""
    role = session.get('role_name')
    if role == 'doctor':
        return redirect(url_for('doctor.dashboard'))
    elif role == 'patient':
        return redirect(url_for('patient.dashboard'))
    elif role == 'lab_tech':
        return redirect(url_for('lab.dashboard'))
    elif role == 'external_lab_tech':
        return redirect(url_for('external_lab.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    return render_template('dashboard/index.html')

@dashboard_bp.route('/procedure/<int:procedure_id>')
def detail(procedure_id):
    """Renders detailed status dashboard for a single scheduled procedure."""
    # Logic to fetch procedure readiness, checklist items, audit logs, and reports will go here
    return render_template('dashboard/details.html', procedure_id=procedure_id)

@dashboard_bp.route('/procedure/<int:procedure_id>/verify/<int:item_id>', methods=['POST'])
def verify_item(procedure_id, item_id):
    """Clinical staff validation checkoff for document uploads or checklist verifications."""
    # Clinical sign-off verification logic goes here
    flash("Item verification processing placeholder", "success")
    return redirect(url_for('dashboard.detail', procedure_id=procedure_id))

@dashboard_bp.route('/procedure/<int:procedure_id>/override', methods=['POST'])
def override_readiness(procedure_id):
    """Forces manual override of a procedure status (e.g. override red warning to yellow/green)."""
    # Readiness override logic goes here
    flash("Readiness override processing placeholder", "warning")
    return redirect(url_for('dashboard.detail', procedure_id=procedure_id))
