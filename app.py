from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

app = Flask(__name__)

db = SQL("sqlite:///routineroster.db")

db.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                       username TEXT NOT NULL, 
                       hash TEXT NOT NULL, 
                       user_type TEXT NOT NULL);""")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    return apology("To do", 400)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # if request is POST - fetching data from frontend
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        user_type = request.form.get("reg-type")

        # if data is valid, users table is created
        if not username:
            return apology("No username provided")
        elif not password:
            return apology("No password provided")
        elif not confirmation:
            return apology("Password not confirmed")
        elif confirmation != password:
            return apology("Passwords are not matching")
        elif not user_type:
            return apology("Please specify the registration type")
        
        #checking if username is taken
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("username is already taken")
        
        db.execute("INSERT INTO users (username, hash, user_type) VALUES (?, ?, ?)", username, generate_password_hash(request.form.get("password")), user_type)

        flash(f"Successfully registered a new {user_type} account as {username}!")
        return redirect("/")
        
        

@app.route("/login")
def login():
    return apology("to do", 400)