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
        existing_user = Users.query.filter(
            Users.user_name == request.form.get("username").lower()).all()

        if existing_user:
            flash("Username already exists. Please try another username or \
                log in if you already have an account.")
            return redirect(url_for("register"))

        user = Users(
            user_name=request.form.get("username").lower(),
            password=generate_password_hash(request.form.get("password"))
        )
        
        db.session.add(user)
        db.session.commit()

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration successful! Welcome, {}.".format(
            request.form.get("username")))
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
        
    if "user" in session:
        return render_template("profile.html", username=session["user"], is_superuser=check_user_level())

    return redirect(url_for("login"))


def check_user_level():
    current_user = Users.query.filter(Users.user_name==session["user"])
    return True if current_user[0].is_superuser else False        


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out successfully.")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = Users.query.filter(
            Users.user_name == request.form.get("username").lower()).all()

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user[0].password, request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Login successful. Welcome back, {}!".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/get_categories")
def get_categories():

    if check_user_level()==False:
        flash("You must be a superuser to manage categories!")
        return redirect(url_for(
            "profile", username=session["user"]))

    categories = list(Category.query.order_by(Category.id).all())
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if check_user_level()==False:
        flash("You must be a superuser to manage categories!")
        return redirect(url_for(
            "profile", username=session["user"]))

    if request.method == "POST":
        category = Category(category_name=request.form.get("category_name"))
        db.session.add(category)
        db.session.commit()
        return redirect(url_for("get_categories"))
    return render_template("add_category.html")


@app.route("/edit_category/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if check_user_level()==False:
        flash("You must be a superuser to manage categories!")
        return redirect(url_for(
            "profile", username=session["user"]))
    
    category = Category.query.get_or_404(category_id)
    if request.method == "POST":
        category.category_name = request.form.get("category_name")
        db.session.commit()
        return redirect(url_for("get_categories"))
    return render_template("edit_category.html", category=category)
