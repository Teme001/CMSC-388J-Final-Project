from flask import Blueprint, render_template
from flask_login import current_user, login_required

#from .models import User

main = Blueprint("main", __name__, template_folder="templates")

#def get_all_users():
#  return list(User.objects.filter(id__ne=current_user.id))


@main.route('/', methods=["GET", "POST"])
def index():
  return render_template('index.html')



@main.route('/404')
def error():
  return render_template('main.404.html')


# Route for querying users
# Uses POST to receive user input and redirects to a GET route with the search query
# Renders a page with all possible users that matches with the query
# Each user is linkable (<a></a>) and redirects to its profile page
# @main.route("/search", methods=["POST"])
# @login_required
# def search():
#  query = request.form.get('search')
#  results = User.objects.filter(username__contains=query).exclude(
#    id=current_user.id)
#  return render_template("search_results.html", users=results)

# SocketIO handlers (if using Flask-SocketIO)
# Note: The commented-out code will not run without Flask-SocketIO

# Load the forms from forms.py
# update_username_form = UpdateUsernameForm()
# update_profile_pic_form = UpdateProfilePicForm()
# update_email_form = UpdateEmailForm()

# allows user to update username and set/update profile picture
# Update username
# if update_username_form.validate_on_submit():
#   new_user = User.objects(
#     username=update_username_form.username.data).first()
#   if new_user is None:
#     current_user.username = update_username_form.username.data
#     current_user.save()
#     flash("Username updated")
#     return redirect(url_for('settings'))

# Update email
# if update_email_form.validate_on_submit():
#   new_email = User.objects(email=update_email_form.email.data).first()
#   if new_email is None:
#     current_user.email = update_email_form.email.data
#     current_user.save()
#     flash("Email updated")
#     return redirect(url_for('settings'))

# Update profile image
# if update_profile_pic_form.validate_on_submit():
#   image = update_profile_pic_form.profile_pic.data
#   image_name = secure_filename(image.filename)
#   image_path = os.path.join("images", image_name)
#   image.save(image_path)

# with open(image_path, "rb") as img_file:
#   if current_user.profile_pic.get() is None:
#     current_user.profile_pic.put(img_file, content_type=image.mimetype)
#   else:
#     current_user.profile_pic.replace(img_file, conent_type=image.mimetype)
#   current_user.save()
#   flash("Profile image Updated")
#   return redirect(url_for('settings'))

# if current_user.profile_pic:
#   img_data = current_user.profile_pic.read()
#   img_b64 = base64.b64encode(img_data).decode('utf-8')
# else:
#   img_b64 = None

# return render_template('settings.html',
#                        update_username_form=update_username_form,
#                        update_email_form=update_email_form,
#                        update_profile_pic_form=update_profile_pic_form,
#                        image=img_b64)
