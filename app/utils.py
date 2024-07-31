from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

try:
    db.create_all()
except Exception as e:
    print(f"Error creating database: {e}")
    # Consider logging the error or taking other actions
 
