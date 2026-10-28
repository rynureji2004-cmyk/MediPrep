from flask import Flask, render_template
import os
import logging
from config import config_by_name
from database import DatabaseManager

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def create_app(config_env=None):
    """Application factory for building and configuring the Flask system."""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration settings
    env = config_env or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[env])
    
    # Initialize MySQL Database connection pool
    DatabaseManager.initialize_pool(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME'],
        pool_size=app.config['DB_POOL_SIZE'],
        pool_name=app.config['DB_POOL_NAME']
    )
    
    # Ensure secure directory for document uploads exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints (routing structures)
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.patient import patient_bp
    from app.routes.doctor import doctor_bp
    from app.routes.admin import admin_bp
    from app.routes.lab import lab_bp
    from app.routes.external_lab import external_lab_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(lab_bp, url_prefix='/lab')
    app.register_blueprint(external_lab_bp, url_prefix='/external_lab')
    
    # Root Route redirection / Landing
    @app.route('/')
    def landing():
        from app.repositories.admin_repository import AdminRepository
        stats = None
        try:
            stats = AdminRepository.get_admin_stats()
        except Exception as e:
            logger.error(f"Error fetching stats for landing page: {e}")
        return render_template('base.html', stats=stats)
        
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_message="Resource not found"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_message="An internal server error occurred"), 500

    return app
