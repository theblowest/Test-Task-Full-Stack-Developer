from logging.handlers import RotatingFileHandler
import os
from flask_sqlalchemy import SQLAlchemy
import werkzeug
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv

from app.database import db
from app.user.models import User

load_dotenv()

# Create a Flask app instance
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_pyfile("config.py")

# Configure logging
if not app.debug:  # Logs are written only in production mode
    # Create a handler for logs
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.INFO)
    # Log format
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    # Add handler to the app
    app.logger.addHandler(file_handler)

# Initialize the database
db.init_app(app)
with app.app_context():
    db.create_all()

# Configure migrations
migrate = Migrate(app, db, render_as_batch=True)

# Import routes
from app.user.views import *
from app.admin.views import *
from app.main.views import *

# Command for automatic migration
@app.cli.command("migrate")
def auto_migrate():
    os.system("flask db migrate -m 'Auto-migration'")
    os.system("flask db upgrade")

# Error handler
@app.errorhandler(werkzeug.exceptions.NotFound)
def custom_404(exc):
    return "<h1>Custom 404</h1>", exc.code