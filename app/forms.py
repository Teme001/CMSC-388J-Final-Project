from flask_login import current_user
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, Length, Email, EqualTo, NumberRange, ValidationError, Optional
from .models import User
from . import bcrypt

# MMMM
# from . import bcrypt, app


# Search box - user can search Users by its id (I guess :V)
class SearchForm(FlaskForm):
  seaerch_query = StringField(
    "Query", validators=[InputRequired(),
                         Length(min=1, max=100)])


# LOGIN FORM
class LoginForm(FlaskForm):
  username = StringField("Username",
                         validators=[InputRequired(),
                                     Length(min=1, max=40)])
  password = PasswordField("Password", validators=[InputRequired()])
  submit = SubmitField("Login", render_kw={"class": "submit-class"})


# REGISTRATION FORM
class RegisterForm(FlaskForm):
  username = StringField("Username",
                         validators=[InputRequired(),
                                     Length(min=1, max=40)])
  email = StringField("Email", validators=[InputRequired(), Email()])
  password = PasswordField("Password", validators=[InputRequired()])
  confirm_password = PasswordField(
    "Confirm Password", validators=[InputRequired(),
                                    EqualTo("password")])
  submit = SubmitField("Sign Up")

  def validate_username(self, username):
    user = User.objects(username=username.data).first()
    if user is not None:
      raise ValidationError("Username is taken")

  def validate_email(self, email):
    email = User.objects(email=email.data).first()
    if email is not None:
      raise ValidationError("Account with this email already exists")


# UPDATE ACCOUNT SETTINGS
class UpdateAccountSettingsForm(FlaskForm):
  username = StringField("Username", validators=[Length(min=1, max=40)])
  email = StringField("Email", validators=[Email(), Length(min=1, max=40)])

  profile_pic = FileField(
    "Profile Picture",
    validators=[FileAllowed(["jpg", "png"], "Images Only!")])

  password = PasswordField("Pasword", validators=[Optional(), Length(min=1)])

  bio = TextAreaField("About", validators=[Length(min=0, max=500)])

  submit = SubmitField("Update")

  def validate_username(self, username):
    if username.data != current_user.username:
      user = User.objects(username=username.data).first()
      if user is not None:
        raise ValidationError("Username is taken")

  def validate_email(self, email):
    if email.data != current_user.email:
      user = User.objects(email=email.data).first()
      if user is not None:
        raise ValidationError("Email is taken")

  def validate_profile_pic(self, profile_pic):
    if profile_pic.data:
      filename = secure_filename(profile_pic.data.filename)
      if not filename.lower().endswith((".jpg", ".png")):
        raise ValidationError("File must be a jpg or a png")

  def validate_password(self, password):
    if password.data:
      if not bcrypt.check_password_hash(current_user.password, password.data):
        raise ValidationError("Password is incorrect")


#    user = User.objects(username=current_user.username).first()


class UpdateUsernameForm(FlaskForm):
  username = StringField("Username",
                         validators=[InputRequired(),
                                     Length(min=1, max=40)])
  submit = SubmitField("Update")

  def validate_username(self, username):
    user = User.objects(username=username.data).first()
    if user is not None:
      raise ValidationError("Username is taken")


# UPDATE EMAIL FORM
class UpdateEmailForm(FlaskForm):
  email = StringField("Email", validators=[InputRequired(), Email()])
  submit = SubmitField("Update")

  def validate_email(self, email):
    email = User.objects(email=email.data).first()
    if email is not None:
      raise ValidationError("Account with this email already exists")


# UPDATE PROFILE PIC FORM
class UpdateProfilePicForm(FlaskForm):
  profile_pic = FileField(
    "Profile Picture",
    validators=[FileRequired(),
                FileAllowed(["jpg", "png"], "Images Only!")])
  submit = SubmitField("Update")

  def validate_profile_pic(self, profile_pic):
    filename = secure_filename(profile_pic.data.filename)
    if not filename.lower().endswith((".jpg", ".png")):
      raise ValidationError("File must be a jpg or a png")


class PostForm(FlaskForm):
  title = StringField("Title", validators=[Length(min=0, max=40)])
  body = StringField("Body", [Length(min=1, max=500)])
  image = FileField("Picture",
                    validators=[FileAllowed(["jpg", "png"], "Images Only!")])
  submit = SubmitField("Post")

  def validate_picture(self, image):
    filename = secure_filename(image.data.filename)
    if not filename.lower().endswith((".jpg", ".png")):
      raise ValidationError("File must be a jpg or a png")
