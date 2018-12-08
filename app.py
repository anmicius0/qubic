import os
import yaml

from flask import Flask, flash, redirect, render_template, request, session, g
from flask_mysqldb import MySQL
from flask_session import Session
from functools import wraps
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

# define the login_required
def login_required(f):
    @wraps(f)
    def wrap (*args, **kwargs):
        if 'user_id' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/login')
    return wrap

@app.before_request
def before_request():
    g.user_id = None
    if 'user_id' in session:
        g.user_id = session['user_id']


@app.route("/")
def welcome():
    if 'user_id' in session:
        return redirect('/home')
    else:
        return render_template('index.html')


# let user register for this system
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        hashpass = generate_password_hash(request.form.get("confirmation"))

        try:
            # creat a cursor for the db
            cur = mysql.connection.cursor()
            # insert data into 'users'
            cur.execute("INSERT INTO users(username, hashpass) VALUES(%s, %s)", (username, hashpass))
            # commit the changes to the database
            mysql.connection.commit()
            # close the cursor
            cur.close()
            return redirect('/login')
        except:
            return redirect('/register')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

# let user to login, it also clean the session of 'user_id' 'user_name'
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.pop('user_id', None)
    session.pop('user_name', None)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

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
                session['user_name'] = row[1]

        # close the cursor
        cur.close()

        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# it's the home page, let user to chose the subject
# it pop the session '_sub'
@app.route("/home")
@login_required
def home():

    # creat a cursor for mysql
    cur = mysql.connection.cursor()
    # Query database for subjects
    cur.execute("SELECT * FROM subjects ORDER BY subject")
    objects = cur.fetchall()
    # close the cursor
    cur.close()

    return render_template("home.html", objects = objects)

# chose the book
@app.route("/books", methods=['GET', 'POST'])
@login_required
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

# chose the chapter
@app.route("/chapters", methods=['GET', 'POST'])
@login_required
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

# after chose the subject,book,chapter then store it all in session
@app.route("/setsession", methods=['GET', 'POST'])
@login_required
def setsession():
    if request.method == "POST":
        session["_chapter"] = request.form.get("chapter")
        return redirect("/test")

# get the question from database randomly
@app.route("/test", methods=['GET', 'POST'])
@login_required
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

# after answer a question, record corrects or wrongs
@app.route("/record", methods=["GET", "POST"])
@login_required
def record():
    # get the result for the question
    result = request.form.get("result")
    qid = request.form.get("qid")
    corrects = (int(request.form.get("corrects")) + 1)
    wrongs = (int(request.form.get("wrongs")) + 1)

    # creat a cursor
    cur = mysql.connection.cursor()

    if result == '1':
        cur.execute("UPDATE questions SET corrects = {} WHERE qid = {}".format(corrects, qid))
    else:
        cur.execute("UPDATE questions SET wrongs = {} WHERE qid = {}".format(wrongs, qid))
    # commit the changes to the database
    mysql.connection.commit()

    # close it
    cur.close()

    return redirect("/test")
