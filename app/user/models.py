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
        """Метод для установки пароля с хэшированием."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Метод для проверки пароля."""
        return check_password_hash(self.password, password)

    def is_admin(self):
        """Метод для проверки, является ли пользователь администратором."""
        return self.role == 'admin'

    def set_role(self, role):
        """Метод для изменения роли пользователя."""
        allowed_roles = ['admin', 'user']
        if role not in allowed_roles:
            raise ValueError(f"Недопустимая роль: {role}. Допустимые роли: {allowed_roles}")
        self.role = role
        db.session.commit()

   # Метод get_id для Flask-Login
    def get_id(self):
        return str(self.id)