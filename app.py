from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from portfolio import portfolio_bp, db

app = Flask(__name__)

# Database Setup
def createDB():
    conn = sqlite3.connect("company.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL UNIQUE);
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
    # New table for Requirement 5
    conn.execute("""
    CREATE TABLE IF NOT EXISTS services(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        package_name TEXT NOT NULL,
        service1 TEXT NOT NULL,
        service2 TEXT NOT NULL,
        service3 TEXT NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
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

# Flask Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

# Initialize database with Flask app
db.init_app(app)

# Register Portfolio Blueprint
app.register_blueprint(portfolio_bp, url_prefix='/portfolio')

# Routes
@app.route('/')
def index():
    return redirect(url_for('hello'))

@app.route('/booking')
def hello():
    return render_template('index.html', name="Ry")

@app.route("/product")
def product():
    return render_template('product.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == 'POST':
        # Retrieve form data
        event_name = request.form.get('event_name')
        event_date_time = request.form.get('event_date_time')
        location = request.form.get('location')
        makeup_artist_name = request.form.get('makeup_artist_name')

        # Validate the form data
        if not event_name or not event_date_time or not location or not makeup_artist_name:
            return "<textarea readonly>All fields are required!</textarea>", 400

        # Save the event to the database
        conn = sqlite3.connect("company.db")
        conn.execute(
            "INSERT INTO bookings(reason, artist) VALUES(?, ?)",
            (event_name, makeup_artist_name)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('events'))  # Redirect to the events page after saving

    # Fetch events from the database
    conn = sqlite3.connect("company.db")
    cursor = conn.execute("SELECT id, reason, artist FROM bookings")
    events = [{"id": row[0], "name": row[1], "artist": row[2]} for row in cursor.fetchall()]
    conn.close()

    # Render the events page with the events list
    return render_template('events.html', events=events)

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    conn = sqlite3.connect("company.db")
    if request.method == 'POST':
        # Update the event in the database
        new_reason = request.form.get('reason')
        new_artist = request.form.get('artist')
        conn.execute(
            "UPDATE bookings SET reason = ?, artist = ? WHERE id = ?",
            (new_reason, new_artist, event_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('events'))

    # Fetch the event details for editing
    cursor = conn.execute("SELECT id, reason, artist FROM bookings WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()
    if event:
        return render_template('edit_event.html', event={"id": event[0], "reason": event[1], "artist": event[2]})
    else:
        return "Event not found", 404
    
@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    conn = sqlite3.connect("company.db")
    conn.execute("DELETE FROM bookings WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('events'))

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
