import os
import uuid
import sqlite3
from flask import Flask, render_template, request, send_file, redirect, url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
import io

app = Flask(__name__)

# Database Setup
def init_db():
    conn = sqlite3.connect('maithri_fest.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (name TEXT, pin TEXT, mobile TEXT, detail TEXT, category TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    pin = request.form.get('pin')
    mobile = request.form.get('mobile')
    detail = request.form.get('detail')
    category = request.form.get('category')

    # Save to Database
    conn = sqlite3.connect('maithri_fest.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (name, pin, mobile, detail, category))
    conn.commit()
    conn.close()

    return render_template('index.html', success=True, name=name, pin=pin, category=category)

@app.route('/download_ticket/<name>/<pin>/<category>')
def download_ticket(name, pin, category):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A6)
    width, height = A6

    # Ticket Design
    p.setFillColorRGB(0.1, 0.1, 0.3)
    p.rect(0, 0, width, height, fill=1)
    
    p.setStrokeColorRGB(1, 1, 1)
    p.setLineWidth(2)
    p.rect(5*mm, 5*mm, width-10*mm, height-10*mm)

    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height-25*mm, "MAITHRI FEST 2026")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width/2, height-35*mm, f"E-TICKET: {category.upper()}")

    p.setFont("Helvetica", 10)
    p.drawString(15*mm, height-55*mm, f"NAME: {name}")
    p.drawString(15*mm, height-65*mm, f"ID/PIN: {pin}")
    
    # VIP Special Message
    if category == 'vip':
        p.setFont("Helvetica-Oblique", 9)
        p.drawCentredString(width/2, 20*mm, "Guest of Honor - Entry via VIP Gate")

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Maithri_Ticket_{pin}.pdf", mimetype='application/pdf')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('maithri_fest.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    students = cursor.fetchall()
    
    cursor.execute("SELECT category, COUNT(*) FROM users GROUP BY category")
    counts = dict(cursor.fetchall())
    conn.close()
    
    return render_template('dashboard.html', students=students, counts=counts)

# CRITICAL RENDER PORT FIX
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
