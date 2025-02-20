from flask import Flask, render_template, request, redirect, url_for, flash
import os
import requests
from programm_modules.data_models import db, AuthorModel, BookModel

app = Flask(__name__) # init app
app.secret_key = "supersecretkey"  # for flash-messeges

# for the first sql init:
if not os.path.exists("data"):
  os.makedirs("data")

# create absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data', 'library.sqlite')}"

# this will connect the Flask app to the flask-sqlalchemy code
db.init_app(app)

# fills the databse with the tables (DONE)
#with app.app_context():
#  db.create_all()


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
  """Posts an author"""
  if request.method == "POST":
    name = request.form["name"]
    birth_date = request.form["birthdate"]
    date_of_death = request.form["date_of_death"]

    new_author = AuthorModel(name=name, birth_date=birth_date, date_of_death=date_of_death or None)
    db.session.add(new_author)
    db.session.commit()

    flash("Author successfully added!", "success")
    # lädt die seite 'add_author.html' neu
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

    new_book = BookModel(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id)
    db.session.add(new_book)
    db.session.commit()

    flash("Book successfully added!", "success")
    return redirect(url_for("add_book"))

  return render_template("add_book.html", authors=authors)


@app.route("/")
def home():
  """base route"""
  books = BookModel.query.all()

  # gets coverbook für books
  for book in books:
    book.cover_url = get_book_cover(book.isbn)

  sort_by = "title"

  return render_template("home.html", books=books, sort_by=sort_by)


def get_book_cover(isbn):
  """gets the book-covers for all books, from 'opernlibrary.org'"""
  url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
  response = requests.get(url)

  if response.status_code == 200:
    return url
  return "/static/no_book_cover.jpg"  # if no cover book

@app.route("/sort_books")
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


if __name__ == "__main__":
  app.run(debug=True)