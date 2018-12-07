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
    if 'user_id' in session:
        g.user_id = session['user_id']

@app.route('/')
def welcome():
    return render_template("index.html")

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
        resultValue = cur.execute("SELECT * FROM users WHERE username = %s",[username])
        if resultValue == 1:
            userDetail = cur.fetchall()
            # Remember which user has logged in
            for row in userDetail:
                session["user_id"] = row[0]
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

        # store the input into values
        username = request.form.get("username")
        password = request.form.get("password")

        # make a connection to db
        cur = mysql.connection.cursor()
        # Query database for username
        resultValue = cur.execute("SELECT * FROM users WHERE username = %s",[username])

        # if the user exist
        if resultValue == 1:
            userDetail = cur.fetchall()
        else:
            return redirect("/login")

        # Remember which user has logged in
        for row in userDetail:
            # check the hash
            if not check_password_hash(row[2], password):
                return redirect("/login")
            else:
                session["user_id"] = row[0]

        # close the cursor
        cur.close()

        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/home")
def home():

    # Forget any _sub
    session.pop('_sub', None)

    # creat a cursor for mysql
    cur = mysql.connection.cursor()
    # Query database for subjects
    cur.execute("SELECT * FROM subjects ORDER BY subject")
    objects = cur.fetchall()

    # close the cursor
    cur.close()

    return render_template("home.html", objects = objects)

@app.route("/books", methods=['GET', 'POST'])
def books():
    if request.method == "POST":

        # get the form data
        sub = request.form.get("subject")
        # store the subject into a session
        session["_sub"] = sub

        # creat a cursor
        cur = mysql.connection.cursor()
        # query db for books
        cur.execute("SELECT * from books WHERE subID = %s ORDER BY book", [sub])
        objects = cur.fetchall()

        return render_template("home2.html", objects = objects)

@app.route("/chapters", methods=['GET', 'POST'])
def chapters():
    if request.method == 'POST':

        # get the session data
        sub = session["_sub"]
        book = request.form.get('book')

        # creat a cursor
        cur = mysql.connection.cursor()
        # query the db
        cur.execute("SELECT * from chapters WHERE subID = %s AND book = %s ORDER BY chapter",
        (sub, book))
        objects = cur.fetchall()

        # store the subject into a session
        session["_book"] = book

        return render_template("home3.html", objects = objects)
@app.route("/setsession", methods=['GET', 'POST'])
def setsession():
    if request.method == "POST":
        session["_chapter"] = request.form.get("chapter")
        return redirect("/test")

@app.route("/test", methods=['GET', 'POST'])
def text():
    # get the session data
    sub = session["_sub"]
    book = session["_book"]
    chapter = session["_chapter"]

    # creat a cursor
    cur = mysql.connection.cursor()
    # query the db
    cur.execute("SELECT * from questions WHERE subID = %s AND book = %s AND chapter = %s ORDER BY RAND() LIMIT 1",
    (sub, book, chapter))
    objects = cur.fetchall()

    return render_template("test.html", objects = objects)

@app.route("/record", methods=["GET", "POST"])
def record():
    # get the result for the question
    result = request.form.get("result")
    qid = request.form.get("qid")
    temp_corrects = request.form.get("corrects")
    temp_wrongs = request.form.get("wrongs")
    corrects = int(temp_corrects)
    wrongs = int(temp_wrongs)

    # creat a cursor
    cur = mysql.connection.cursor()

    if result == 1:
        cur.execute("UPDATE questions SET corrects = (%d) WHERE qid = (%s)", (corrects, qid))
    else:
        cur.execute("UPDATE questions SET wrongs = (%d) WHERE qid = (%s)", (wrongs, qid))

    # close it
    cur.close()

    return redirect("/test")
