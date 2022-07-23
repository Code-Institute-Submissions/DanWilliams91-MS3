from flask import flash, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from appdir import app, db, mongo
from appdir.models import Name, Category, Users


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        
        # check if username already exists in db
        existing_user = Users.query.filter(Users.user_name == \
            request.form.get("username").lower()).all()

        if existing_user:
            flash("Username already exists. Please try another username or log in if you already have an account.")
            return redirect(url_for("register"))

        user = Users(
            user_name=request.form.get("username").lower(),
            password=generate_password_hash(request.form.get("password"))
        )
        
        db.session.add(user)
        db.session.commit()

    return render_template("register.html")
