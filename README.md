# File Sharing Web Application

This is a file sharing web application developed with Python and Flask. The system supports two types of users: regular users and admins. Admins can upload files to the server, manage access for regular users, and monitor download statistics. Regular users can view and download files to which they have access.

## Features

### Admin Features:
- **File Upload**: Admins can upload files to the server.
- **File Management**: Admins can delete any file and its record from the server.
- **User Access Control**: Admins can regulate which files are accessible for regular users.
- **File Statistics**: Admins can view a list of files along with their download counts.

### Regular User Features:
- **File Access**: Regular users can view and download files that they have access to (based on admin settings).
- **Registration**: Regular users can register via a login form with username and password.

### Additional Features:
- **User Authentication**: Users can log in with a username and password. Passwords are securely stored using bcrypt.
- **File Download Logging**: Every file download is logged with the user’s name, file name, and download time.
  
## Technologies Used
- **Backend**: Flask
- **Database**: SQLite or MySQL (SQLAlchemy ORM for database management)
- **Authentication**: Password-based login with bcrypt for secure password storage.
- **File Storage**: Files are stored in the local file system.
- **Background Tasks**: (Optional) Email notifications using SMTP for activity logging.
- **Database Migrations**: Alembic for handling database migrations.

## Installation

### Prerequisites
1. Python 3.x
2. pip (Python package installer)

### Clone the repository:
```bash
git https://github.com/theblowest/Test-Task-Full-Stack-Developer.git