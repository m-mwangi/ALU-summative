from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    # Configurations
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/your_database.db'
    
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    
    # Register blueprints
    from .routes import auth, main
    app.register_blueprint(auth)
    app.register_blueprint(main)
    
    # Set up the login manager
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Optional: Set the login view
    login_manager.login_view = 'auth.login'
    
    return app
