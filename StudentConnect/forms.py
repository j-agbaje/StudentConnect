from collections.abc import Sequence
from flask_login import current_user
from typing import Any, Mapping
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField,BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from StudentConnect.models import User





class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    school = StringField("University Name", validators=[DataRequired()])
    primary_language = StringField("First Language", validators=[DataRequired()])
    other_language = StringField("Other Languages")
    country = StringField('Country of Origin', validators=[DataRequired()])
    course = StringField('Major/Field of Study', validators=[DataRequired()])
    mobile_number = StringField('Mobile Number(with country code)', validators=[Length(max=15)])
    whatsapp_number = StringField('WhatsApp Number(with country code)', validators=[Length(max=15)])
    instagram_handle = StringField('Instagram Handle', validators=[Length(max=50)])
    linkedin_handle = StringField('LinkedIn Handle', validators=[Length(max=50)])
    interests = StringField('Interests', validators=[Length(max=500)])
    bio = TextAreaField('Bio(Short description of you)', validators=[Length(max=2000)])
    profile_picture = FileField("Profile Picture", validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This Username is already taken. Please use a different username.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already associated with an account. Please use a different email.')
        

class EditProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"class": "required"})
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"class": "required"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"class": "required"})
    school = StringField("University Name", validators=[DataRequired()], render_kw={"class": "required"})
    primary_language = StringField("First Language", validators=[DataRequired()], render_kw={"class": "required"})
    other_language = StringField("Other Languages", render_kw={"class": "optional"})
    country = StringField('Country of Origin', validators=[DataRequired()], render_kw={"class": "required"})
    course = StringField('Major/Field of Study', validators=[DataRequired()], render_kw={"class": "required"})
    mobile_number = StringField('Mobile Number(with country code)', validators=[Length(max=15)], render_kw={"class": "optional"})
    whatsapp_number = StringField('WhatsApp Number(with country code)', validators=[Length(max=15)], render_kw={"class": "optional"})
    instagram_handle = StringField('Instagram Handle', validators=[Length(max=50)], render_kw={"class": "optional"})
    linkedin_handle = StringField('LinkedIn Handle', validators=[Length(max=50)], render_kw={"class": "optional"})
    interests = StringField('Interests', validators=[Length(max=500)], render_kw={"class": "optional"})
    profile_picture = FileField("Update Profile Picture", validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    bio = TextAreaField('Bio(Short description of you)', validators=[Length(max=1000)], render_kw={"class": "optional", "rows": 5, "cols": 50, "placeholder": "Tell us about yourself in 500 characters or less..."})  # Bio field
    submit = SubmitField('Save')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This Username is already taken. Please use a different username.')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This Email is already registered. Please choose a different email.')