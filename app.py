from flask import Flask, render_template

import sqlite3

conn = None

app = Flask(__name__)


def createDB():
    global conn
    conn = sqlite3.connect("company.db")


    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	email TEXT NOT NULL UNIQUE,
	phone TEXT NOT NULL UNIQUE);
                 """)
    
    
def check_for_available_dates():
    global conn
    cursor = conn.execute("SELECT * FROM dates")
    for row in cursor:
        print(row)


# @app.route("/data")
# def choose_date():
    

@app.route('/')
def hello():
    createDB()
    return render_template('index.html',name="Ry")


@app.route('/login')
def login():
    return render_template('login.html')

app.run()