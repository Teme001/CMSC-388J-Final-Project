import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from mongoengine import connect

from .main import main
from .models import load_user

bcrypt = Bcrypt()

database = os.environ['MONGODB_URI']


def page_not_found(e):
  return render_template("404.html"), 404


def create_app(test_config=None):
  app = Flask(__name__)

  connect(db='App', host={database}, alias='default')
  client = MongoClient(os.environ.get('MONGODB_URI'))
  try:
    client.admin.command('ping')
    print(client.list_database_names())
    print("Pinged your deployment. You successfully connected to MongoDB!")
  except Exception as e:
    print(e)
  # db = client.test
  # chat_collection = db.chats


#  users_collection = client.App
# test = client.test1
# socketio = SocketIO(app, cors_allowed_origins="*")

# app.config.from_pyfile("config.py", silent=False)
# if test_config is not None:
#   app.config.update(test_config)

  app.config['SECRET_KEY'] = b'r\\\xe5Xy\x93{\x07\xa0\xe8\xaajQ\xca\xd6\xbd'

  app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
  )

  from .users.routes import users
  from .social.routes import social
  bcrypt.init_app(app)

  app.register_blueprint(main)
  app.register_blueprint(users)
  app.register_blueprint(social)

  login_manager = LoginManager(app)
  login_manager.login_view = "users.login"
  login_manager.user_loader(load_user)

  return app
