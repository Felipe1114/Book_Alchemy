from app import app
from programm_modules.data_models import db

with app.app_context():
    db.create_all()  # creates tables in database
    print("Database tables created successfully.")
