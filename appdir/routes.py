from flask import flash, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from appdir import app, db, mongo
from appdir.models import Name, Category, Users
import string

a_z = string.ascii_uppercase


def check_user_level():
    """
    Checks whether the logged-in user is a superuser and returns the result
    via a boolean value.
    """
    current_user = Users.query.filter(Users.user_name == session["user"])
    return True if current_user[0].is_superuser else False


@app.route("/")
@app.route("/home")
def home():
    """ Renders the default home page of the app. """
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    When the GET method is used:
        Returns the register.html registration webpage.

    When the POST method is used:
        The function checks whether the username already exists and, if so,
        returns the registration form with a flash message to confirm that the
        username is taken. The function also checks whether a user is already
        logged in and, if so, a flash message is rendered to confirm that the
        current user must be logged out before a new user can be created. If
        neither of these situations occur, the submitted form data is used to
        add a new user to the database, whilst simultaneously logging the new
        user into the app and rendering the profile page.
    """
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
    if "user" in session:
        flash(
            "A user is already logged in - \
            please ensure they are logged out before a new user is created.")
        return redirect(url_for("profile", username=session["user"]))
    else:
        return render_template("register.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    """
    Renders the user's profile page if the user is logged in, or returns the
    login page if no user is logged in.

    Calls the is_superuser function to check whether the current user is a
    superuser, and passes the returned value to the profile page for
    conditional layouts of the page.
    """
    if "user" in session:
        return render_template(
            "profile.html",
            username=session["user"],
            is_superuser=check_user_level())
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """
    Removes the user session cookie and redirects the user to the login page.
    A flash message is displayed to confirm that the user has logged out.
    """
    flash("You have been logged out successfully.")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    When the GET method is used, the function checks whether a user is
    currently logged in. If so, a flash message is displayed to confirm this
    and the user is redirected to their profile page.

    When the POST method is used, the submitted form data is checked against
    the database. If either the username or password do not match a User
    stored in the database, a flash message is displayed to confirm that
    either the username or password is incorrect. If both the username and
    password match an existing database User, a session cookie is added to
    the browser and the user is directed to their profile page with a flash
    message to confirm their successful login.
    """
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
                flash("Incorrect Username and/or Password.")
                return redirect(url_for("login"))
        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password.")
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
    """
    Returns the categories.html webpage and passes lists of all recipes (Name)
    and Categories to the webpage.
    """
    categories = list(Category.query.order_by(Category.id).all())
    recipes = list(Name.query.order_by(Name.recipe_name).all())
    return render_template(
        "categories.html", categories=categories, recipes=recipes)


@app.route("/get_recipes")
def get_recipes():
    """
    Returns the recipes.html webpage and passes lists of all recipes (Name),
    Categories and recipe data listed on the Mongo database.

    The a_z global variable is also passed to allow iteration of the alphabet
    for the functional purposes of the webpage.
    """
    categories = list(Category.query.order_by(Category.id).all())
    recipes = list(Name.query.order_by(Name.recipe_name).all())
    mongo_recipes = list(mongo.db.recipes.find())
    return render_template(
        "recipes.html", categories=categories, recipes=recipes,
        mongo_recipes=mongo_recipes, a_z=a_z)


@app.route("/get_recipes_filter/<sel_filter>")
def get_recipes_filter(sel_filter):
    """
    Returns the recipes.html webpage and passes lists of all recipes (Name),
    Categories and recipe data listed on the Mongo database. Displays recipes
    (Names) whose recipe_name values begin with the same letter as the
    sel_filter parameter.

    The a_z global variable is also passed to allow iteration of the alphabet
    for the functional purposes of the webpage.
    """
    categories = list(Category.query.order_by(Category.id).all())
    all_recipes = list(Name.query.order_by(Name.recipe_name).all())
    recipes = []
    for recipe in all_recipes:
        if recipe.recipe_name.startswith(sel_filter) \
        or recipe.recipe_name.startswith(sel_filter.lower()):
            recipes.append(recipe)
    mongo_recipes = list(mongo.db.recipes.find())
    letter_filter = sel_filter
    return render_template(
        "recipes.html", categories=categories, recipes=recipes,
        mongo_recipes=mongo_recipes, a_z=a_z, letter_filter=letter_filter)
        

@app.route("/get_recipes_newest")
def get_recipes_newest():
    """
    Returns the recipes.html webpage and passes lists of all recipes (Name),
    Categories and recipe data listed on the Mongo database. Displays recipes
    (Names) in order of most-recently added, based on their id value.
    """
    categories = list(Category.query.order_by(Category.id).all())
    recipes = list(Name.query.order_by(Name.id.desc()).all())
    mongo_recipes = list(mongo.db.recipes.find())
    return render_template(
        "recipes_newest.html", categories=categories, recipes=recipes,
        mongo_recipes=mongo_recipes)


