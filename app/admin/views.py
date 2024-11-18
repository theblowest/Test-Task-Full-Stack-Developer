import os
from datetime import datetime
from flask import flash, request, render_template, redirect, send_from_directory, url_for
from flask_login import login_required, current_user
from app import app
from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOAD_FOLDER
from app.database import db
from app.files.models import DownloadLog, File
from werkzeug.utils import secure_filename
from functools import wraps
import logging

from app.user.models import User

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Проверка расширений
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Декоратор проверки прав администратора
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Пожалуйста, войдите в систему.', 'danger')
            return redirect(url_for('login'))
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin():
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Загрузка файла
@app.route('/admin/upload', methods=['POST'])
@login_required
@admin_required
def admin_upload_file():
    try:
        uploaded_file = request.files.get('file')
        if not uploaded_file or uploaded_file.filename == '':
            flash('Не выбран файл для загрузки!', 'danger')
            return redirect(url_for('admin_dashboard'))

        if not allowed_file(uploaded_file.filename):
            flash('Недопустимый формат файла!', 'danger')
            return redirect(url_for('admin_dashboard'))

        if request.content_length and request.content_length > MAX_FILE_SIZE:
            flash('Файл слишком большой!', 'danger')
            return redirect(url_for('admin_dashboard'))

        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Уникальное имя файла, если он уже существует
        if os.path.exists(file_path):
            filename = f"{int(datetime.now().timestamp())}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)

        uploaded_file.save(file_path)
        new_file = File(
            name=filename,
            path=file_path,
            description=request.form.get('description', ''),
            user_id=current_user.id
        )
        db.session.add(new_file)
        db.session.commit()
        flash('Файл успешно загружен!', 'success')
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла: {e}")
        flash('Произошла ошибка при загрузке файла.', 'danger')
    return redirect(url_for('admin_dashboard'))

# Скачивание файла
@app.route('/admin/download/<int:file_id>', methods=['GET'])
@login_required
def admin_download_file(file_id):
    try:
        # Получаем объект файла из базы данных
        file = File.query.get_or_404(file_id)

        # Проверяем доступность файла
        if not file.accessible_to_users:
            flash('Вы не имеете доступа к этому файлу.', 'danger')
            return redirect(url_for('admin_dashboard'))

        # Проверяем наличие файла в файловой системе
        if not os.path.isfile(file.path):  # Проверяем наличие файла по его полному пути
            flash('Файл не найден на сервере.', 'danger')
            return redirect(url_for('admin_dashboard'))

        # Увеличиваем количество загрузок
        file.downloads += 1  # Инкрементируем вручную
        db.session.commit()  # Сохраняем изменения в базе данных

        # Логируем событие скачивания
        download_log = DownloadLog(user_id=current_user.id, file_id=file.id)
        db.session.add(download_log)
        db.session.commit()

        # Отправляем файл клиенту
        directory = os.path.dirname(file.path)  # Получаем каталог файла
        filename = os.path.basename(file.path)  # Получаем имя файла
        return send_from_directory(directory=directory, path=filename, as_attachment=True)

    except Exception as e:
        logging.error(f"Ошибка при скачивании файла: {e}")
        flash('Произошла ошибка при скачивании файла.', 'danger')
        return redirect(url_for('admin_dashboard'))

# Удаление файла
from flask import request, jsonify

@app.route('/admin/delete/<int:file_id>', methods=['POST'])
@login_required
def admin_delete_file(file_id):
    try:
        # Получаем файл из базы данных
        file = File.query.get_or_404(file_id)

        # Проверяем, что файл существует
        if os.path.exists(file.path):
            os.remove(file.path)  # Удаляем файл с сервера
        else:
            flash('Файл не найден на сервере.', 'danger')

        # Удаляем файл из базы данных
        db.session.delete(file)
        db.session.commit()

        # Возвращаем успешный JSON-ответ
        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()  # Откатываем транзакцию при ошибке
        logging.error(f"Ошибка при удалении файла: {e}")
        flash('Произошла ошибка при удалении файла.', 'danger')
        return jsonify({'success': False})


# Панель администратора
@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():
    files = File.query.all()  # Список всех файлов
    users = User.query.all()  # Список всех пользователей

    if request.method == 'POST':
        # Обработка действий с файлами
        file_id = request.form.get('file_id')
        action = request.form.get('action')
        try:
            if action == 'delete' and file_id:
                file = File.query.get_or_404(file_id)
                if os.path.exists(file.path):
                    os.remove(file.path)  # Удаляем файл из файловой системы
                db.session.delete(file)  # Удаляем запись о файле из базы данных
                db.session.commit()
                flash('Файл успешно удалён.', 'success')
            elif action == 'toggle_availability' and file_id:
                file = File.query.get_or_404(file_id)
                file.accessible_to_users = not file.accessible_to_users  # Переключаем доступность файла
                db.session.commit()
                flash('Доступность файла изменена.', 'success')
        except Exception as e:
            logging.error(f"Ошибка в admin_dashboard: {e}")
            flash('Произошла ошибка при обработке запроса.', 'danger')

    return render_template('admin/dashboard.html', files=files, users=users)


# Обработчик смены роли пользователя
@app.route('/admin/change_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_change_role(user_id):
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')

    if action == 'toggle_role':
        if user.role == 'user':
            user.role = 'admin'
            flash(f'{user.username} теперь администратор.', 'success')
        else:
            user.role = 'user'
            flash(f'{user.username} теперь обычный пользователь.', 'success')
        
        db.session.commit()
        
    return redirect(url_for('admin_dashboard'))