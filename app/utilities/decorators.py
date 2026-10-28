from functools import wraps
from flask import session, redirect, url_for, flash, abort

def login_required(f):
    """Decorator checking that a valid user login session is active."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator restricting route access to users with specified role names."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('auth.login'))
            
            user_role = session.get('role_name')
            if user_role not in roles:
                # Deny access with 403 Forbidden
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
