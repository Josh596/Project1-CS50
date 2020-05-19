import os
import csv
from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)
app.secret_key = "onlymeshouldknow"

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



@app.route("/", methods = ["GET", "POST"])
def sign_in():
	msg = ""
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form.get('username')
		password = request.form.get('passowrd')
		account = db.execute("SELECT * FROM USERS WHERE USERNAME = :USERNAME AND PASSWORD = :PASSWORD", {"USERNAME": username, "PASSWORD": password}).fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['ID']
			session['username'] = account['USERNAME']
			return redirect(url_for('book'))
                                    

			
		else: 
			msg = "Invalid credentials"

	return render_template("Sign.html", msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('sign_in'))
    
    
 
@app.route("/sign_up", methods = ["GET", "POST"])
def sign_up():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']

		account = db.execute("SELECT * FROM USERS WHERE USERNAME = :USERNAME AND PASSWORD = :PASSWORD", {"USERNAME": username}).fetchone()

		if account:
			msg = 'account already exists'
			
		elif not username or not password:
			msg = 'Please fill out the form!'
			

		else:
			db.execute('INSERT INTO USERS (USERNAME, PASSWORD) VALUES (:USERNAME, :PASSWORD)', {"USERNAME":username, "PASSWORD":password})
			db.commit()
			msg = 'You have successfully registered!'
	return render_template("sign.html", msg = msg)
			
		
    
    # Show registration form with message (if any	
	
	
        
        
    
        
    

            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            
@app.route("/book", methods = ["GET", "POST"])
def book():
	if request.method == 'POST':
		username = request.form.get('username')
		return render_template('books.html', username = username )

	return url_for('sign_up')
        # User is loggedin show them the home page
        
    # User is not loggedin redirect to login page
    
	


