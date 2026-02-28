import os
import sqlite3
from flask import Flask, render_template, request, send_file, io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('maithri_fest.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (name TEXT, pin TEXT, mobile TEXT, branch TEXT, category TEXT)''')
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
    branch = request.form.get('branch')
    category = request.form.get('category')

    conn = sqlite3.connect('maithri_fest.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (name, pin, mobile, branch, category))
    conn.commit()
    conn.close()

    # We pass these variables back so the "Download" button appears
    return render_template('index.html', success=True, name=name, pin=pin, category=category)

@app.route('/download_ticket/<name>/<pin>/<category>')
def download_ticket(name, pin, category):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A6)
    width, height = A6
    
    # Official Ticket Design
    p.setFillColorRGB(0.05, 0.1, 0.25)
    p.rect(0, 0, width, height, fill=1)
    
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height-20*mm, "MAITHRI FEST 2026")
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, height-28*mm, "Official Entry Pass")
    p.drawCentredString(width/2, height-33*mm, "Dates: May 8 - 9, 2026")
    
    p.setStrokeColorRGB(1, 1, 1)
    p.line(10*mm, height-38*mm, width-10*mm, height-38*mm)
    
    p.setFont("Helvetica-Bold", 11)
    p.drawString(15*mm, height-55*mm, f"NAME: {name.upper()}")
    p.drawString(15*mm, height-65*mm, f"ID/PIN: {pin}")
    p.drawString(15*mm, height-75*mm, f"TYPE: {category.upper()}")
    
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width/2, 15*mm, "Please carry a valid ID along with this pass.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Maithri_Pass_{pin}.pdf")

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('maithri_fest.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    students = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', students=students)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
