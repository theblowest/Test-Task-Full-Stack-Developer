import os
from flask import flash, render_template, redirect, request, send_file, send_from_directory, session, url_for
from app import app
from app.database import db
from app.files.models import DownloadLog, File, FileAccess
from app.main.views import login_required
from app.user.forms import LoginForm, RegistrationForm
from app.user.models import User
from flask_login import login_user, current_user

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'uploads')  # Путь к папке app/uploads

@app.route("/users")
def get_users():
    query = db.select(User)
    users = db.session.execute(query).scalars()
    return render_template("users/list.html", users=users)


@app.route("/users/<int:user_id>")
def user_detail(user_id):
    return render_template("users/detail.html", user_id=user_id)


@app.route('/user_dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():

    # Получаем список всех файлов, доступных для пользователей
    files = File.query.filter_by(accessible_to_users=True).all()

    # Если пользователь отправил POST-запрос (скачивание файла)
    if request.method == 'POST':
        file_id = request.form.get('file_id')  # Получаем ID файла из формы
        file = File.query.get(file_id)

        if file and file.accessible_to_users:
            file_path = os.path.join(UPLOAD_FOLDER, file.path)  # Формируем полный путь к файлу

            if os.path.exists(file_path):  # Проверяем, существует ли файл
                try:
                    # Логируем скачивание
                    log = DownloadLog(user_id=current_user.id, file_id=file.id)
                    db.session.add(log)
                    file.increment_downloads()  # Увеличиваем количество скачиваний
                    db.session.commit()

                    # Отправляем файл пользователю
                    return send_file(file_path, as_attachment=True)
                except Exception as e:
                    flash(f"Произошла ошибка при скачивании: {e}", "error")
            else:
                flash("Файл не найден.", "error")

    # Рендеринг страницы с файлами
    return render_template('users/dashboard.html', files=files)

@app.route('/download/<int:file_id>', methods=['GET'])
@login_required
def download_user_file(file_id):
    file = File.query.get_or_404(file_id)

    # Проверка прав доступа через FileAccess
    access_record = FileAccess.query.filter_by(file_id=file.id, user_id=current_user.id).first()
    if not access_record:
        flash('У вас нет прав для доступа к этому файлу.', 'danger')
        return redirect(url_for('user_dashboard'))

    # Логирование скачивания
    download_log = DownloadLog(user_id=current_user.id, file_id=file.id)
    db.session.add(download_log)
    db.session.commit()

    return send_from_directory(directory=UPLOAD_FOLDER, filename=file.name, as_attachment=True)



# Список файлов для пользователя
@app.route('/files', methods=['GET'])
@login_required
def file_list():
    files = File.query.all()
    return render_template('files/list.html', files=files)
