from appdir import db


class Name(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(100), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        "category.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return "ID:{0} - Name: {1}".format(
            self.id, self.recipe_name
        )


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(25), unique=True, nullable=False)
    recipes = db.relationship(
        "Name", backref="category", cascade="all, delete", lazy=True)

    def __repr__(self):
        return self.category_name


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return self.user_name
