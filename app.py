from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

app = Flask(__name__)

db = SQL("sqlite:///routineroster.db")

types = ["client", "trainer"]

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
        return render_template("register.html", types=types)
    else:
        # if request is POST - fetching data from frontend
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        user_type = request.form.get("reg-type")

        # checking if data is valid
        if not username:
            return apology("No username provided")
        elif not password:
            return apology("No password provided")
        elif not confirmation or confirmation != password:
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
        
        

@app.route("/login", methods=["GET", "POST"])
def login():

    # forget any user_id stored in session
    session.clear()

    # user sent a POST request
    if request.method == "POST":

        # checking is pass and username is provided
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        
        # query db for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # check if username is provided and if password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        
        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # remember if user is client or trainer
        session["user_type"] = rows[0]["user_type"]

        return redirect("/")
    
    # if user reached via GET
    else:
        return render_template("login.html")