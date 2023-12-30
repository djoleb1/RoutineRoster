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

db.execute("""CREATE TABLE IF NOT EXISTS followers (
                    follower_id INTEGER,
                    followed_id INTEGER,
                    FOREIGN KEY (follower_id) REFERENCES users(id),
                    FOREIGN KEY (followed_id) REFERENCES users(id),
                    CONSTRAINT PK_followers PRIMARY KEY (follower_id, followed_id)
                )""")


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
    return redirect("/home")

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
        # creating lists that will be used to store users with 'trainer' type and trainers which current user is following
    
        global followed
        global rows
        global showcased_trainers
        all_trainers = []
        followed = []

        #querying dv to find all trainers
        rows = db.execute("SELECT id, username, user_type, full_name, profile_picture FROM users WHERE user_type = 'trainer';")

        #querying db to find all of the trainers that current user is following
        followers = db.execute("SELECT followed_id FROM followers WHERE follower_id = ?", session["user_id"])

        # apppending all of the followed trainers to followed list so we could compare it in if/else
        for follower in followers:
            followed.append(follower["followed_id"])

        for row in rows:
            if row["full_name"] and row["id"] not in followed and row["id"] != session["user_id"]:
                all_trainers.append(row)

        if len(all_trainers) <= 3:
            showcased_trainers = all_trainers
            return render_template("home.html", trainers=all_trainers)
            
        else:
            showcased_trainers = all_trainers[:3]
            return render_template("home.html", trainers=all_trainers[:3], show_more = True)

    
    else:
        id = request.form.get("id")
        db.execute("INSERT INTO followers (follower_id, followed_id) VALUES (?, ?);", session["user_id"], id)
        return redirect("/home")
    
    
@app.route("/show_more_trainers", methods=["GET"])
@login_required
def fetch_more_trainers():
    
    trainers = []
    for row in rows:
        if row["full_name"] and row["id"] != session["user_id"] and row["id"] not in followed and row not in showcased_trainers:
            trainers.append({
                'id': row["id"],
                'username': row["username"],
                'user_type': row["user_type"],
                'full_name': row["full_name"],
                'profile_picture': row["profile_picture"]
            })
    
    return jsonify({'trainers': trainers})