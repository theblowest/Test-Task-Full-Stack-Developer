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

# Настроим логирование
logging.basicConfig(level=logging.INFO)
# Настройка Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.init_app(app)

# Функция загрузки пользователя по ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Загрузка пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_file_by_id(file_id):
    try:
        # Попытка найти файл по его ID
        file = File.query.get(file_id)
        if file is None:
            raise NoResultFound  # Если файл не найден, выбрасываем исключение
        return file
    except NoResultFound:
        # Логирование ошибки, если файл не найден
        logging.error(f"Файл с ID {file_id} не найден.")
        return None

# Декоратор для проверки роли пользователя
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login')) 
        if current_user.role != 'admin':
            return redirect(url_for('user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Главная страница
@app.route('/')
def home():
    return render_template("index.html") 


# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Используем форму для логина
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        # Проверяем, существует ли пользователь и правильность пароля
        if user and check_password_hash(user.password, password):
            login_user(user)  # Используем Flask-Login для входа
            logging.info(f"User {username} logged in successfully with role {user.role}.")
            if user.role == 'admin' or current_user.is_admin():
                return redirect(url_for('admin_dashboard'))  # Страница админа
            else:
                return redirect(url_for('user_dashboard'))  # Страница пользователя
        else:
            logging.warning(f"Failed login attempt for {username}. Incorrect username or password.")
            flash("Неверное имя пользователя или пароль", "error")
            return redirect(url_for('login'))  # Перенаправление на страницу логина

    return render_template("users/login.html", form=form)

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm() 
    if form.validate_on_submit():
        first_name = form.first_name.data
        username = form.username.data
        password = form.password.data
        
        # Проверяем, существует ли уже пользователь с таким именем
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists! Please choose a different one.", "error")
            return redirect(url_for('register'))
        
        # Хешируем пароль
        hashed_password = generate_password_hash(password)
        
        # Создаем нового пользователя
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

# Страница списка файлов для пользователей
@app.route('/files')
@login_required
def files():
    file_list = File.query.all()  # Получаем список всех файлов
    return render_template("files/list.html", files=file_list)
