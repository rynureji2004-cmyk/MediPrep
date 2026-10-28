from flask import Blueprint, redirect, url_for, flash
import logging

logger = logging.getLogger(__name__)

external_lab_bp = Blueprint('external_lab', __name__)

@external_lab_bp.route('/dashboard')
def dashboard():
    """External lab technician workflow replaced by direct doctor upload per system design."""
    flash("External Laboratory accounts are not required. External reports are submitted directly by attending doctors upon receipt from patients.", "info")
    return redirect(url_for('auth.login'))

@external_lab_bp.route('/upload/<int:item_id>', methods=['GET', 'POST'])
def upload_report(item_id):
    """External lab technician upload route disabled. Reports are uploaded by attending doctors."""
    flash("External Laboratory accounts are not required. External reports are submitted directly by attending doctors upon receipt from patients.", "info")
    return redirect(url_for('auth.login'))
