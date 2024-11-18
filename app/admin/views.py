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

# Check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Decorator to check admin rights
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in.', 'danger')
            return redirect(url_for('login'))
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin():
            flash('You do not have access to this page.', 'danger')
            return redirect(url_for('user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Admin file upload
@app.route('/admin/upload', methods=['POST'])
@login_required
@admin_required
def admin_upload_file():
    try:
        uploaded_file = request.files.get('file')
        if not uploaded_file or uploaded_file.filename == '':
            flash('No file selected for upload!', 'danger')
            return redirect(url_for('admin_dashboard'))

        if not allowed_file(uploaded_file.filename):
            flash('Invalid file format!', 'danger')
            return redirect(url_for('admin_dashboard'))

        if request.content_length and request.content_length > MAX_FILE_SIZE:
            flash('File is too large!', 'danger')
            return redirect(url_for('admin_dashboard'))

        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Ensure unique filename if file already exists
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
        flash('File successfully uploaded!', 'success')
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        flash('An error occurred while uploading the file.', 'danger')
    return redirect(url_for('admin_dashboard'))

# Admin file download
@app.route('/admin/download/<int:file_id>', methods=['GET'])
@login_required
def admin_download_file(file_id):
    try:
        # Get file object from the database
        file = File.query.get_or_404(file_id)

        # Check file accessibility
        if not file.accessible_to_users:
            flash('You do not have access to this file.', 'danger')
            return redirect(url_for('admin_dashboard'))

        # Check if file exists on the server
        if not os.path.isfile(file.path):
            flash('File not found on the server.', 'danger')
            return redirect(url_for('admin_dashboard'))

        # Increment download count
        file.downloads += 1
        db.session.commit()

        # Log the download event
        download_log = DownloadLog(user_id=current_user.id, file_id=file.id)
        db.session.add(download_log)
        db.session.commit()

        # Send the file to the client
        directory = os.path.dirname(file.path)
        filename = os.path.basename(file.path)
        return send_from_directory(directory=directory, path=filename, as_attachment=True)

    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        flash('An error occurred while downloading the file.', 'danger')
        return redirect(url_for('admin_dashboard'))

# Admin file deletion
from flask import request, jsonify

@app.route('/admin/delete/<int:file_id>', methods=['POST'])
@login_required
def admin_delete_file(file_id):
    try:
        # Get the file from the database
        file = File.query.get_or_404(file_id)

        # Check if file exists
        if os.path.exists(file.path):
            os.remove(file.path)  # Delete file from the server
        else:
            flash('File not found on the server.', 'danger')

        # Delete the file from the database
        db.session.delete(file)
        db.session.commit()

        # Return a successful JSON response
        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()  # Rollback the transaction on error
        logging.error(f"Error deleting file: {e}")
        flash('An error occurred while deleting the file.', 'danger')
        return jsonify({'success': False})

# Admin dashboard
@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():
    files = File.query.all()  # List of all files
    users = User.query.all()  # List of all users

    if request.method == 'POST':
        # Handle file actions
        file_id = request.form.get('file_id')
        action = request.form.get('action')
        try:
            if action == 'delete' and file_id:
                file = File.query.get_or_404(file_id)
                if os.path.exists(file.path):
                    os.remove(file.path)  # Delete file from the filesystem
                db.session.delete(file)  # Delete file record from the database
                db.session.commit()
                flash('File successfully deleted.', 'success')
            elif action == 'toggle_availability' and file_id:
                file = File.query.get_or_404(file_id)
                file.accessible_to_users = not file.accessible_to_users  # Toggle file accessibility
                db.session.commit()
                flash('File availability changed.', 'success')
        except Exception as e:
            logging.error(f"Error in admin_dashboard: {e}")
            flash('An error occurred while processing the request.', 'danger')

    return render_template('admin/dashboard.html', files=files, users=users)


# Handler for changing user role
@app.route('/admin/change_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_change_role(user_id):
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')

    if action == 'toggle_role':
        if user.role == 'user':
            user.role = 'admin'
            flash(f'{user.username} is now an administrator.', 'success')
        else:
            user.role = 'user'
            flash(f'{user.username} is now a regular user.', 'success')
        
        db.session.commit()
        
    return redirect(url_for('admin_dashboard'))