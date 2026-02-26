from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# This creates the database file automatically
DB_FILE = 'maithri_fest.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pin TEXT UNIQUE,
            mobile TEXT,
            branch TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    pin = data.get('pin', '').strip().upper()
    mobile = data.get('mobile', '').strip()
    branch = data.get('branch', '').strip()

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if student is already registered
        cursor.execute("SELECT * FROM students WHERE pin = ?", (pin,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "This PIN is already registered!"})

        # Save to database
        cursor.execute("INSERT INTO students (pin, mobile, branch) VALUES (?, ?, ?)", 
                       (pin, mobile, branch))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Registration Successful!"})
    except Exception as e:
        return jsonify({"success": False, "message": "Database Error. Try again."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
