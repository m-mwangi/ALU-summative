from app import create_app, db
from flask_migrate import Migrate
import click

app = create_app()
migrate = Migrate(app, db)

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()

@app.cli.command()
def migrate_db():
    """Run migrations."""
    with app.app_context():
        from flask_migrate import upgrade
        upgrade()

if __name__ == "__main__":
    app.run()
