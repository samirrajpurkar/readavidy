import os

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
import json
import urllib


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

@app.route("/search")
def search():
  return render_template("search.html")

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('index'))

@app.route("/books")
def books():
  books = db.execute("SELECT * FROM books").fetchall()
  return render_template("books.html", books=books)

@app.route("/api/<string:isbn_id>", methods=["GET"])
def book_api(isbn_id):
  """Return details about a single book."""
    
  res = requests.get('https://www.goodreads.com/book/review_counts.json', 
                      params = {
                        'key1': 'Uo253OAVQpF0dJzIH9w', 
                        'isbns': isbn_id })

  try:
    grbook = res.json()
  except ValueError:
    grbook = None
  
  if grbook is None:
    return jsonify({
      "error": "Invalid isbn on goodreads"
      }), 404

  # Make sure book exits.
  try:
    book = db.execute("SELECT * FROM BOOKS WHERE isbn = :isbn_id", {
      "isbn_id": isbn_id
      }).fetchone()
  except ValueError:
    return jsonify({
      "error": "select database error"
      }), 404

  if book is None:
    return jsonify({
      "error": "Invalid isbn from readavidy"
      }), 404

  return jsonify({
    "title": book.title,
    "author": book.author,
    "year": book.year,
    "isbn": grbook["books"][0].get('isbn'),
    "reviewcount": grbook["books"][0].get('reviews_count'),
    "averagescore": grbook["books"][0].get('average_rating')
    }), 200


@app.route("/search_record", methods=["POST"])
def search_record():
  
  print(request.form.get("isbn"))
  print(request.form.get("title"))
  print(request.form.get("author"))
  print(request.form.get("radio"))

  isbn = request.form.get("isbn")
  radio = request.form.get("radio")
  title = request.form.get("title")

  isbn = '%' + request.form.get("isbn") + '%'
  title = ('%' + request.form.get("title") + '%').lower()
  author = ('%' +request.form.get("author") + '%').lower()

  
  if request.form.get("radio") == "isbn":
    try:
      books = db.execute("SELECT * FROM BOOKS WHERE isbn like :isbn", {
        "isbn": isbn
        }).fetchall()  
      if (len(books) == 0):
        return render_template("books.html", books=books, message="Book not found", messagetype="error")  
    except ValueError:
      return render_template("books.html", books=books, message="Book not found", messagetype="error")
  elif request.form.get("radio") == 'title':
      try:
        books = db.execute("SELECT * FROM BOOKS WHERE lower(title) like :title", {
        "title": title
        }).fetchall()  
        if (len(books) == 0):
          return render_template("books.html", books=books, message="Book not found", messagetype="error")  
      except ValueError:
        return render_template("books.html", books=books, message="Book not found", messagetype="error")
  elif request.form.get("radio") == 'author':
      try:
        books = db.execute("SELECT * FROM BOOKS WHERE lower(author) like :author", {
        "author": author
        }).fetchall()  
        if (len(books) == 0):
          return render_template("books.html", books=books, message="Book not found", messagetype="error")  
      except ValueError:
        return render_template("books.html", books=books, message="Book not found", messagetype="error")
  else:
     return render_template("books.html", books=books, message="Book not found", messagetype="error")

  return render_template("books.html", books=books)

@app.route("/add_review", methods=["POST"])
def add_review():
  """Add review for that book"""

  rating = request.form.get("rating")
  try:
    review = request.form.get("review")
  except ValueError:
    return render_template("error.html", message="Invalid review.")
  username = request.form.get("username")
  try:
    user = db.execute("SELECT * FROM USERS WHERE username = :username", {
      "username": username
      }).fetchone()
  except ValueError:
    return render_template("error.html", message="Invalid review.")
  user_id = user.user_id
  book_id = request.form.get("book_id")

  try:
    db.execute("INSERT INTO REVIEWS (rating, review, user_id, book_id) VALUES(:rating, :review, :user_id, :book_id)", 
      {
        "rating": rating,
        "review": review,
        "user_id": user_id,
        "book_id": book_id
      })
    db.commit()
  except ValueError:
    return render_template("error.html", message="Error in inserting a new review")

  book = db.execute("SELECT * from BOOKS WHERE id = :book_id", {
    "book_id": book_id
    }).fetchone()

  reviews = db.execute("SELECT * FROM REVIEWS WHERE book_id = :book_id", {
    "book_id": book_id
    }).fetchall()


  return render_template("book.html", book=book, reviews = reviews, user_id=user_id, addreviews = False)


@app.route("/books/<int:book_id>")
def book(book_id):
  """Lists details about a single book."""

  book = db.execute("SELECT * FROM BOOKS WHERE id = :id", {
    "id": book_id,
    }).fetchone()

  # Get all reviews.
  reviews = db.execute("SELECT * FROM REVIEWS WHERE book_id = :book_id",
                            {"book_id": book_id}).fetchall()
  try:
    user = db.execute("SELECT * FROM USERS WHERE username = :username", {
      "username": session["username"]
      }).fetchone()
  except ValueError:
    return render_template("error.html", message="user not found!")

  # check if the review exists for that user_id
  # if yes then the user should not be able to add more reviews
  
  reviewfound = db.execute("SELECT * FROM REVIEWS WHERE user_id = :user_id AND book_id = :book_id", {
    "user_id": user.user_id,
    "book_id": book_id
    }).fetchone()

  if (reviewfound):
    addreviews = False
  else:
    addreviews = True

  return render_template("book.html", book=book, reviews = reviews, user_id=user.user_id, addreviews = addreviews)


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

  if username not in session:
    session["username"] = request.form.get("username")

  # check for the username and password
  if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 1:
    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("books.html", message="You have successfully logged into the system... awesome!", messagetype='success', books= books)
  
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

  if username not in session:
    session["username"] = request.form.get("username")

  # check if the same username exists in the database
  # if so return error
  if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 1:
    return render_template("error_register_user.html", message="User already exists..sorry!")
  db.execute("INSERT INTO users (username, password, rememberme) VALUES(:username, :password, :rememberme)", {"username": username, "password": password, "rememberme": rememberme})
  db.commit()
  books = db.execute("SELECT * FROM books").fetchall()
  return render_template("books.html", message="You have successfully registered into the system... awesome!", messagetype='success', books= books)
