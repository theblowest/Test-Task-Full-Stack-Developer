from flask_login import UserMixin
from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Enum
from enum import Enum as PyEnum


# class Role(PyEnum):
#     user = 'user'
#     admin = 'admin'


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    password = Column(String(128), nullable=False)
    # role = Column(Enum(Role), default=Role.user)
    role = Column(String(50), nullable=False, default='user') 
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Method to set the password with hashing."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Method to check the password."""
        return check_password_hash(self.password, password)

    def is_admin(self):
        """Method to check if the user is an administrator."""
        return self.role == 'admin'

    def set_role(self, role):
        """Method to change the user's role."""
        allowed_roles = ['admin', 'user']
        if role not in allowed_roles:
            raise ValueError(f"Invalid role: {role}. Allowed roles: {allowed_roles}")
        self.role = role
        db.session.commit()

    # get_id method for Flask-Login
    def get_id(self):
        return str(self.id)