@app.route("/view_category/<int:category_id>")
def view_category(category_id):
    """
    Renders the category.html webpage and passes a list of recipes (Names)
    which are assigned to the category identifiable by the category_id
    parameter (as well as their associated data stored on the Mongo database).
    """
    category = Category.query.get_or_404(category_id)
    all_recipes = list(Name.query.order_by(Name.recipe_name).all())
    recipes = []
    mongo_recipes = []
    for recipe in all_recipes:
        if recipe.category_id == category_id:
            recipes.append(recipe)
            mongo_recipes.append(
                list(mongo.db.recipes.find({"id": recipe.id}))[0])
    return render_template(
        "category.html", category=category, recipes=recipes,
        mongo_recipes=mongo_recipes)


@app.route("/manage_categories")
def manage_categories():
    """
    Returns the manage_categories webpage with a list of all categories and
    recipes for superusers to create, add, edit and delete categories.

    If the user requesting the webpage is not a superuser, they are
    redirected to their profile page and a flash message is displayed to
    confirm they are not able to view the requested webpage.
    """
    if check_user_level() is False:
        flash("You must be a superuser to manage categories!")
        return redirect(url_for(
            "profile", username=session["user"]))
    categories = list(Category.query.order_by(Category.id).all())
    recipes = list(Name.query.order_by(Name.recipe_name).all())
    return render_template(
        "manage_categories.html", categories=categories, recipes=recipes)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    """
    When the GET method is used:
        Returns the add_category webpage which enables superusers to add a new
        category.

    When the POST method is used:
        The submitted form data is used to add a new Category to the database.
        The user is redirected to the manage_categories webpage and a flash
        message is displayed to confirm that the Category was added to the
        database.

    If the user requesting the webpage is not a superuser, they are
    redirected to their profile page and a flash message is displayed to
    confirm they are not able to view the requested webpage.
    """
    if check_user_level() is False:
        flash("You must be a superuser to manage categories!")
        return redirect(url_for(
            "profile", username=session["user"]))
    if request.method == "POST":
        category = Category(
            category_name=request.form.get("category_name"),
            category_img=request.form.get("category_img")
            )
        db.session.add(category)
        db.session.commit()
        flash("Category added successfully.")
        return redirect(url_for("manage_categories"))
    return render_template("add_category.html")


