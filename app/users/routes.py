from flask import Blueprint, render_template, redirect, url_for, flash, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required  # Import Flask-Login components

from .. import bcrypt
import os

from ..forms import LoginForm, RegisterForm
from ..models import User

users = Blueprint("users",
                  __name__,
                  template_folder="template",
                  static_folder="static")


# Login page
@users.route('/login', methods=['GET', 'POST'])
def login():
  # if user is authenticated redirect to the accounts page
  if current_user.is_authenticated:
    return redirect(url_for('social.profile', user_id=current_user.id))

  form = LoginForm()
  #send received data to the database for verification, throw messages if not verified
  if form.validate_on_submit():
    user = User.objects(username=form.username.data).first()
    if user is None:
      flash("Login failed, username does not exist")
    elif not bcrypt.check_password_hash(user.password, form.password.data):
      flash("Login failed, please check email and password")
    else:
      login_user(user)
      return redirect(url_for('users.account'))
  return render_template('login.html', form=form)


# Logout route when logged in, sends you back to index page
@users.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('main.index'))


# Register Page
@users.route('/register', methods=['GET', 'POST'])
# Send user to accounts page once info verified
def register():
  if current_user.is_authenticated:
    return redirect(url_for("social.feed"))

  form = RegisterForm()
  # send info recieved for verification and acceptablity
  if form.validate_on_submit():
    user_pwd = bcrypt.generate_password_hash(
      form.password.data).decode('utf-8')
    user = User(username=form.username.data,
                email=form.email.data,
                password=user_pwd)

    # SET DEFAULT IMAGE
    # with open('static/default.jpg', 'rb') as imagefile:
    #   # Read the contents of the file
    #   content = io.BytesIO(imagefile.read())
    #   filename = 'default.jpg'
    #   content_type = 'image/jpeg'
    #   user.profile_pic.put(content,
    #                        content_type=content_type,
    #                        filename=filename)

    # Save user into DB
    user.save()
    flash(
      "Congratulations, you've been registered and can now login to your account"
    )
    return redirect(url_for("users.login"))
  return render_template('register.html', form=form)


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
  # Now, account will display user's posts (NO DO THAT IN THE PROFILE PAGE WITHT THE THE FOLLOWERS)
  # This can be called profile instead of account (both work)
  return render_template('account.html')


# Users page
@users.route('/users', methods=['GET'])
@login_required
def get_users():
  return list(User.objects.filter(id__ne=current_user.id))


@users.route('/get_all_users', methods=['GET'])
def get_all_users():
  unfollowed = []
  unfollowed.append(current_user)
  for user in User.objects.all():
    if user.username != current_user.username and user not in current_user.following:
      unfollowed.append(user)

  return render_template('all_users.html',
                         unfollowed=unfollowed,
                         followed=current_user.following)


@users.route('/fetch_profile_image/<filename>')
def fetch_profile_img(filename):
  return send_from_directory(os.path.join(os.getcwd(), 'app', 'static'),
                             filename)
