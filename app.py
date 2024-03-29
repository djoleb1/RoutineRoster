import os
from dotenv import load_dotenv
from cs50 import SQL
from flask import Flask, flash, redirect, jsonify, render_template, request, session, json
import requests
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import apology, login_required, allowed_file, usd



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

db.execute("""CREATE TABLE IF NOT EXISTS posts (
           id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
           trainer_id INTEGER,
           post_content TEXT,
           timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
           FOREIGN KEY(trainer_id) REFERENCES users(id));""")

db.execute("""CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id INTEGER,
            name TEXT NOT NULL,
            equipment TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            instructions TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, name))""")

db.execute("""CREATE TABLE IF NOT EXISTS balance (
           user_id INTEGER,
           balance INTEGER,
           FOREIGN KEY (user_id) REFERENCES users(id))""")

db.execute("""CREATE TABLE IF NOT EXISTS routines (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            trainer_id INTEGER,
            name TEXT NOT NULL,
            price INTEGER,
            description TEXT,
            exercises TEXT,
            FOREIGN KEY (trainer_id) REFERENCES users(id))
            """)

db.execute("""CREATE TABLE IF NOT EXISTS transactions (
           buyer_id INTEGER,
           routine_id INTEGER,
           timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
           FOREIGN KEY (routine_id) REFERENCES routines(id)
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
        # checking if user has any saved exercises
        exercises = db.execute("SELECT * FROM exercises WHERE user_id = ? ORDER BY id", session["user_id"])
        
        # check if user has bought any routines
        routines = db.execute("SELECT t.buyer_id, t.routine_id, r.trainer_id, r.name, r.price, r.description, r.exercises, u.full_name, u.profile_picture FROM transactions t JOIN routines r ON t.routine_id = r.id JOIN users u ON r.trainer_id = u.id WHERE t.buyer_id = ?", session["user_id"])

        for routine in routines:
            routine["exercises"] = json.loads(routine["exercises"])
            routine["exercises"] = '<br>'.join(routine["exercises"])
            

        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        
        # if user already has a pfp and full name in DB
        try:
            data = db.execute("SELECT profile_picture, full_name FROM users WHERE id = ?", session["user_id"])
            pfp = data[0]["profile_picture"]
            fname = data[0]["full_name"]
            return render_template("account.html", pfp=pfp, fname=fname, routines=routines, username=username[0]["username"], exercises=exercises)
        
        # if user doesn't have a pfp and full name in db
        except IndexError:
            return render_template("account.html", routines=routines, username=username[0]["username"], exercises=exercises)
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
        # to render 'who to follow' 
        # creating lists that will be used to store users with 'trainer' type and trainers which current user is following
        global followed
        global rows
        global showcased_trainers
        all_trainers = []
        followed = []
        posts = []

        #querying dv to find all trainers
        rows = db.execute("SELECT id, username, user_type, full_name, profile_picture FROM users WHERE user_type = 'trainer';")

        #querying db to find all of the trainers that current user is following
        followers = db.execute("SELECT followed_id FROM followers WHERE follower_id = ?", session["user_id"])

        # apppending all of the followed trainers to followed list so we could compare it in if/else
        for follower in followers:
            followed.append(follower["followed_id"])

         # to render the posts
        queryposts = db.execute("SELECT posts.id, trainer_id, post_content, timestamp, username, profile_picture FROM posts JOIN users ON posts.trainer_id=users.id ORDER BY timestamp DESC;")
        for post in queryposts:
            if post["trainer_id"] in followed or post["trainer_id"] == session["user_id"]:
                posts.append(post)

        for row in rows:
            if row["full_name"] and row["id"] not in followed and row["id"] != session["user_id"]:
                all_trainers.append(row)

        if len(all_trainers) <= 3:
            showcased_trainers = all_trainers
            return render_template("home.html", trainers=all_trainers, posts=posts)
            
        else:
            showcased_trainers = all_trainers[:3]
            return render_template("home.html", trainers=all_trainers[:3], show_more = True, posts=posts)
        
    else:
        id = request.form.get("id")
        db.execute("INSERT INTO followers (follower_id, followed_id) VALUES (?, ?);", session["user_id"], id)
        return redirect("/home")
    
@app.route("/shop", methods=["GET", "POST"])
@login_required
def shop():
    if request.method == "GET":

        purchased_routine_ids = []

        # if user is trainer, all of his created routines are showing
        if session["user_type"] == "trainer":
            available_routines = db.execute("SELECT routines.id, trainer_id, name, price, description, full_name, profile_picture FROM routines JOIN users ON routines.trainer_id=users.id WHERE trainer_id = ?", session["user_id"])
        # if the user is client, all of the not purchased routines are showing
        else:
            available_routines = []
            all_routines = db.execute("SELECT routines.id, trainer_id, name, price, description, full_name, profile_picture FROM routines JOIN users ON routines.trainer_id=users.id")

            # SQL query to check all routines that current user has purchased    
            purchased_routines = db.execute("SELECT routine_id FROM transactions WHERE buyer_id = ?", session["user_id"])

            # filtering out only IDs from the previous query
            for routine in purchased_routines:
                purchased_routine_ids.append(int(routine["routine_id"]))

            print(f"PURCHASED ROUTINE IDS ARE {purchased_routine_ids}")

            for routine in all_routines:
                if routine["id"] not in purchased_routine_ids:
                    available_routines.append(routine)
                
        try:
            balance = db.execute("SELECT balance FROM balance WHERE user_id = ?", session["user_id"])[0]["balance"]
        except IndexError:
            balance = 0


        return render_template("shop.html", routines=available_routines, balance=usd(balance))
    if request.method == "POST":
        routine_id = request.json.get("routineId")

        # check the price of the routine
        price = db.execute("SELECT price FROM routines WHERE id = ?", routine_id)[0]["price"]
        
        # check the balance of the current user:
        try:
            balance = db.execute("SELECT balance FROM balance WHERE user_id = ?", session["user_id"])[0]["balance"]
        except IndexError:
            balance = 0
        
        if price > balance:
            print("NOT ENOUGH BALANCE")
            return jsonify({
                "routine id": routine_id,
                "status": "Not enough balance!"
            })
               
        else:
            db.execute("INSERT INTO transactions (buyer_id, routine_id) VALUES (?, ?)", session["user_id"], routine_id)

            # subtract the routine price from the user's balance
            db.execute("UPDATE balance SET balance = ? WHERE user_id = ?", int(balance - price), session["user_id"])

            # get the ID of the trainer
            trainer_id = db.execute("SELECT * FROM routines WHERE id = ?", routine_id)[0]["trainer_id"]

            # find trainer's current balance
            try:
                trainer_balance = db.execute("SELECT * FROM balance WHERE user_id = ?", trainer_id)[0]["balance"]
            except IndexError:
                db.execute("INSERT INTO balance (user_id, balance) VALUES (?, ?)", trainer_id, 0)
                trainer_balance = db.execute("SELECT * FROM balance WHERE user_id = ?", trainer_id)[0]["balance"]

            # add the routine price to trainer's balance
            db.execute("UPDATE balance SET balance = ? WHERE user_id = ?", int(trainer_balance + price), trainer_id)

            flash("Successfully purchased a new routine!")

            return jsonify({
                "routine id": routine_id,
                "status": "Successfully purchased"
            })

    
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

@app.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == 'POST':
        content = request.json.get('content')
        post_id = db.execute("INSERT INTO posts (trainer_id, post_content) VALUES (?, ?)", session["user_id"], content)
        user_info = db.execute("SELECT username, profile_picture FROM users WHERE id = ?;", session["user_id"])[0]

        return jsonify({
            'message': content,
            'username': user_info['username'],
            'id': post_id,
            'profile_picture': user_info['profile_picture']
        })
        
@app.route("/delete_post", methods=["GET", "POST"])
@login_required
def delete_post():
    if request.method == "POST":
        id = request.json.get('post_id')
        db.execute("DELETE FROM posts WHERE id = ?", id)
        return jsonify({'Success': id})
        
@app.route("/edit_post", methods=["GET", "POST"])
@login_required
def edit_post():
    if request.method == "POST":
        post_id = request.json.get("post_id")
        new_content = request.json.get("new_content")

        db.execute("UPDATE posts SET post_content = ? WHERE id = ?;", new_content, post_id)
        return jsonify({"id": post_id, "new_content": new_content})
    
@app.route("/exercises")
@login_required
def load_exercises():
    
    return render_template("exercises.html", session_type=session["user_type"])

@app.route("/api/exercises", methods=["GET", "POST"])
@login_required
def get_exercises():
    if request.method == "GET":
        api_key = os.getenv('API_KEY')
        musclegroup = request.args.get("muscle_group")
        
        external_api_url = f'https://api.api-ninjas.com/v1/exercises?muscle={musclegroup}'
        headers = {'X-Api-Key': api_key}
        response = requests.get(external_api_url, headers=headers)
        return jsonify({"exercises": response.json()})
    
    if request.method == "POST":
        session_type = session["user_type"]
        exercise_name = request.json.get("name")
        equipment = request.json.get("equipment")
        difficulty = request.json.get("difficulty")
        instructions = request.json.get("instructions")
        
        if session["user_type"] != "trainer":
            try:
                db.execute("INSERT INTO exercises (user_id, name, equipment, difficulty, instructions) VALUES (?, ?, ?, ?, ?);", session["user_id"], exercise_name, equipment, difficulty, instructions)
            except ValueError:
                return jsonify({"message": "You have already saved that exercise!"})
        
        return jsonify({
            "message": "Exercise saved successfully!", 
            "session": session_type
        })


@app.route("/removeexercise", methods=["GET", "POST"])
@login_required
def remove_exercise():
    if request.method == "POST":
        id = request.json.get('post_id')
        db.execute("DELETE FROM exercises WHERE id = ?", id)
        return jsonify({'Success': id})
    
@app.route("/addfunds", methods=["GET", "POST"])
@login_required
def add_funds():
    if request.method == "POST":
        amount = request.json.get("amount")
        if not db.execute("SELECT balance FROM balance WHERE user_id = ?", session["user_id"]):
            db.execute("INSERT INTO balance (user_id, balance) VALUES (?, ?)", session["user_id"], amount)
            return jsonify({"message": "Success", "amount": amount})
        else:
            current_amount = db.execute("SELECT balance FROM balance WHERE user_id = ?", session["user_id"])[0]["balance"]
            new_amount = current_amount + amount
            db.execute("UPDATE balance SET balance =  ? WHERE user_id = ?", new_amount, session["user_id"])
            return jsonify({"message": "Success", "amount": new_amount})
        
@app.route("/saveroutine", methods=["GET", "POST"])
@login_required
def saveroutine():
    if request.method == "POST":
        name = request.json.get("name")
        price = request.json.get("price")
        description = request.json.get("description")
        exercises = request.json.get("exercises")

        # check if the name already exists in the db
        name_exists = db.execute("SELECT * FROM routines WHERE name = ?", name)
        if name_exists:
            return jsonify({"message": "Routine name already exists, please choose a different name"})
        
        exercises_string = json.dumps(exercises)    

        db.execute("INSERT INTO routines (trainer_id, name, price, description, exercises) VALUES (?, ?, ?, ?, ?)", session["user_id"], name, price, description, exercises_string)

        return jsonify({"message": "ok"})
    
@app.route("/removeroutine", methods=["GET", "POST"])
@login_required
def removeroutine():
    if request.method == "POST":
        routine_id = request.json.get("routineId")
        
        db.execute("DELETE FROM transactions WHERE buyer_id = ? AND routine_id = ?", session["user_id"], routine_id)
        return jsonify({"message": "ok"})