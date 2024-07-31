from app import create_app, db

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("Database initialized!")
    except Exception as e:
        print(f"Error creating database: {e}")
        # Consider logging the error or taking other actions
