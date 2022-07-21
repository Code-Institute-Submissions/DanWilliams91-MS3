from flask import flash, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from appdir import app, db, mongo
from appdir.models import Name, Category, Users


@app.route("/", methods=["GET", "POST"])
def home():
    admin_user = Users(
        user_name="Admin",
        password="ABC123",
        is_superuser=True
    )
    db.session.add(admin_user)
    db.session.commit()
    users = list(User.query.order_by(User.id).all())
    return render_template("base.html", users=users)
