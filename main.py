import os
import csv
import requests
from flask import Flask, session, render_template, request, url_for, jsonify
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



@app.route("/", methods = ['GET', 'POST'])
def login():	
	if request.method == "POST":
		email = request.form.get("email")
		User = db.execute("SELECT id FROM users WHERE email= :email", {"email": email}).fetchone()

		if User is not None:
			password = request.form.get("password")
			session["user_email"] = email
			session['user_id'] = User
			return render_template('books.html')
		else:
			return render_template('sign.html', work="Failed", error = 'User not registered')
	return render_template('sign.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        User = db.execute("SELECT id FROM users WHERE email= :email", {"email": email}).fetchone()
        # Checking if the user is registered
        if User is not None:
            return render_template("sign_up.html", work="Failed")
        password = request.form.get("password")


        db.execute("INSERT INTO users (email, password) VALUES (:email, :password)",
        {"email": email, "password": password})
        db.commit()                   
        return render_template('sign.html')       
    return render_template("sign_up.html")


@app.route("/logout")
def logout():
    try:
        session.pop("user_email")
    except KeyError:
        return render_template("sign.html", work="Failed", error="Please Login First")
    return render_template("sign.html", work = 'Success')


@app.route("/books", methods = ["GET", "POST"])
def books():
	if request.method == "POST":		
		return render_template('books.html')
	
	return render_template('sign.html', work = "Failed", error = 'Please Sign in')

@app.route("/search", methods = ["GET", "POST"])
def search():
	if "user_email" not in session:
		return render_template("sign.html", error="Please Login First", work="Failed")

	if request.method == 'POST':
		searchs = []
		title = request.form.get('title')
		author = request.form.get('author')
		isbn = request.form.get('isbn')					
		if title is not "":
			titles = db.execute("SELECT * FROM books WHERE title iLIKE '%"+title+"%'").fetchall()
			searchs.append(titles)
		if author is not "":
			authors = db.execute("SELECT * FROM books WHERE author iLIKE '%"+author+"%'").fetchall()
			searchs.append(authors)
		if isbn is not "":
			isbns = db.execute("SELECT * FROM books WHERE author iLIKE '%"+isbn+"%'").fetchall()
			searchs.append(isbns)
		if len(searchs) == 0:
			return render_template('books.html', work = 'Failed')					
		return render_template('search.html', work = 'Success', searchs = searchs )
	
	return render_template("sign.html", error = "Login", work = "Failed")

@app.route("/result/<int:book_id>", methods = ["GET", "POST"])
def result(book_id):

	if "user_email" not in session:
		return render_template("sign.html", error ="Please Login First", work="Failed")

	book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": book_id}).fetchone()
	if book is None:
		return render_template('books.html', work = 'Failed')

    # When review if submitted for the book.
	if request.method == "POST":
		user_id = session["user_id"][0]
		rating = request.form.get("rating")
		comment = request.form.get("comment")
		if db.execute("SELECT id FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                      {"user_id": user_id, "book_id": book_id}).fetchone() is None:
			db.execute(
                "INSERT INTO reviews (user_id, book_id, rating, comment) VALUES (:user_id, :book_id, :rating, :comment)",
                {"book_id": book.id, "user_id": user_id, "rating": rating, "comment": comment})
		else:
			db.execute(
			    "UPDATE reviews SET comment = :comment, rating = :rating WHERE user_id = :user_id AND book_id = :book_id",
			    {"comment": comment, "rating": rating, "user_id": user_id, "book_id": book_id})
		db.commit()

    #Goodreads API#
    # Processing the json data
	res = requests.get("https://www.goodreads.com/book/review_counts.json",
	           params={"key": "HD8qbAr9QIMZRCGGI5cEkQ", "isbns": book.isbn}).json()["books"][0]

	ratings_count = res["ratings_count"]
	average_rating = res["average_rating"]
	reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
	users = []
	for review in reviews:
		email = db.execute("SELECT email FROM users WHERE id = :user_id", {"user_id": review.user_id}).fetchone().email
		users.append((email, review))

	return render_template("result.html", book=book, users=users,
                           ratings_count=ratings_count, average_rating=average_rating, user_email=session["user_email"])



    
    
    
	 
       
