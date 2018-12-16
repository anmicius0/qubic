import os
import yaml

from flask import Flask, flash, redirect, render_template, request, session, g, make_response, url_for
from flask_mysqldb import MySQL
from flask_session import Session
from functools import wraps
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
mysql = MySQL(app)


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
            flash("register success")
            return redirect('/login')
        except:
            flash("register failed")
            return redirect('/register')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

# let user to login, it also clean the session of 'user_id'
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.pop('user_id', None)

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
            flash("can't find user")
            return redirect("/login")

        # Remember which user has logged in
        for row in userDetail:
            # check the hash
            if not check_password_hash(row[2], password):
                flash("Wrong password")
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

# it's the home page, let user to chose the subject
# login_required
@app.route("/home")
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
@app.route("/books", methods=['POST'])
def books():
    # get the form data
    sub = request.form.get("subject")

    # creat a cursor
    cur = mysql.connection.cursor()
    # query db for books
    cur.execute("SELECT * from books WHERE subID = %s ORDER BY book", [sub])
    objects = cur.fetchall()

    # store the subject into a cookie
    resp = make_response(render_template("home2.html", objects = objects))
    resp.set_cookie('sub', sub)

    return resp

# chose the chapter
@app.route("/chapters", methods=['POST'])
def chapters():

    # get the cookie data
    sub = request.cookies.get('sub')
    book = request.form.get('book')


    # creat a cursor
    cur = mysql.connection.cursor()
    # query the db
    cur.execute("SELECT * from chapters WHERE subID = %s AND book = %s ORDER BY chapter",
    (sub, book))
    objects = cur.fetchall()

    resp = make_response(render_template("home3.html", objects = objects))
    resp.set_cookie('book', book)

    return resp

# after chose the subject,book,chapter then store it all in session
@app.route("/setsession", methods=['POST'])
def setsession():
    chapter = request.form.get("chapter")

    resp = make_response(redirect("/test"))
    resp.set_cookie('chapter', chapter)

    return resp

# get the question from database randomly
# login_required
@app.route("/test", methods=['GET','POST'])
def text():
    # get the session data
    sub = request.cookies.get('sub')
    book = request.cookies.get('book')
    chapter = request.cookies.get('chapter')

    # creat a cursor
    cur = mysql.connection.cursor()
    # query the db
    cur.execute("SELECT * from questions WHERE subID = %s AND book = %s AND chapter = %s ORDER BY RAND() LIMIT 1",
    (sub, book, chapter))
    objects = cur.fetchall()

    return render_template("test.html", objects = objects)

# after answer a question, record corrects or wrongs
@app.route("/record", methods=["POST"])
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

# for user to submit a new question
# login_required
@app.route("/submit-question", methods=["GET", "POST"])
def submit_question():
    if request.method == "POST":
        subID = request.form.get('subID')
        book = int(request.form.get('book'))
        chapter = int(request.form.get('chapter'))
        content = request.form.get('content')
        op1 = request.form.get('op1')
        op2 = request.form.get('op2')
        op3 = request.form.get('op3')
        op4 = request.form.get('op4')
        answer = request.form.get('answer')
        solution = request.form.get('solution')

        try:
            # make a cursor
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO questions(content, op1, op2, op3, op4, answer, solution, subID, book, chapter) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (content, op1, op2, op3, op4, answer, solution, subID, book, chapter))
            mysql.connection.commit()
            cur.close()
            flash("Submit successfully")
            return redirect("/submit-question")
        except:
            flash("Submit failed")
            return redirect("/submit-question")
    else:
        return render_template("submit-question.html")
