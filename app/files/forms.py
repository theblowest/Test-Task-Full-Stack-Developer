from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired

class FileInfoForm(FlaskForm):
    """Form for displaying and editing file information."""
    name = StringField('File Name', validators=[DataRequired()])
    submit = SubmitField('Save Changes')


class FileUploadForm(FlaskForm):
    """Form for uploading a file."""
    file = FileField('Select File', validators=[DataRequired()])
    submit = SubmitField('Upload')


class FileDownloadForm(FlaskForm):
    """Form for downloading a file."""
    submit = SubmitField('Download File')