from flask import Blueprint, render_template

bp_user = Blueprint('bp_user', __name__)


@bp_user.get('/authenticate/user_home')
def user_home_get():
    return render_template("user_home.html")


@bp_user.post('/authenticate/user_home')
def user_home_post():
    from models import User
    user = User.query.first()
    from app import db
    user.admin = True
    db.session.commit()
    print(123)
    return render_template("user_home.html")
