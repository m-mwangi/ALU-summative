from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_socketio import SocketIO
import os

# Import blueprints
from .routes import auth, main

# Initialize instances
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Update after choosing a database
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'

    # Initialize dependencies
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)
    socketio.init_app(app)

    # Set login view
    login_manager.login_view = 'auth.login'

    # Import User model after creating the app context
    with app.app_context():
        from .models import User  # Ensure this import is here

        # Define the user loader function
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Create database tables
        db.create_all()

    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(main)

    return app
