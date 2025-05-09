from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User, DataType


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class DataUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    data_type = SelectField('Data Type', choices=[(dt.value, dt.name) for dt in DataType], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=500)])
    file = FileField('File', validators=[
        FileAllowed(['csv', 'xlsx', 'txt', 'json'], 'Only CSV, Excel, Text, or JSON files are allowed!')
    ])
    submit = SubmitField('Upload Data')

class StudySessionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    date = StringField('Date', validators=[DataRequired()])
    duration = StringField('Duration (minutes)', validators=[DataRequired()])
    content = TextAreaField('Notes', validators=[Length(max=1000)])
    submit = SubmitField('Save Study Session')
