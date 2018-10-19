import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
  return render_template("login.html")

@app.route("/register")
def register():
  return render_template("register.html")

@app.route("/books")
def books():
  books = db.execute("SELECT * FROM books").fetchall()
  return render_template("books.html", books=books)

@app.route("/login_user", methods=["POST"])
def login_user():
  print(request.form.get("username"))
  print(request.form.get("password"))
  print(request.form.get("rememberme"))
  
  try:
    username = request.form.get("username")
  except ValueError:
    return render_template("error_login_user.html", message="Invalid username.")

  try:
    password = request.form.get("password")
  except ValueError:
    return render_template("error_login_user.html", message="Invalid password")

  # check for the username and password
  if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 1:
    books = db.execute("SELECT * FROM books")
    return render_template("success_login_user.html", message="You have successfully logged into the system... awesome!", books= books)
  
  return render_template("error_login_user.html", message="Invalid Login attempt...")



@app.route("/register_user", methods=["POST"])
def register_user():
  print(request.form.get("username"))
  print(request.form.get("password"))
  print(request.form.get("rememberme"))

  rememberme = True if request.form.get("rememberme") == "on" else False 

  try:
    username = request.form.get("username")
  except ValueError:
    return render_template("error_register_user.html", message="Invalid username.")

  try:
    password = request.form.get("password")
  except ValueError:
    return render_template("error_register_user.html", message="Invalid password")

  # check if the same username exists in the database
  # if so return error
  if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 1:
    return render_template("error_register_user.html", message="User already exists..sorry!")
  db.execute("INSERT INTO users (username, password, rememberme) VALUES(:username, :password, :rememberme)", {"username": username, "password": password, "rememberme": rememberme})
  db.commit()
  return redirect(url_for('books'))
