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

# Создаем экземпляр Flask приложения
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_pyfile("config.py")

# Настройка логирования
if not app.debug:  # Логи пишутся только в режиме продакшн
    # Создаём обработчик для логов
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.INFO)
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    # Добавляем обработчик в приложение
    app.logger.addHandler(file_handler)

# Инициализация базы данных
db.init_app(app)
with app.app_context():
    db.create_all()

# Настройка миграций
migrate = Migrate(app, db, render_as_batch=True)

# Подключение маршрутов
from app.user.views import *
from app.admin.views import *
from app.main.views import *

# Команда для автоматической миграции
@app.cli.command("migrate")
def auto_migrate():
    os.system("flask db migrate -m 'Auto-migration'")
    os.system("flask db upgrade")

# Обработчик ошибок
@app.errorhandler(werkzeug.exceptions.NotFound)
def custom_404(exc):
    return "<h1>Custom 404</h1>", exc.code