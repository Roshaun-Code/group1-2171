# Import the database instance (db) from the database module
from database import db

# Define the User model class, which represents the 'users' table in the database
# This class inherits from 'db.Model', making it a SQLAlchemy model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # The 'id' column is an integer and serves as the primary key for the table
    first_name = db.Column(db.String(80), nullable=False) # The 'first_name' column stores the user's first name (up to 80 characters)
    last_name = db.Column(db.String(80), nullable=False)  # The 'last_name' column stores the user's last name (up to 80 characters)
    email = db.Column(db.String(120), unique=True, nullable=False)  # The 'email' column stores the user's email address (up to 120 characters) and the 'unique=True' means every email should be unique
    password = db.Column(db.String(200), nullable=False)  # This will store the hashed password for security purposes
    # When 'nullable=Flase' the column must have data in it

# Event Model to store event details
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)  # Required field
    makeup_artist_name = db.Column(db.String(255), nullable=False)  # Required field
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    services = db.relationship('ServicePackage', backref='event', lazy=True)

# Service Package Model to store service offerings
class ServicePackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

# Booking Model to store booking information and prevent conflicts
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, unique=True)  # Ensure no double bookings

# # Portfolio Model to store portfolio items
# class PortfolioItem(db.Model):
#     id = db.Column(db.Integer, primary_key=True)  # Unique ID for the portfolio item
#     title = db.Column(db.String(100), nullable=False)  # Title of the portfolio item
#     filename = db.Column(db.String(200), nullable=False)  # File name of the uploaded file
#     category = db.Column(db.String(50), nullable=False)  # Category for the portfolio item (e.g., 'Bridal', 'Birthday', etc.)

#     def __repr__(self):
#         return f'<PortfolioItem {self.title}>'