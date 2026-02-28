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
                      (name TEXT, pin_or_mobile TEXT, branch_or_job TEXT, category TEXT)''')
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
    
    if category == 'student':
        val = request.form.get('pin')
        info = request.form.get('branch')
    else:
        val = request.form.get('mobile')
        info = request.form.get('job_info')

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
    
    # Background Design (Sunset Red)
    p.setFillColorRGB(0.8, 0.2, 0.1)
    p.rect(0, 0, width, height, fill=1)
    p.setFillColorRGB(1, 1, 1)
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height-15*mm, "MAITHRI FEST 2026")
    p.setFont("Helvetica", 8)
    p.drawCentredString(width/2, height-20*mm, "MARCH 06 & 07")

    # Message based on category
    p.setFont("Helvetica-Bold", 10)
    if category == 'vip':
        msg = f"Welcome to the Maithri Fest, Sir!"
    else:
        msg = f"Welcome to Maithri Fest and Enjoy the Fest!"
    p.drawCentredString(width/2, height-30*mm, msg)

    # Details
    p.setFont("Helvetica", 10)
    p.drawString(15*mm, height-45*mm, f"NAME: {name.upper()}")
    p.drawString(15*mm, height-52*mm, f"ID/MOB: {val}")
    p.drawString(15*mm, height-59*mm, f"INFO: {info.upper()}")

    # QR Code Generation
    qr_data = f"Maithri2026|{category}|{name}|{val}"
    qr = qrcode.make(qr_data)
    qr_img_buffer = io.BytesIO()
    qr.save(qr_img_buffer, format='PNG')
    qr_img_buffer.seek(0)
    
    p.drawInlineImage(qr_img_buffer, width/2-20*mm, 15*mm, width=40*mm, height=40*mm)

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Pass_{name}.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
