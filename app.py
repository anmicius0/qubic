import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

app = Flask(__name__)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def welcome():
    return render_template("index.html")

# let user register for this system
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""


    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        con = sql.connect("quiz.db")
        db = con.cursor()

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Missing USER NAME")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("MISSING PASSWORD")

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("PASSWORDD DOESN'T MATCH")

        hashpass = generate_password_hash(request.form.get("confirmation"))

        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hashh)", username = request.form.get("username"), hashh = hashpass)
        if not result:
            return apology("the user name already exist")

        # start to login
        # Forget any user_id
        session.clear()

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
            username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/book")
def menu():

    # get the search text
    sub = request.args.get("subject")

    # Show portfolio of stocks
    rows = db.execute("SELECT * FROM books WHERE subject = :subject ORDER BY book", subject = sub)

    return render_template("menu.html", lens = len(rows), item = rows)

@app.route("/chps")
def menu2():

    re = request.args.get("re")

    sub,book = re.split("%2C")

    # get the book chosed
    book = request.args.get("book")

    # Show portfolio of stocks
    rows = db.execute("SELECT * FROM chps WHERE subject = :subject AND book = :book ORDER BY book", subject = sub, book = book)

    return render_template("menu2.html", lens = len(rows), item = rows)

if __name__ =='__main__':
    app.run(debug=True)
