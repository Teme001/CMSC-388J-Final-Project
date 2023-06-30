import os
import io
import base64
import requests
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from .. import bcrypt
from flask_login import current_user, login_user, LoginManager, UserMixin, logout_user, login_required
from werkzeug.utils import secure_filename
from ..forms import PostForm, UpdateAccountSettingsForm
from ..models import User, Follow, Post

from flask import jsonify

Weather_api = os.environ.get('weather_api')
social = Blueprint("social", __name__, template_folder="templates")


# Search bar result
@social.route('/search_users', methods=['GET'])
def search_users():
  query = request.args.get('query', '')
  matching_users = User.objects(username__icontains=query)
  return render_template('search_results.html', users=matching_users)


@social.route('/follow/<follower_name>/<following_name>',
              methods=['POST'],
              endpoint='follow_user')
@login_required
def follow(follower_name, following_name):
  follower = User.objects.get(username=follower_name)
  following = User.objects.get(username=following_name)

  # Add the following user to the follower's following list
  if following not in follower.following:
    follower.following.append(following)
    follower.save()

  return redirect(url_for('users.get_all_users'))


# ------SOMEHOW PROFILE DOES NOT WORK------
# Add a new route for displaying user profiles
@social.route('/profile/<user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
  user = User.objects(username=user_id).first()

  if not user:
    return jsonify({'error': 'User not found'}), 404
  followers_count = 0
  for follow in Follow.objects.all():
    if user in follow.following:
      followers_count += 1
  following_count = len(user.following)

  return render_template('profile.html',
                         user=user,
                         followers_count=followers_count,
                         following_count=following_count)


# Feeds page route
@social.route('/feed', methods=['GET', 'POST'])
@login_required
def feed():
  url = f'http://api.openweathermap.org/data/2.5/forecast?id=524901&appid={Weather_api}'
  response = requests.get(url)
  weather_data = response.json()

  if response.status_code != 200:
    logging.error(
      f"Weather API request failed with status code {response.status_code}: {weather_data}"
    )
    weather_data = None
  elif 'list' not in weather_data:
    logging.error(f"Weather API response missing 'list' key: {weather_data}")
    weather_data = None
  else:
    weather_data = weather_data['list'][0]['main']

  posts = list(Post.objects)

  # posts.append(Post.objects.filter(author=current_user))

  for follower in current_user.following:
    if follower != current_user:
      posts.extend(Post.objects.filter(author=follower))

  form = PostForm()

  if request.method == 'POST':
    if form.validate_on_submit():
      user_post = Post()
      user_post.author = current_user
      user_post.title = form.title.data
      user_post.body = form.body.data
      user_post.image = None

      if form.image.data:
        image = form.image.data
        image_name = secure_filename(image.filename)
        image_path = os.path.join("images", image_name)
        image.save(image_path)

        user_post.image = image_path  # Set the image field on the Post

      user_post.save()  # Save the post whether or not an image was uploaded
      redirect(request.path)

  return render_template('feed.html',
                         weather_data=weather_data,
                         posts=posts,
                         form=form)


@social.route('/followers/<user_id>', methods=['GET'])
@login_required
def get_followers(user_id):
  user = User.objects(id=user_id).first()

  if not user:
    return jsonify({'error': 'User not found'}), 404

  followers = []
  for follow in Follow.objects.all():
    if user in follow.following:
      followers.append(follow)
  return render_template('followers.html', followers=followers)


@social.route('/following/<user_id>', methods=['GET'])
@login_required
def get_following(user_id):
  user = User.objects(id=user_id).first()

  if not user:
    return jsonify({'error': 'User not found'}), 404

  following = user.following
  return render_template('following.html', following=following)


# Settings page - TODO
@social.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():

  # Load User profile
  if current_user.profile_pic:
    img_data = current_user.profile_pic.read()
    img_b64 = base64.b64encode(img_data).decode('utf-8')
  else:
    img_b64 = None

  # Get user from this session
  user_object = User.objects(username=current_user.username).first()

  # Load account form from forms.py
  update_account_form = UpdateAccountSettingsForm()

  # Update Account when submitted
  if update_account_form.validate_on_submit():
    # Check for username
    if user_object.username == update_account_form.username.data:
      new_username = user_object.username
    elif User.objects(
        username=update_account_form.username.data).first() is None:
      new_username = update_account_form.username.data
      user_object.modify(username=new_username)
    else:
      flash('User already exists!')
      return redirect(url_for('users.settings'))

    # Check for email
    if user_object.email == update_account_form.email.data:
      new_email = user_object.email
    elif User.objects(email=update_account_form.email.data).first() is None:
      new_email = update_account_form.email.data
      user_object.modify(email=new_email)
    else:
      flash('Email already exists!')
      return redirect(url_for('users.settings'))

    # Check for password
    if len(update_account_form.password.data) > 0:
      hashed = bcrypt.generate_password_hash(
        update_account_form.password.data).decode('utf-8')
      user_object.modify(password=hashed)

    # Check for profile picture and save locally
    if update_account_form.profile_pic.data:
      image = update_account_form.profile_pic.data
      image_name = secure_filename(image.filename)
      image_path = os.path.join("images", image_name)
      image.save(image_path)

      # Save on DB
      with open(image_path, "rb") as img_file:
        user_object.profile_pic.replace(img_file, content_type=image.mimetype)

    # Check for bio
    if len(update_account_form.bio.data) > 0:
      new_bio = update_account_form.bio.data
      user_object.modify(bio=new_bio)

    # Save user to the DB with the fields modified
    user_object.save()

    login_user(user_object, remember=True)

  return render_template('settings.html',
                         user=user_object,
                         update_account_form=update_account_form,
                         image=img_b64)


# Chat page
@social.route('/chat')
@login_required
def chat():
  return render_template('chat.html')


@social.route('/marketplace', methods=['GET', 'POST'])
def marketplace():
  search_term = request.args.get('search', default='laptop', type=str)
  url = "https://api.rainforestapi.com/request"
  parameters = {
    "api_key": os.environ['MARKETPLACE_API'],
    "type": "search",
    "amazon_domain": "amazon.com",
    "search_term": search_term
  }
  response = requests.get(url, parameters)
  products = response.json()['search_results']
  return render_template('marketplace.html', products=products)


@social.route('/videos')
def videos():
  url = "https://www.googleapis.com/youtube/v3/search"
  search_term = request.args.get('search',
                                 default='Never gonna give you up',
                                 type=str)
  parameters = {
    "key": os.environ['YOUTUBE_API'],
    "q": search_term,
    "type": "video",
    "part": "snippet",
    "maxResults": "10"
  }
  response = requests.get(url, params=parameters, verify=False)
  videos = response.json()['items']
  return render_template('videos.html', videos=videos)
