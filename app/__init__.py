from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Security Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', os.urandom(32))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///aura.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_POOL_SIZE'] = 10
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
    
    # Rate Limiting
    app.config['RATELIMIT_STORAGE_URL'] = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    app.config['RATELIMIT_DEFAULT'] = '1000 per day;100 per hour'
    
    # CORS Configuration
    app.config['CORS_HEADERS'] = 'Content-Type'
    
    # Initialize extensions
    db = SQLAlchemy(app)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)
    login_manager = LoginManager(app)
    csrf = CSRFProtect(app)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(401)
    def unauthorized(e):
        return {'error': 'Unauthorized access'}, 401
    
    @app.errorhandler(500)
    def server_error(e):
        return {'error': 'Internal server error'}, 500
    
    return app, db, bcrypt, jwt, login_manager, csrf

# Create application instance
app, db, bcrypt, jwt, login_manager, csrf = create_app()

# Import routes after app creation to avoid circular imports
from app.routes.auth import auth_bp
from app.routes.main import main_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

# Initialize database
with app.app_context():
    db.create_all()
