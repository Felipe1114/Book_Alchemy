from flask import Flask, render_template, request, redirect, url_for, flash
import os
import requests
from programm_modules.data_models import db, AuthorModel, BookModel

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Für Flash-Messages

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


#Route zum Hinzufügen eines Autors
@app.route("/add_author", methods=["GET", "POST"])
def add_author():
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


# 2️⃣ Route zum Hinzufügen eines Buches
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
  authors = AuthorModel.query.all()  # Alle Autoren aus der Datenbank holen

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


# 3️⃣ Route für die Home-Seite
@app.route("/")
def home():
  books = BookModel.query.all()

  # Holt das Cover-Bild für jedes Buch über die ISBN
  for book in books:
    book.cover_url = get_book_cover(book.isbn)

  sort_by = "title"

  return render_template("home.html", books=books, sort_by=sort_by)


# 🔹 Hilfsfunktion zum Abrufen des Buchcovers (nutzt die Open Library API)
def get_book_cover(isbn):
  url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
  response = requests.get(url)

  if response.status_code == 200:
    return url  # Falls das Bild existiert, Rückgabe der URL
  return "/static/no_cover.png"  # Falls kein Bild gefunden wird, Standardbild anzeigen

@app.route("/sort_books")
def sort_books():
    sort_by = request.args.get("sort_by", "title")  # Standard: Sortierung nach Titel

    if sort_by == "title":
        books = BookModel.query.order_by(BookModel.title).all()
    elif sort_by == "author":
        books = BookModel.query.join(AuthorModel).order_by(AuthorModel.name).all()
    else:
        books = BookModel.query.all()

    for book in books:
        book.cover_url = get_book_cover(book.isbn)

    return render_template("home.html", books=books, sort_by=sort_by)

if __name__ == "__main__":
  app.run(debug=True)