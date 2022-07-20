from flask import flash, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from appdir import app, db, mongo
from appdir.models import (
    Name,
    Category,
    Users
)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("base.html")
