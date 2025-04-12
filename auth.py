# Necessary Flask components and modules
from flask import Blueprint, render_template, request, redirect, url_for, session  # Flask helpers for routing, rendering, and sessions
from flask_bcrypt import Bcrypt  # Bcrypt for hashing passwords 
from database import db  # Imports the database instance for interacting with the database
from models import User  # Imports the User model to interact with the user table in the database

# Creates a Blueprint for authentication-related routes, also allows organizing routes into modular components
auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()  # Initialize bcrypt for hashing and checking passwords

# Route for login - handles both GET and POST requests
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # If the request method is POST (form submission)
    if request.method == 'POST':
        login = request.form['login']  # The user enters their login (email)
        password = request.form['password']  # The user enters their password (plaintext)

        # Attempt to retrieve the user from the database by their email
        user = User.query.filter_by(email=login).first()
        
        # If user exists and the entered password matches the stored hashed password
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store the user ID in the session (to track login state)
            return redirect(url_for('home'))  # Redirect to the home page after successful login
        else:
            return "Invalid credentials", 401  # Return error message if login fails

    # If the request is a GET (initial visit to the login page), render the login template
    return render_template('login.html')

# Route for logout - logs out the user and redirects to the login page
@auth.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user ID from the session (logging the user out)
    return redirect(url_for('auth.login'))  # Redirect to the login page after logout

# Route for sign-up - handles both GET and POST requests for user registration
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # If the request method is POST (form submission)
    if request.method == 'POST':
        first_name = request.form['first_name']  # User's first name
        last_name = request.form['last_name']  # User's last name
        email = request.form['email']  # User's email address
        password = request.form['password']  # The password entered by the user (plaintext)
        confirm_password = request.form['confirm_password']  # The password confirmation field

        # Check if the passwords match
        if password != confirm_password:
            return "Passwords do not match!", 400  # Return error if passwords don't match

        # Check if a user already exists with the given email
        if User.query.filter_by(email=email).first():
            return "User already exists!", 400  # Return error if user with email already exists

        # Hash the password using bcrypt before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')  # Hash and decode to a string

        # Create a new user instance and add it to the database
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
        db.session.add(new_user)  # Add the new user to the session
        db.session.commit()  # Commit the transaction to save the user in the database

        return redirect(url_for('auth.login'))  # Redirect to the login page after successful sign-up

    # If the request is a GET (initial visit to the sign-up page), render the sign-up template
    return render_template('signup.html')
