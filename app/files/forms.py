from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired

class FileInfoForm(FlaskForm):
    """Форма для отображения и редактирования информации о файле."""
    name = StringField('File Name', validators=[DataRequired()])
    submit = SubmitField('Save Changes')


class FileUploadForm(FlaskForm):
    """Форма для загрузки файла."""
    file = FileField('Select File', validators=[DataRequired()])
    submit = SubmitField('Upload')


class FileDownloadForm(FlaskForm):
    """Форма для скачивания файла."""
    submit = SubmitField('Download File')
