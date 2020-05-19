import os
import csv
from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem

engine = create_engine('DATABASE_URL')
db = scoped_session(sessionmaker(bind=engine))

f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader:
    db.execute("INSERT INTO books (ISBN, title, author, year) VALUES (:ISBN, :title, :author, :year)",
               {"ISBN": isbn, "title": title, "author": author, "year": year})