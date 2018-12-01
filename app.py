import os
import yaml

from flask import Flask, flash, redirect, render_template, request, session, g
from flask_mysqldb import MySQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

app = Flask(__name__)

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
mysql = MySQL(app)

app.secret_key = os.urandom(24)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.before_request
def before_request():
    g.user_id = None
    if 'user' in session:
        g.user_id = session['user_id']

@app.route('/')
def welcome():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

# let user register for this system
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing USER NAME")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("MISSING PASSWORD")
        # Ensure confirmation was submitted
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("PASSWORDD DOESN'T MATCH")

        username = request.form.get("username")
        hashpass = generate_password_hash(request.form.get("confirmation"))

        # creat a cursor for the db
        cur = mysql.connection.cursor()
        # insert data into 'users'
        result = cur.execute("INSERT INTO users(username, hashpass) VALUES(%s, %s)", (username, hashpass))
        # commit the changes to the database
        mysql.connection.commit()
        # close the cursor
        cur.close()

        # start to login
        # Forget any user_id
        session.pop('user_id', None)

        # creat a cursor for the db
        cur = mysql.connection.cursor()
        # Query database for username
        cur.execute("SELECT * FROM users WHERE username = %s",(request.form.get("username")))
        row = cur.fetchone()
        # Remember which user has logged in
        session["user_id"] = row['uid']
        # close the cursor
        cur.close()

        # Redirect user to home page
        return redirect("/home")


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.pop('user_id', None)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # make a connection to db
        cur = mysql.connection.cursor()
        # Query database for username
        cur.execute("SELECT * FROM users WHERE username = %s",(request.form.get("username")))
        row = cur.fetchone()
        # Ensure username exists and password is correct
        if len(row) != 1 or not check_password_hash(row["hashpass"], request.form.get("password")):
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = row["uid"]

        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
