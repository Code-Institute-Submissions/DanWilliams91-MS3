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
        session["user"] = request.form.get("username").lower() # put the new user into 'session' cookie
        flash("Registration successful! Welcome, {}.".format(
            request.form.get("username")))
        return redirect(url_for("profile", username=session["user"]))

    if "user" in session:
        flash(
            "A user is already logged in - \
            please ensure they are logged out before a new user is created.")
        return redirect(url_for("profile", username=session["user"]))
    else:
        return render_template("register.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
        
    if "user" in session:
        return render_template(
            "profile.html",
            username=session["user"],
            is_superuser=check_user_level())

    return redirect(url_for("login"))


def check_user_level():
    current_user = Users.query.filter(Users.user_name == session["user"])
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

    if "user" in session:
        flash(
            "A user is already logged in - \
                please ensure they are logged out before a new user logs in.")
        return redirect(url_for("profile", username=session["user"]))
    else:
        return render_template("login.html")


@app.route("/get_categories")
def get_categories():
    categories = list(Category.query.order_by(Category.id).all())
    recipes = list(Name.query.order_by(Name.recipe_name).all())
    return render_template("categories.html", categories=categories, recipes=recipes)


@app.route("/view_category/<int:category_id>")
def view_category(category_id):
    category = Category.query.get_or_404(category_id)
    all_recipes = list(Name.query.order_by(Name.recipe_name).all())
    recipes = []
    mongo_recipes = []
    for recipe in all_recipes:
        if recipe.category_id == category_id:
            recipes.append(recipe)
            mongo_recipes.append(list(mongo.db.recipes.find({"id": recipe.id}))[0])
    return render_template("category.html", category=category, recipes=recipes, mongo_recipes=mongo_recipes)


@app.route("/manage_categories")
def manage_categories():
    if check_user_level() == False:
        flash("You must be a superuser to manage categories!")
        return redirect(url_for(
            "profile", username=session["user"]))
    categories = list(Category.query.order_by(Category.id).all())
    return render_template("manage_categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if check_user_level() == False:
        flash("You must be a superuser to manage categories!")
        return redirect(url_for(
            "profile", username=session["user"]))
    if request.method == "POST":
        category = Category(category_name=request.form.get("category_name"))
        db.session.add(category)
        db.session.commit()
        return redirect(url_for("manage_categories"))
    return render_template("add_category.html")


@app.route("/edit_category/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if check_user_level() == False:
        flash("You must be a superuser to manage categories!")
        return redirect(url_for(
            "profile", username=session["user"]))    
    category = Category.query.get_or_404(category_id)
    if request.method == "POST":
        category.category_name = request.form.get("category_name")
        db.session.commit()
        return redirect(url_for("manage_categories"))
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<int:category_id>")
def delete_category(category_id):
    if check_user_level() == False:
        flash("You must be a superuser to manage categories!")
        return redirect(url_for(
            "profile", username=session["user"]))
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    mongo.db.tasks.delete_many({"category_id": str(category_id)})
    flash("Category deleted successfully.")
    return redirect(url_for("manage_categories"))


@app.route("/get_users")
def get_users():
    if check_user_level() == False:
        flash("You must be a superuser to manage users!")
        return redirect(url_for(
            "profile", username=session["user"]))
    users = list(Users.query.order_by(Users.id).all())
    return render_template("users.html", users=users)


@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if check_user_level() == False:
        flash("You must be a superuser to manage users!")
        return redirect(url_for(
            "profile", username=session["user"]))
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.")
    return redirect(url_for("get_users"))


@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if check_user_level() == False:
        flash("You must be a superuser to manage users!")
        return redirect(url_for(
            "profile", username=session["user"]))
    user = Users.query.get_or_404(user_id)
    if request.method == "POST":
        user.user_name = request.form.get("user_name")
        if request.form.get("is_superuser") == "True":
            user.is_superuser = True
        else:
            user.is_superuser = False
        db.session.commit()
        return redirect(url_for("get_users"))
    return render_template("edit_user.html", user=user)


@app.route("/my_recipes")
def my_recipes():
    recipes = list(Name.query.order_by(Name.recipe_name).all())
    owner_recipes = list(mongo.db.recipes.find({"created_by": session["user"]}))
    user_recipes = []
    for recipe in recipes:
        for owned_recipe in owner_recipes:
            if recipe.id == owned_recipe["id"]:
                user_recipes.append(recipe)
    categories = list(Category.query.order_by(Category.id).all())
    return render_template(
        "my_recipes.html", user_recipes=user_recipes, categories=categories)


@app.route("/manage_recipes")
def manage_recipes():
    if check_user_level() == False:
        return redirect(url_for("my_recipes"))
    recipes = list(Name.query.order_by(Name.recipe_name).all())
    categories = list(Category.query.order_by(Category.id).all())
    mongo_recipes = list(mongo.db.recipes.find())
    return render_template(
        "manage_recipes.html", mongo_recipes=mongo_recipes, recipes=recipes, categories=categories)


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():    
    # check if user is logged in
    if "user" not in session:
        flash("You need to be logged in to add a recipe.")
        return redirect(url_for("login"))
    if request.method == "POST":
        recipe_main = Name(
            recipe_name=request.form.get("recipe_name"),
            category_id=int(request.form.get("category_id"))
        )
        db.session.add(recipe_main)
        db.session.commit()
        new_recipe = Name.query.filter(
            Name.recipe_name == request.form.get("recipe_name"))
        recipe_details = {
            "id": new_recipe[0].id,
            "ingredients": request.form.get("ingredients"),
            "instructions": request.form.get("instructions"),
            "created_by": session["user"]
        }
        db.session.add(recipe_main)
        db.session.commit()
        mongo.db.recipes.insert_one(recipe_details)
        flash("Recipe saved")
        return redirect(url_for("my_recipes"))
    categories = list(Category.query.order_by(Category.category_name).all())
    return render_template("add_recipe.html", categories=categories)


@app.route("/delete_recipe/<int:recipe_id>")
def delete_recipe(recipe_id):
    recipe = Name.query.get_or_404(recipe_id)
    mongo_recipe = list(mongo.db.recipes.find({"id": recipe.id}))[0]
    if session["user"] != mongo_recipe["created_by"]:
        if check_user_level() == False:
            flash("You can only delete your own recipes!")
            return redirect(url_for("my_recipes"))
    db.session.delete(recipe)
    db.session.commit()
    mongo.db.recipes.delete_one(mongo_recipe)
    flash("Recipe deleted successfully.")
    return redirect(url_for("manage_recipes"))


@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    recipe = Name.query.get_or_404(recipe_id)
    mongo_recipe = list(mongo.db.recipes.find({"id": recipe_id}))[0]
    categories = list(Category.query.order_by(Category.category_name).all())
    # if user doesn't own recipe
    if session["user"] != mongo_recipe["created_by"]:
        if check_user_level() == False:
            flash("You can only edit your own recipes!")
            return redirect(url_for("my_recipes"))
    if request.method == "POST":
        recipe.recipe_name = request.form.get("recipe_name"),
        recipe.category_id = int(request.form.get("category_id"))
        db.session.commit()
        mongo_details = {
            "id": recipe_id,
            "ingredients": request.form.get("ingredients"),
            "instructions": request.form.get("instructions"),
            "created_by": mongo_recipe["created_by"]
        }
        mongo.db.recipes.update_one({"id": recipe_id}, {"$set": mongo_details})
        flash("Recipe updated successfully")
        return redirect(url_for("my_recipes"))
    return render_template(
        "edit_recipe.html", categories=categories, recipe=recipe,
        mongo_recipe=mongo_recipe)
