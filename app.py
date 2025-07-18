from flask import Flask, render_template, request, redirect, url_for, flash, json, jsonify
from werkzeug.exceptions import HTTPException
import os
import requests
from programm_modules.data_models import db, AuthorModel, BookModel
from programm_modules.pydantic_models import Author, Book
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__) # init app
app.secret_key = "supersecretkey"  # for flash-massages



def initialize():
	"""checks data path and initialices database"""
	try:
		# checks if dir for database exist
		if not os.path.exists("data"):
			raise HTTPException(description="'Dir' for database does not exist!!!")
		
		# create absolute path for sql-lite db. Path should be: main_dir/Book_Alchemy/data/library.sqlite
		basedir = os.path.abspath(os.path.dirname(__file__))
		app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data', 'library.sqlite')}"
		
		# this will connect the Flask app to the flask-sqlalchemy code
		db.init_app(app)
	
	except HTTPException as e:
		handle_HTTPexception(e)
	
	except SQLAlchemyError as e:
		handle_SQLalchemy_error(e)
		

@app.route("/add_author", methods=["GET", "POST"])
def add_author():
	"""Posts an new Author"""
	if request.method == "POST":
		name = request.form["name"]
		birth_date = request.form["birthdate"]
		date_of_death = request.form["date_of_death"]
		
		# checks with Pydantic if the input values are correct
		py_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
		
		new_author = AuthorModel(name=py_author.name, birth_date=py_author.birth_date, date_of_death=py_author.date_of_death)
		db.session.add(new_author)
		db.session.commit()
		
		flash("Author successfully added!", "success")
		# loads the side 'add_author.html' new
		return redirect(url_for("add_author"))

	return render_template("add_author.html")
	
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
	"""Posts a book"""
	authors = AuthorModel.query.all()  # get all authors
	
	if request.method == "POST":
		title = request.form["title"]
		isbn = request.form["isbn"]
		publication_year = request.form["publication_year"]
		author_id = request.form["author_id"]
		
		# checks with Pydantic if the input values are correct
		py_book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id)
		
		new_book = BookModel(title=py_book.title, isbn=py_book.isbn, publication_year=py_book.publication_year, author_id=py_book.author_id)
		
		db.session.add(new_book)
		db.session.commit()
		
		flash("Book successfully added!", "success")
		return redirect(url_for("add_book"))

	return render_template("add_book.html", authors=authors)


@app.route("/")
def home():
	"""base route, returns home.html file"""
	books = BookModel.query.all()
	
	# gets coverbook for books
	for book in books:
		book.cover_url = get_book_cover(book.isbn)

	sort_by = "title"

	return render_template("home.html", books=books, sort_by=sort_by)


@app.route("/sort_books", methods=["GET"])
def sort_books():
	"""sort books by 'title' or 'author'"""
	sort_by = request.args.get("sort_by", "title")  # default: sort by title
	
	if sort_by == "title":
		books = BookModel.query.order_by(BookModel.title).all()
	elif sort_by == "author":
		books = BookModel.query.join(AuthorModel).order_by(AuthorModel.name).all()
	else:
		books = BookModel.query.all()
	
	for book in books:
		book.cover_url = get_book_cover(book.isbn)
	
	return render_template("home.html", books=books, sort_by=sort_by)
	
	
@app.route("/search_books", methods=["GET"])
def search_books():
	"""search books by name or word in book title"""
	query = request.args.get("query", "").strip()
	
	if not query:
		return render_template("home.html", books=[], message="Please enter a search term.")
	
	# SQLAlchemy LIKE Query (finds books, with word in title)
	search_results = BookModel.query.filter(BookModel.title.ilike(f"%{query}%")).all()
	
	if not search_results:
		return render_template("home.html", books=[], message="No books found.")
	
	return render_template("home.html", books=search_results)

	
@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
	"""delete a book by its id"""
	book = BookModel.query.get_or_404(book_id)  # get book or 404 Error
	author = book.author  # save book-author from boook
	
	db.session.delete(book)
	db.session.commit()  # delete book
	
	# If the author has no other books, delete him/her
	if not author.books:
		db.session.delete(author)
		db.session.commit()
	
	flash("Book deleted successfully!", "success")
	
	return redirect(url_for("home"))  # redirect zu home.html


def get_book_cover(isbn):
	"""gets the book-covers for all books, from 'opernlibrary.org'"""
	try:
		url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
		response = requests.get(url)
		
		if response.status_code == 200:
			return url
		
		# if no book-cover exist, return base cover book.
		return get_absolute_path_for_static_book_cover()
	
	except HTTPException as e:
		handle_HTTPexception(e)

import os

def get_absolute_path_for_static_book_cover():
	"""
	Returns the absolute path up to the 'Book_Alchemy' directory.
	"""
	# Get the absolute path of the current script
	current_script_path = os.path.abspath("./static/no_book_cover.jpg")
	
	# Navigate up the directory tree until we find 'Book_Alchemy'
	path_parts = current_script_path.split(os.sep)
	
	# Find the index of 'Book_Alchemy' in the path
	try:
		book_alchemy_index = path_parts.index('Book_Alchemy')
	except ValueError:
		raise HTTPException("The directory 'Book_Alchemy' was not found in the path")
	
	# Reconstruct the path up to 'Book_Alchemy'
	absolute_path = os.path.join(os.sep, *path_parts[:book_alchemy_index + 1])
	
	return absolute_path


@app.errorhandler(ValidationError)
def handle_validation_error(e):
	"""Handle Pydantic validation errors."""
	return jsonify({
	    "error": "Validation Error",
	    "message": "Wrong input for Author!",
	    "details": str(e)
	}), 400  # Bad Request status code


@app.errorhandler(HTTPException)
def handle_HTTPexception(e):
	"""Return JSON instead of HTML for HTTP errors."""
	# start with the correct headers and status code from the error
	response = e.get_response()
	# replace the body with JSON
	response.data = json.dumps({
	    "code": e.code,
	    "name": e.name,
	    "description": e.description,
	})
	response.content_type = "application/json"
	return response


@app.errorhandler(SQLAlchemyError)
def handle_SQLalchemy_error(e):
	"""Handle Pydantic validation errors."""
	return jsonify({
	    "error": "Internal Server Error",
	    "message": "Database Error!",
	    "details": str(e)
	}), 500  # Internal server Error code

	
if __name__ == "__main__":
	initialize()
	app.run(host="127.0.0.1", port=5002, debug=True)