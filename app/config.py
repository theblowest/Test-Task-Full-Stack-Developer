import os

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG")
PORT = os.getenv("PORT")
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
BASE_DIR = os.getenv("BASE_DIR")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS")
MAX_FILE_SIZE = os.getenv("MAX_FILE_SIZE")