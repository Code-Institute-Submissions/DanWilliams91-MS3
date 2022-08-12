from appdir import db


class Name(db.Model):
    """
    A class to represent a recipe.

    Attributes
    ----------
    id: int
        a unique id number to differentiate each recipe
    recipe_name: str
        the name of the recipe
    img_url: str
        the optional url of the image to be used to represent the recipe
    category_id: int
        a foreign key to represent which category class the recipe is assigned
        to
    """
    id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(100), unique=True, nullable=False)
    img_url = db.Column(db.String())
    category_id = db.Column(db.Integer, db.ForeignKey(
        "category.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return "ID:{0} - Name: {1}".format(
            self.id, self.recipe_name
        )


class Category(db.Model):
    """
    A class to represent a category for recipes to be assigned to.

    Attributes
    ----------
    id: int
        a unique id number to differentiate each category
    category_name: str
        the name of the category
    category_img: str
        the url of the image to be used to represent the category
    recipes: relationship
        represents relationships between the category and recipes (Name class)
        assigned to it
    """
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(25), unique=True, nullable=False)
    category_img = db.Column(db.String())
    recipes = db.relationship(
        "Name", backref="category", cascade="all, delete", lazy=True)

    def __repr__(self):
        return self.category_name


class Users(db.Model):
    """
    A class to represent a registered user of the app.

    Attributes
    ----------
    id: int
        a unique id number to differentiate each user
    user_name: str
        the username of the user - required to log into the app
    password: str
        the user's password for logging into the app
    is_superuser: bool
        represents whether the user is an app superuser
    """
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return self.user_name
