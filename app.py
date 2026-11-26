import os
from flask import Flask, render_template, jsonify, request
from flask_login import LoginManager
from config import config_dict
from database import db
from models.user import User


def create_app(config_name=None):
    """Application factory for Blue Line."""
    if config_name is None:
        env = os.environ.get('FLASK_ENV', 'development')
        config_name = 'development' if env != 'testing' else 'testing'

    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])
    if config_name == 'production' and 'insecure' in app.config['SECRET_KEY']:
        raise RuntimeError('Set a strong SECRET_KEY in .env before running in production.')

    # Ensure instance directory exists
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.contacts import contacts_bp
    from routes.emergency import emergency_bp
    from routes.api import api_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # Context processors
    @app.context_processor
    def inject_global_template_vars():
        return {
            'DEMO_MODE': app.config.get('DEMO_MODE', True),
            'APP_NAME': 'BLUE LINE',
            'APP_SUBTITLE': 'Smart Emergency Safety System'
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'API endpoint not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Access forbidden'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

    # Auto-create tables in development
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app('development')
    # Seed database if not yet seeded
    from database.seed_data import seed_database
    seed_database(app)
    
    print("\n" + "=" * 65)
    print(" 🚀 BLUE LINE - Emergency Response System Server Active")
    print(" 🌐 Local URL: http://127.0.0.1:5000")
    print(" 🛡️  Demo Mode: ENABLED (Simulated emergency dispatch)")
    print(" 👤 Demo User : demo@example.com (Password: Demo@12345)")
    print(" 🔑 Admin User: admin@blueline.local (Password: Admin@12345)")
    print("=" * 65 + "\n")

    app.run(host='127.0.0.1', port=5000, debug=True)
