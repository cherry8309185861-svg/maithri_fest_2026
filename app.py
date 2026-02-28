import os
import sqlite3
import io
import qrcode
from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('maithri_fest.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (name TEXT, val TEXT, info TEXT, category TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    category = request.form.get('category')
    name = request.form.get('name')
    val = request.form.get('pin') if category == 'student' else request.form.get('mobile')
    info = request.form.get('branch') if category == 'student' else request.form.get('job_info')

    conn = sqlite3.connect('maithri_fest.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (name, val, info, category))
    conn.commit()
    conn.close()

    return render_template('index.html', success=True, name=name, val=val, info=info, category=category)

@app.route('/download_ticket/<name>/<val>/<info>/<category>')
def download_ticket(name, val, info, category):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A6)
    width, height = A6
    
    p.setFillColorRGB(0.8, 0.2, 0.1)
    p.rect(0, 0, width, height, fill=1)
    p.setFillColorRGB(1, 1, 1)
    
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, height-15*mm, "MAITHRI FEST 2026")
    p.setFont("Helvetica", 9)
    p.drawCentredString(width/2, height-21*mm, "MARCH 06 & 07")

    p.setFont("Helvetica-Bold", 11)
    msg = "Welcome to the Mythri Fest, Sir!" if category == 'vip' else "Welcome & Enjoy the Fest!"
    p.drawCentredString(width/2, height-35*mm, msg)

    p.setFont("Helvetica", 11)
    p.drawString(15*mm, height-55*mm, f"NAME: {name.upper()}")
    p.drawString(15*mm, height-63*mm, f"ID/MOB: {val}")
    p.drawString(15*mm, height-71*mm, f"INFO: {info.upper()}")

    # Stable QR Generation
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(f"MAITHRI2026-{category}-{val}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_buffer = io.BytesIO()
    img.save(qr_buffer)
    qr_buffer.seek(0)
    p.drawInlineImage(qr_buffer, width/2-22*mm, 10*mm, width=45*mm, height=45*mm)

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Pass_{val}.pdf", mimetype='application/pdf')

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
