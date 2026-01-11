from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    check_password = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # Logic to prevent duplicate usernames
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken.')

    # Logic to prevent duplicate emails
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered.')
        
class AddDeviceForm(FlaskForm):
    device_name = StringField('Device Name', validators=[DataRequired()])
    submit = SubmitField('Add Device')

class EditDeviceForm(FlaskForm):
    device_name = StringField('New Device Name', validators=[DataRequired()])
    submit = SubmitField('Save Changes')
    
class AddGuestForm(FlaskForm):
    email = StringField('Guest Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Grant Access')