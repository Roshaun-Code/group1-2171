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

@app.route('/events')
def events():
    return render_template('events.html')

# @app.route('/upload')
# def upload():
#     return render_template('portfolioupload.html')

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