@app.route("/edit_category/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    """
    When the GET method is used:
        Returns the edit_category.html webpage for the Category identified by
        the category_id parameter.

    When the POST method is used:
        Updates the Category identified by the category_id parameter with the
        data submitted by the user via the HTML form. The user is then
        redirected to the manage_categories.html webpage and a flash message
        is displayed to confirm that the Category was updated.

    If the user requesting the webpage is not a superuser, they are
    redirected to their profile page and a flash message is displayed to
    confirm they are not able to view the requested webpage.
    """
    if check_user_level() is False:
        flash("You must be a superuser to manage categories!")
        return redirect(url_for(
            "profile", username=session["user"]))    
    category = Category.query.get_or_404(category_id)
    if request.method == "POST":
        category.category_name = request.form.get("category_name")
        category.category_img=request.form.get("category_img")
        db.session.commit()
        flash("Category updated successfully.")
        return redirect(url_for("manage_categories"))
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<int:category_id>")
def delete_category(category_id):
    """
    Deletes the Category identified by the category_id parameter from the
    database, then redirects the user to the manage_categories webpage with a
    flash message to confirm the Category deletion.

    If the user performing the action is not a superuser, they are redirected
    to their profile page and a flash message is displayed to confirm they are
    not able to perform the requested action.
    """
    if check_user_level() is False:
        flash("You must be a superuser to manage categories!")
        return redirect(url_for(
            "profile", username=session["user"]))
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted successfully.")
    return redirect(url_for("manage_categories"))


@app.route("/get_users")
def get_users():
    """
    Returns the users.html template with a list of all Users for superusers
    to manage.

    If the user requesting the webpage is not a superuser, they are
    redirected to their profile page and a flash message is displayed to
    confirm they are not able to view the requested webpage.
    """
    if check_user_level() is False:
        flash("You must be a superuser to manage users!")
        return redirect(url_for(
            "profile", username=session["user"]))
    users = list(Users.query.order_by(Users.id).all())
    return render_template("users.html", users=users)


@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    """
    Deletes the User specified by the user_id parameter from the database and
    redirects the current user to the users.html webpage via the get_users()
    function, along with a flash message to confirm that the User was deleted
    successfully.

    If the user performing the action is not a superuser, they are redirected
    to their profile page and a flash message is displayed to confirm they are
    not able to perform the requested action.
    """
    if check_user_level() is False:
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
    """
    When the GET method is used:
        Returns the edit_user.html webpage for the User identified by
        the user_id parameter.

    When the POST method is used:
        Updates the User identified by the user_id parameter with the
        data submitted by the user via the HTML form. The user is then
        redirected to the users.html webpage via the get_users() function,
        along with a flash message to confirm that the User was deleted
        successfully.

    If the user requesting the webpage is not a superuser, they are
    redirected to their profile page and a flash message is displayed to
    confirm they are not able to view the requested webpage.
    """
    if check_user_level() is False:
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
    """
    Returns the my_recipes.html webpage with lists of recipes (Names) owned by
    the current user, along with their associated data stored on the Mongo
    database. A list of all Categories is also passed to the webpage.
    """
    recipes = list(Name.query.order_by(Name.id.desc()).all())
    mongo_recipes = list(mongo.db.recipes.find())
    owner_recipes = list(
        mongo.db.recipes.find({"created_by": session["user"]}))
    user_recipes = []
    for recipe in recipes:
        for owned_recipe in owner_recipes:
            if recipe.id == owned_recipe["id"]:
                user_recipes.append(recipe)
    categories = list(Category.query.order_by(Category.id).all())
    return render_template(
        "my_recipes.html", user_recipes=user_recipes, categories=categories,
        mongo_recipes=mongo_recipes)


@app.route("/manage_recipes")
def manage_recipes():
    """
    Returns the manage_recipes webpage with a list of all categories and
    recipes (Names) - along with their associated data stored on the Mongo
    database - for superusers to manage.

    If the user requesting the webpage is not a superuser, they are
    redirected to their profile page and a flash message is displayed to
    confirm they are not able to view the requested webpage.
    """
    if check_user_level() is False:
        return redirect(url_for("my_recipes"))
    recipes = list(Name.query.order_by(Name.recipe_name).all())
    categories = list(Category.query.order_by(Category.id).all())
    mongo_recipes = list(mongo.db.recipes.find())
    return render_template(
        "manage_recipes.html", mongo_recipes=mongo_recipes, recipes=recipes,
        categories=categories)


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    """
    Checks whether a user is logged into the app.

    If a user is not logged in:
        The user is redirected to the login webpage and a flash message is
        displayed to confirm that they must be logged in to add a new recipe
        (Name).

    If a user is logged in:
        When the GET method is used:
            The add_recipe.html webpage is returned with a list of all
            categories to enable the user to select an appropriate category
            for the new recipe.

        When the POST method is used:
            Adds a new recipe (Name) to the database and its associated
            data to the Mongo database, and redirects the user to the
            my_recipes.html webpage via the my_recipes() function. A flash
            message is displayed to confirm the addition of the new recipe
            (Name).
    """
    if "user" not in session:
        flash("You need to be logged in to add a recipe.")
        return redirect(url_for("login"))
    if request.method == "POST":

        #update Postgres db
        recipe_main = Name(
            recipe_name=request.form.get("recipe_name"),
            category_id=int(request.form.get("category_id")),
            img_url=request.form.get("img_url")
        )
        db.session.add(recipe_main)
        db.session.commit()

        #update Mongo db
        new_recipe = Name.query.filter(
            Name.recipe_name == request.form.get("recipe_name"))
        #ensure no blank lines in ingredients array
        ingredients_unformatted = request.form.get("ingredients").splitlines()
        ingredients = []
        for ingredient in ingredients_unformatted:
            if ingredient != "":
                ingredients.append(ingredient)
        #ensure no blank lines in instructions array
        instructions_unformatted = request.form.get("instructions").splitlines()
        instructions = []
        for instruction in instructions_unformatted:
            if instruction != "":
                instructions.append(instruction)
        recipe_details = {
            "id": new_recipe[0].id,
            "ingredients": ingredients,
            "instructions": instructions,
            "created_by": session["user"]
        }
        mongo.db.recipes.insert_one(recipe_details)
        flash("Recipe saved.")
        return redirect(url_for("my_recipes"))
    categories = list(Category.query.order_by(Category.category_name).all())
    return render_template("add_recipe.html", categories=categories)


@app.route("/delete_recipe/<int:recipe_id>")
def delete_recipe(recipe_id):
    """
    Firstly checks whether the current user is the original creator of the
    recipe (Name) identified by the recipe_id parameter.

    If the current user is not the original creator of the recipe:
        The check_user_level() function confirms whether the current user is a
        superuser.

        If the current user is a superuser:
            The recipe (Name) identified by the recipe_id parameter is deleted
            from the database and its associated data is deleted from the
            Mongo database. The user is then redirected to the
            manage_recipes.html webpage via the manage_recipes() function and
            a flash message is displayed to confirm the deletion of the recipe
            (Name).

        If the current user is not a superuser:
            The user is redirected to the my_recipes.html webpage via the
            my_recipes() function and a flash message is displayed to confirm
            that they can only delete their own recipes.

    If the current user is the original creator of the recipe:
        The recipe (Name) identified by the recipe_id parameter is deleted
        from the database and its associated data is deleted from the
        Mongo database. The user is then redirected to the
        my_recipes.html webpage via the my_recipes() function and a flash
        message is displayed to confirm the deletion of the recipe (Name).
    """
    recipe = Name.query.get_or_404(recipe_id)
    mongo_recipe = list(mongo.db.recipes.find({"id": recipe.id}))[0]
    if session["user"] != mongo_recipe["created_by"]:
        if check_user_level() is False:
            flash("You can only delete your own recipes!")
            return redirect(url_for("my_recipes"))
    db.session.delete(recipe)
    db.session.commit()
    mongo.db.recipes.delete_one(mongo_recipe)
    flash("Recipe deleted successfully.")
    if session["user"] != mongo_recipe["created_by"]:
        return redirect(url_for("manage_recipes"))
    else:
        return redirect(url_for("my_recipes"))


@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    """
    Firstly checks whether the current user is the original creator of the
    recipe (Name) identified by the recipe_id parameter.

    If the current user is not the original creator of the recipe:
        The check_user_level() function confirms whether the current user is a
        superuser.

        If the current user is a superuser:
            When the GET method is used:
                The edit_recipe.html webpage is rendered with the current
                recipe (Name) identified by the recipe_id parameter passed to
                it, along with its associated data from the Mongo database and
                lists of all Categories.

            When the POST method is used:
                The recipe (Name) identified by the recipe_id parameter is
                updated on the Postgres database and the Mongo database in
                line with the data submitted via the HTML form. The user is
                then redirected to the manage_recipes.html webpage via the
                manage_recipes() function.

        If the current user is not a superuser:
            The user is redirected to the my_recipes.html webpage via the
            my_recipes() function and a flash message is displayed to confirm
            that they are only able to edit their own recipes.

    If the current user is the original creator of the recipe:
        When the GET method is used:
            The edit_recipe.html webpage is rendered with the current
            recipe (Name) identified by the recipe_id parameter passed to
            it, along with its associated data from the Mongo database and
            lists of all Categories.
        
        When the POST method is used:
            If the current user is a superuser:
                The recipe (Name) identified by the recipe_id parameter is
                updated on the Postgres database and the Mongo database in
                line with the data submitted via the HTML form. The user is
                then redirected to the my_recipes.html webpage via the
                my_recipes() function.

            If the current user is a not a superuser:
                The recipe (Name) identified by the recipe_id parameter is
                updated on  the Postgres database and the Mongo database in
                line with the data submitted via the HTML form. The user is
                then redirected to the manage_recipes.html webpage via the
                manage_recipes() function.
    """
    recipe = Name.query.get_or_404(recipe_id)
    mongo_recipe = list(mongo.db.recipes.find({"id": recipe_id}))[0]
    categories = list(Category.query.order_by(Category.category_name).all())
    # if user doesn't own recipe
    if session["user"] != mongo_recipe["created_by"]:
        if check_user_level() is False:
            flash("You can only edit your own recipes!")
            return redirect(url_for("my_recipes"))
    if request.method == "POST":
        # update Postgres db
        recipe.recipe_name = request.form.get("recipe_name"),
        recipe.category_id = int(request.form.get("category_id")),
        recipe.img_url = request.form.get("img_url")
        db.session.commit()

        #update Mongo db
        #ensure no blank lines in ingredients array
        ingredients_unformatted = request.form.get("ingredients").splitlines()
        ingredients = []
        for ingredient in ingredients_unformatted:
            if ingredient != "":
                ingredients.append(ingredient)
        instructions_unformatted = request.form.get(
            "instructions").splitlines()
        #ensure no blank lines in instructions array
        instructions = []
        for instruction in instructions_unformatted:
            if instruction != "":
                instructions.append(instruction)
        mongo_details = {
            "id": recipe_id,
            "ingredients": ingredients,
            "instructions": instructions,
            "created_by": mongo_recipe["created_by"]
        }
        mongo.db.recipes.update_one(
            {"id": recipe_id}, {"$set": mongo_details})

        message = f"Recipe { recipe.recipe_name } updated successfully."
        flash(message)
        if check_user_level() is False:
            return redirect(url_for("my_recipes"))
        else:
            return redirect(url_for("manage_recipes"))
    return render_template(
        "edit_recipe.html", categories=categories, recipe=recipe,
        mongo_recipe=mongo_recipe)
