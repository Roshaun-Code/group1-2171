# Import the SQLAlchemy class from the flask_sqlalchemy extension
from flask_sqlalchemy import SQLAlchemy

# Create an instance of SQLAlchemy to interact with the database
# This object will be used to define models and interact with the database
db = SQLAlchemy()

def create_db(app):
    """Create the database if it doesn't exist."""
    # 'app.app_context()' ensures that the code inside runs within the Flask application context
    # This is necessary to interact with the database and other app components
    with app.app_context():
        # Check if the tables exist, and if not, create them
        # 'db.create_all()' creates all the tables defined by the models if they don't exist already
        db.create_all()  # This will create all tables in the database, including User and others if defined
