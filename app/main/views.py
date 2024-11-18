import logging
from flask import flash, render_template, redirect, url_for, request, session, send_file
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from app import app
from werkzeug.security import check_password_hash, generate_password_hash
from app.files.models import DownloadLog, File
from app.user.forms import RegistrationForm, LoginForm
from app.user.models import User
from app.database import db
from sqlalchemy.orm.exc import NoResultFound
from functools import wraps
from flask_login import login_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.init_app(app)

# Function to load a user by ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_file_by_id(file_id):
    try:
        # Attempt to find the file by its ID
        file = File.query.get(file_id)
        if file is None:
            raise NoResultFound  # If the file is not found, raise an exception
        return file
    except NoResultFound:
        # Log an error if the file is not found
        logging.error(f"File with ID {file_id} not found.")
        return None

# Decorator to check user role
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login')) 
        if current_user.role != 'admin':
            return redirect(url_for('user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Home page
@app.route('/')
def home():
    return render_template("index.html") 

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Use the login form
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            login_user(user)  # Use Flask-Login to log the user in
            logging.info(f"User {username} logged in successfully with role {user.role}.")
            if user.role == 'admin' or current_user.is_admin():
                return redirect(url_for('admin_dashboard'))  # Admin dashboard page
            else:
                return redirect(url_for('user_dashboard'))  # User dashboard page
        else:
            logging.warning(f"Failed login attempt for {username}. Incorrect username or password.")
            flash("Incorrect username or password", "error")
            return redirect(url_for('login'))  # Redirect back to the login page

    return render_template("users/login.html", form=form)

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm() 
    if form.validate_on_submit():
        first_name = form.first_name.data
        username = form.username.data
        password = form.password.data
        
        # Check if a user with this username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists! Please choose a different one.", "error")
            return redirect(url_for('register'))
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Create a new user
        user = User(first_name=first_name, username=username, password=hashed_password, role='user')
        
        try:
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred during registration: {e}", "error")
            return redirect(url_for('register'))

    return render_template("users/registration.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# User files list page
@app.route('/files')
@login_required
def files():
    file_list = File.query.all()  # Get a list of all files
    return render_template("files/list.html", files=file_list)
