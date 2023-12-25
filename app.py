import os
from cs50 import SQL
from flask import Flask, flash, redirect, jsonify, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required, allowed_file

app = Flask(__name__)

db = SQL("sqlite:///routineroster.db")

TYPES = {"client", "trainer"}

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                    username TEXT NOT NULL, 
                    hash TEXT NOT NULL, 
                    full_name TEXT,
                    profile_picture TEXT,
                    user_type TEXT NOT NULL);""")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
        return render_template("register.html", types=TYPES)
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
        
        db.execute("INSERT INTO users (username, hash, user_type) VALUES (?, ?, ?);", username, generate_password_hash(request.form.get("password")), user_type)

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
    
@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/account", methods=["GET", "POST"])
@login_required
def my_account():
    if request.method == "GET":
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        # if user already has a pfp and full name in DB
        try:
            data = db.execute("SELECT profile_picture, full_name FROM users WHERE id = ?", session["user_id"])
            pfp = data[0]["profile_picture"]
            fname = data[0]["full_name"]
            return render_template("account.html", pfp=pfp, fname=fname, username=username[0]["username"])
        # if user doesn't have a pfp and full name in db
        except IndexError:
            return render_template("account.html", username=username[0]["username"])
    else:
        # fetching data from frontend
        full_name = request.form["full_name"]
        profile_picture = request.files["profile_picture"]
        # checking if full name and picture is provided and if picture is in correct format
        if full_name and profile_picture and allowed_file(profile_picture.filename, ALLOWED_EXTENSIONS):

            # secure filename checks if there are any dangerous or unwanted parts from the file name
            filename = secure_filename(profile_picture.filename)

            # saving the uploaded picture to uploads folder
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            picture_path = filename
            db.execute("UPDATE users SET full_name = ?, profile_picture = ? WHERE id = ?",full_name, picture_path, session["user_id"])

            flash('Profile updated successfully!', 'success')
            return redirect('/')
        
        else:
            return apology("Invalid file format or missing information")
        
@app.route("/home", methods=["GET", "POST"])
@login_required
def trainers():
    
    if request.method == "GET":
        trainers = []
        rows = db.execute("SELECT id, username, user_type, full_name, profile_picture FROM users WHERE user_type = 'trainer';")
        if rows and len(rows) <= 3:
            for i in range(len(rows)):
                if rows[i]["full_name"]:
                    trainers.append(rows[i])
        elif rows and len(rows) > 3:
            for i in range(3):
                if rows[i]["full_name"]:
                    trainers.append(rows[i])
        else:
            return render_template("home.html", trainers=trainers)
        
        return render_template("home.html", trainers=trainers)
    
    else:
        id = request.form.get("id")
        print(f"id is: {id}")
        return redirect("/")
    
    
@app.route("/show_more_trainers", methods=["GET"])
@login_required
def fetch_more_trainers():
    trainers = []
    # logic to fetch more trainers 
    # Assuming you already have a logic for pagination or getting the next set of trainers
    rows = db.execute("SELECT id, username, user_type, full_name, profile_picture FROM users WHERE user_type = 'trainer' LIMIT 3 OFFSET 3;")
    for row in rows:
        if row["full_name"]:
            trainers.append({
                'id': row["id"],
                'username': row["username"],
                'user_type': row["user_type"],
                'full_name': row["full_name"],
                'profile_picture': row["profile_picture"]
            })
    return jsonify({'trainers': trainers})