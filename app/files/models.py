from datetime import datetime
from app.database import db

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    downloads = db.Column(db.Integer, default=0)
    description = db.Column(db.String(255), nullable=True)
    accessible_to_users = db.Column(db.Boolean, default=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='uploaded_files')
    
    # Обновленные отношения с использованием back_populates
    download_logs = db.relationship('DownloadLog', back_populates='file', cascade='all, delete-orphan' ,lazy=True)

    def __repr__(self):
        return f'<File {self.name}>'

    def increment_downloads(self):
        """Increase download count by 1."""
        self.downloads += 1
        db.session.commit()


class DownloadLog(db.Model):
    __tablename__ = 'download_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    download_time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    # Обновленные отношения с использованием back_populates
    user = db.relationship('User', backref='download_activity')
    file = db.relationship('File', back_populates='download_logs')

    def __repr__(self):
        return f'<DownloadLog {self.download_time}>'


class FileAccess(db.Model):
    __tablename__ = 'file_access'

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    download_time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    file = db.relationship('File', backref='access_logs')
    user = db.relationship('User', backref='file_access_logs')