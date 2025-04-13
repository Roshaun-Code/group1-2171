from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from portfolio import portfolio_bp, db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'roshaun'

# Database Setup
def createDB():
    conn = sqlite3.connect("company.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('client', 'admin'))
    );
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS dates(
        date TEXT PRIMARY KEY,
        booked BOOLEAN NOT NULL);
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reason TEXT NOT NULL,
        artist TEXT NOT NULL);
    """)

    #  New table for Requirement 6  
    conn.execute("""
    CREATE TABLE IF NOT EXISTS feedback(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        comments TEXT NOT NULL,
        rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5)
    );
    """)
    conn.commit()
    conn.close()

createDB()

def createEventsDB():
    conn = sqlite3.connect("events.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT NOT NULL,
        event_date TEXT NOT NULL,
        location TEXT NOT NULL,
        artist_name TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

createEventsDB()

def createClientsDB():
    conn = sqlite3.connect("clients.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL UNIQUE,
        preferences TEXT,
        event_requirements TEXT
    );
    """)
    conn.commit()
    conn.close()

createClientsDB()

# Flask Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

# Initialize database with Flask app
db.init_app(app)

# Register Portfolio Blueprint
app.register_blueprint(portfolio_bp, url_prefix='/portfolio')

def login_required(role=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash("You need to log in first.", "warning")
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'client':
            return render_template('home.html', role='client')  # Render home page for clients
        elif session['role'] == 'admin':
            return render_template('home.html', role='admin')  # Render home page for admins
    return redirect(url_for('welcome'))  # Redirect unauthenticated users to the welcome page

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/booking')
@login_required(role='client')
def hello():
    return render_template('index.html', name="Ry")

@app.route("/product")
@login_required(role='client')
def product():
    return render_template('product.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect("company.db")
        cursor = conn.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            flash(f"Welcome, {user[1]}!", "success")
            return redirect(url_for('index'))  # Redirect to the index route
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('welcome'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')  # 'client' or 'admin'

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("company.db")
        try:
            conn.execute("INSERT INTO users(username, password, role) VALUES(?, ?, ?)", (username, hashed_password, role))
            conn.commit()
            flash("User registered successfully! Please log in.", "success")
            return redirect(url_for('welcome'))  # Redirect to the welcome page
        except sqlite3.IntegrityError:
            flash("Username already exists", "danger")
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/create_event', methods=['GET', 'POST'])
@login_required(role='admin')
def create_event():
    if request.method == 'POST':
        # Retrieve form data
        event_name = request.form.get('event_name')
        event_date = request.form.get('event_date')
        location = request.form.get('location')
        artist_name = request.form.get('artist_name')

        # Validate form data
        if not event_name or not event_date or not location or not artist_name:
            return "All fields are required!", 400

        # Save the event to the events database
        conn = sqlite3.connect("events.db")
        conn.execute(
            "INSERT INTO events(event_name, event_date, location, artist_name) VALUES(?, ?, ?, ?)",
            (event_name, event_date, location, artist_name)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('events'))  # Redirect to the events page after saving

    return render_template('create_event.html')

@app.route('/events')
@login_required(role='client')
def events():
    conn = sqlite3.connect("events.db")
    cursor = conn.execute("SELECT id, event_name, event_date, location, artist_name FROM events")
    events = [{"id": row[0], "name": row[1], "date": row[2], "location": row[3], "artist": row[4]} for row in cursor.fetchall()]
    conn.close()
    return render_template('events.html', events=events)

from datetime import datetime

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    conn = sqlite3.connect("events.db")
    if request.method == 'POST':
        # Update the event in the database
        new_event_name = request.form.get('event_name')
        new_event_date = request.form.get('event_date')
        new_location = request.form.get('location')
        new_artist_name = request.form.get('artist_name')

        conn.execute(
            "UPDATE events SET event_name = ?, event_date = ?, location = ?, artist_name = ? WHERE id = ?",
            (new_event_name, new_event_date, new_location, new_artist_name, event_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('events'))

    # Fetch the event details for editing
    cursor = conn.execute("SELECT id, event_name, event_date, location, artist_name FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()
    if event:
        # Format the event_date for the datetime-local input
        formatted_date = datetime.strptime(event[2], "%Y-%m-%dT%H:%M").strftime("%Y-%m-%dT%H:%M")
        return render_template('edit_event.html', event={
            "id": event[0],
            "name": event[1],
            "date": formatted_date,
            "location": event[3],
            "artist": event[4]
        })
    else:
        return "Event not found", 404
    
@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    conn = sqlite3.connect("events.db")
    conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('events'))

@app.route('/clients')
@login_required(role='admin')
def clients():
    conn = sqlite3.connect("clients.db")
    cursor = conn.execute("SELECT id, name, email, phone, preferences, event_requirements FROM clients")
    clients = [{"id": row[0], "name": row[1], "email": row[2], "phone": row[3], "preferences": row[4], "event_requirements": row[5]} for row in cursor.fetchall()]
    conn.close()
    return render_template('clients.html', clients=clients)

@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        preferences = request.form.get('preferences')
        event_requirements = request.form.get('event_requirements')

        conn = sqlite3.connect("clients.db")
        conn.execute(
            "INSERT INTO clients(name, email, phone, preferences, event_requirements) VALUES(?, ?, ?, ?, ?)",
            (name, email, phone, preferences, event_requirements)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('clients'))

    return render_template('add_client.html')

@app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    conn = sqlite3.connect("clients.db")
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        preferences = request.form.get('preferences')
        event_requirements = request.form.get('event_requirements')

        conn.execute(
            "UPDATE clients SET name = ?, email = ?, phone = ?, preferences = ?, event_requirements = ? WHERE id = ?",
            (name, email, phone, preferences, event_requirements, client_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('clients'))

    cursor = conn.execute("SELECT id, name, email, phone, preferences, event_requirements FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    conn.close()
    if client:
        return render_template('edit_client.html', client={
            "id": client[0],
            "name": client[1],
            "email": client[2],
            "phone": client[3],
            "preferences": client[4],
            "event_requirements": client[5]
        })
    else:
        return "Client not found", 404

@app.route('/date', methods=['POST'])
def home():
    date = request.form.get("datetime")
    if date:
        if isUniqueDate(date):
            try:
                conn = sqlite3.connect("company.db")
                conn.execute("INSERT INTO dates(date, booked) VALUES(?, ?)", (date, 0))
                conn.commit()
                conn.close()
                return f"<textarea name='disabled' disabled>{date} has been booked successfully</textarea>"
            except sqlite3.Error as e:
                return f"<textarea name='disabled' disabled>Database error: {e}</textarea>"
        else:
            return f"<textarea name='disabled' disabled>{date} already exists in database, please try another date or time</textarea>"
    return "<textarea name='disabled' disabled>We couldn't process your request</textarea>"

@app.route('/bookings')
@login_required(role='admin')
def bookings():
    conn = sqlite3.connect("company.db")
    cursor = conn.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()
    conn.close()
    return render_template("bookings.html", bookings=bookings)

@app.route('/register', methods=['POST'])
def book():
    reason = request.form.get("reason")
    artist = request.form.get("phase")

    conn = sqlite3.connect("company.db")
    conn.execute("INSERT INTO bookings(reason, artist) VALUES(?, ?)", (reason, artist))
    conn.commit()
    conn.close()

    return f"<textarea readonly> Your booking with {artist} is scheduled </textarea>"

@app.route("/cancel", methods=['POST'])
def cancel():
    id = request.form.get("booking_id")
    if not id:
        return "<textarea readonly> Invalid Booking ID </textarea>"

    conn = sqlite3.connect("company.db")
    conn.execute("DELETE FROM bookings WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return f"<textarea readonly> Booking with id {id} has been cancelled </textarea>"



@app.route('/feedback', methods=['GET', 'POST'])
@login_required(role='client')
def feedback():
    conn = sqlite3.connect("company.db")
    try:
        if request.method == 'POST':
            # Retrieve form data
            client_name = request.form.get('client_name')
            comments = request.form.get('comments')
            rating = request.form.get('rating')

            # Validate form data
            if not client_name or not comments or not rating:
                return "All fields are required!", 400

            # Save feedback to the database
            conn.execute(
                "INSERT INTO feedback(client_name, comments, rating) VALUES(?, ?, ?)",
                (client_name, comments, int(rating))
            )
            conn.commit()
            return redirect(url_for('feedback'))  # Redirect to the feedback page after submission

        # Fetch all feedback from the database
        cursor = conn.execute("SELECT client_name, comments, rating FROM feedback")
        feedback_list = [{"client_name": row[0], "comments": row[1], "rating": row[2]} for row in cursor.fetchall()]
        return render_template('feedback.html', feedback_list=feedback_list)
    finally:
        conn.close()  # Ensure the connection is closed

@app.route('/feedback_summary')
@login_required(role='admin')
def feedback_summary():
    conn = sqlite3.connect("company.db")
    cursor = conn.execute("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as total_feedback
        FROM feedback
    """)
    summary = cursor.fetchone()
    conn.close()

    return render_template('feedback_summary.html', avg_rating=summary[0], total_feedback=summary[1])

def isUniqueDate(date):
    conn = sqlite3.connect("company.db")
    cursor = conn.execute("SELECT * FROM dates WHERE date = ?", (date,))
    result = cursor.fetchone()
    conn.close()
    return result is None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
