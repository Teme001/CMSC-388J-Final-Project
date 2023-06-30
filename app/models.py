from flask_login import UserMixin
from flask import request
from flask_mongoengine import MongoEngine
# from . import login_manager

db = MongoEngine()


# @login_manager.user_loader
def load_user(user_id):
  return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
  username = db.StringField(max_length=40,
                            required=True,
                            unique=True,
                            min_length=1)
  email = db.EmailField(unique=True, required=True)
  password = db.StringField(required=True)
  profile_pic = db.ImageField(upload_to='avatar',
                              blank=True,
                              null=True,
                              default='default.jpg')
  following = db.ListField(
    db.ReferenceField('self', reverse_delete_rule=db.PULL))

  bio = db.StringField(min_length=3, max_length=500)

  # Returns unique string identifying our object
  def get_id(self):
    return self.username


class Follow(db.Document):
  follower = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)
  following = db.ReferenceField(User, reverse_delete_rule=db.CASCADE)


# Make a graph data structure that represents the user's friends, traverse with dijkstra to find
# user's friend efficiently. Nah, just a array containing all user's friend's id
# A Hash map?
#   users's friend =
#   {
#      user1: { friend1, friend2, friend3, ...}
#      user2: { friend2, friend3}
#      user3: { friend1 }
#   }


class Comment(db.Document):
  #   # author - A reference to the User who authored the comment.
  author = db.ReferenceField(User, required=True)

  #   # body - The main content of the comment.
  body = db.StringField(required=True, max_length=500)

  #   # likes -  An array of references to Users who have liked the comment.
  likes = db.ListField(db.ReferenceField(User))

  #   # created at - a string
  date = db.StringField(required=True)


class Post(db.Document):
  #   # user post - reference to the User who posted
  author = db.ReferenceField(User, required=True)

  #   # title of the post
  title = db.StringField(min_length=1, max_length=100, required=True)

  #   # main content of the post - length between 3 and 500 character
  body = db.StringField(min_length=1, max_length=500, required=True)

  #   # likes - An array of references to Users who have liked the post.
  # likes = db.ListField(db.ReferenceField(User))

  # #   # comments - An array of comments, each of which should have its own schema
  # #  comments = db.ListField(db.EmbeddedDocumentField(Comment))

  # #   # created at - a string
  # date = db.StringField(required=True)

  #   # image field - user's able to post with a picture


image = db.StringField()
