from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

from app.files import models
from app.user import models