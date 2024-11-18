from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField(
        label="Repeat Password",  
        validators=[DataRequired(), Length(min=6), EqualTo('password', message="Passwords must match")]
    )
    submit = SubmitField('Register')