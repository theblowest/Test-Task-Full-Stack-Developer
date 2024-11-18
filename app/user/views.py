import os
from flask import flash, render_template, redirect, request, send_file, send_from_directory, session, url_for
from app import app
from app.database import db
from app.files.models import DownloadLog, File, FileAccess
from app.main.views import login_required
from app.user.forms import LoginForm, RegistrationForm
from app.user.models import User
from flask_login import login_user, current_user

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'uploads')  # Path to the 'app/uploads' folder

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

    # Get the list of all files available to users
    files = File.query.filter_by(accessible_to_users=True).all()

    # If the user sent a POST request (file download)
    if request.method == 'POST':
        file_id = request.form.get('file_id')  # Get the file ID from the form
        file = File.query.get(file_id)

        if file and file.accessible_to_users:
            file_path = os.path.join(UPLOAD_FOLDER, file.path)  # Construct the full file path

            if os.path.exists(file_path):  # Check if the file exists
                try:
                    # Log the download
                    log = DownloadLog(user_id=current_user.id, file_id=file.id)
                    db.session.add(log)
                    file.increment_downloads()  # Increase the download count
                    db.session.commit()

                    # Send the file to the user
                    return send_file(file_path, as_attachment=True)
                except Exception as e:
                    flash(f"An error occurred while downloading: {e}", "error")
            else:
                flash("File not found.", "error")

    # Render the page with files
    return render_template('users/dashboard.html', files=files)

@app.route('/download/<int:file_id>', methods=['GET'])
@login_required
def download_user_file(file_id):
    file = File.query.get_or_404(file_id)

    # Check access rights through FileAccess
    access_record = FileAccess.query.filter_by(file_id=file.id, user_id=current_user.id).first()
    if not access_record:
        flash('You do not have permission to access this file.', 'danger')
        return redirect(url_for('user_dashboard'))

    # Log the download
    download_log = DownloadLog(user_id=current_user.id, file_id=file.id)
    db.session.add(download_log)
    db.session.commit()

    return send_from_directory(directory=UPLOAD_FOLDER, filename=file.name, as_attachment=True)


# List of files for the user
@app.route('/files', methods=['GET'])
@login_required
def file_list():
    files = File.query.all()
    return render_template('files/list.html', files=files)