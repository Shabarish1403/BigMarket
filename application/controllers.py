from flask import render_template_string
from flask import current_app as app
from flask_security import auth_required, current_user, roles_required

# Views
@app.route("/")
@auth_required()
def home():
    return render_template_string('Hello! hola hola')

@app.route("/user")
# @auth_required()
@roles_required("user")
def user_home():
    return render_template_string("Hello {{ current_user.email }} you are a user!")