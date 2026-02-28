from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import uuid # For unique QR tokens

app = Flask(__name__)
DB_FILE = 'maithri_fest.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Optimized table for 25,000+ entries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            pin_or_id TEXT UNIQUE,
            mobile TEXT,
            branch_or_job TEXT,
            category TEXT,
            token TEXT UNIQUE
        )
    ''')
    # Indexing for faster searching during security checks
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_token ON participants(token)")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    category = data.get('category') 
    name = data.get('name', '').strip()
    mobile = data.get('mobile', '').strip()
    pin_id = data.get('pin_id', '').strip()
    detail = data.get('detail', '').strip()
    
    # Validation
    if not name or not pin_id or not detail:
        return jsonify({"success": False, "message": "All fields are required!"})
    
    if not mobile.isdigit() or len(mobile) != 10:
        return jsonify({"success": False, "message": "Mobile Number must be exactly 10 digits!"})

    # Unique Token for QR Security
    token = str(uuid.uuid4().hex)[:12] 

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO participants (name, pin_or_id, mobile, branch_or_job, category, token) VALUES (?, ?, ?, ?, ?, ?)", 
                       (name, pin_id, mobile, detail, category, token))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Registration Successful!", "token": token})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "This PIN/ID is already registered!"})

# PRIVATE DASHBOARD 
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) FROM participants GROUP BY category")
    counts = dict(cursor.fetchall())
    cursor.execute("SELECT name, pin_or_id, mobile, branch_or_job, category FROM participants ORDER BY id DESC")
    all_data = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', counts=counts, students=all_data)

# SECURITY CHECK ROUTE (Scanned by guards)
@app.route('/verify/<token>')
def verify(token):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, category, branch_or_job FROM participants WHERE token = ?", (token,))
    user = cursor.fetchone()
    conn.close()
    if user:
        color = "#4dfa6d" if user[1] == 'student' else "#f1c40f"
        return f"""
        <div style="font-family:sans-serif; text-align:center; padding:50px; background:#1a1a1a; color:white; height:100vh;">
            <h1 style="color:{color}; font-size:3rem;">✅ VALID ENTRY</h1>
            <hr style="border:0; border-top:1px solid #333; margin:20px 0;">
            <h2>Name: {user[0]}</h2>
            <h3>Category: {user[1].upper()}</h3>
            <p>Detail: {user[2]}</p>
            <p style="margin-top:50px; color:#aaa;">Verified for Maithri Fest 2026</p>
        </div>
        """
    return "<body style='background:red; color:white; text-align:center;'><h1>❌ INVALID PASS</h1></body>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
