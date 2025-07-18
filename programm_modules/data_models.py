from flask_sqlalchemy import SQLAlchemy


# instanciate database
db = SQLAlchemy()

class AuthorModel(db.Model):
	"""Model for Author information"""
	__tablename__ = 'authors'


	id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing cause primary key
	name = db.Column(db.String(50), nullable=False)
	birth_date = db.Column(db.String(10), nullable=False) #(format: DD/MM/YYYY)
	date_of_death = db.Column(db.String(10), nullable=True)  #(format: DD/MM/YYYY)


	def __repr__(self):
		"""
		Developer-friendly representation of the instance.
		"""
		return (f"AuthorModel(id={self.id!r}, name='{self.name!r}', "
		        f"birth_date='{self.birth_date!r}', date_of_death='{self.date_of_death!r}')")


	def __str__(self):
		"""
		User-friendly representation of the instance.
		"""
		return (f"Author: {self.name}, born on {self.birth_date}"
		        f"{', died on ' + self.date_of_death if self.date_of_death else ''}")


class BookModel(db.Model):
	"""Model for Books and its information"""
	__tablename__ = 'books'  # Explicitly define the table name
	
	
	id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing cause primary key
	isbn = db.Column(db.String(13), unique=True, nullable=False)  # ISBN 13-typed
	title = db.Column(db.String(200), nullable=False)  # Title of the book
	publication_year = db.Column(db.Integer, nullable=False)
	author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)  # Foreign key to Author table


	# Define the relationship to the AuthorModel
	author = db.relationship('AuthorModel', backref=db.backref('books', lazy=True))
	
	
	def __repr__(self):
		"""
		Developer-friendly representation of the instance.
		"""
		return (f"BookModel(id={self.id!r}, isbn='{self.isbn!r}', title='{self.title!r}', "
		        f"publication_year={self.publication_year!r}, author_id={self.author_id!r})")


	def __str__(self):
		"""
		User-friendly representation of the instance.
		"""
		return f"Book: '{self.title}' (ISBN: {self.isbn}), published in {self.publication_year}"