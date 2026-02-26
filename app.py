from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

# Define app first to fix the NameError
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('maithri_fest.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS students (pin TEXT UNIQUE, mobile TEXT, branch TEXT, time TEXT)')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    pin = data.get('pin', '').upper().strip()
    
    # 1. Eligibility Condition
    try:
        prefix = int(pin.split('-')[0][:5])
        is_eligible = "295" in pin and (23295 <= prefix <= 28295)
    except:
        is_eligible = False

    if not is_eligible:
        return jsonify({"success": False, "message": "❌ You are not eligible for Maithri Fest"})

    # 2. Check if already registered
    conn = sqlite3.connect('maithri_fest.db')
    cursor = conn.cursor()
    cursor.execute("SELECT pin FROM students WHERE pin = ?", (pin,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"success": True, "already": True, "message": "You are already registered and you are eligible to the maithri fest"})

    # 3. New Registration
    cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?)", 
                   (pin, data.get('mobile'), data.get('branch'), datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "already": False, "message": "You are registered and eligible for Maithri Fest."})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)