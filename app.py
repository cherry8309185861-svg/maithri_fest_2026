import os
import sqlite3
import io
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
    info = request.form.get('job_info') if category == 'vip' else request.form.get('branch')

    # STRICT VIP JOB VALIDATION
    if category == 'vip':
        # List of high-end/respectful keywords
        respectful_jobs = [
            'police', 'doctor', 'engineer', 'politician', 'hero', 'actor', 
            'collector', 'dsp', 'si', 'judge', 'advocate', 'professor', 
            'minister', 'ceo', 'manager', 'scientist', 'ias', 'ips'
        ]
        
        # Check if the entered job contains any of the respectful keywords
        is_valid_vip = any(job in info.lower() for job in respectful_jobs)
        
        if not is_valid_vip:
            error_msg = "Sorry, registration unsuccessful. Go to Student Registration and try!"
            return render_template('index.html', error=error_msg)

    # If valid, save to database
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
    
    # Pass Design
    p.setFillColorRGB(0.8, 0.2, 0.1)
    p.rect(0, 0, width, height, fill=1)
    p.setFillColorRGB(1, 1, 1)
    
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, height-15*mm, "MAITHRI FEST 2026")
    
    p.setFont("Helvetica-Bold", 11)
    msg = "Welcome to the Mythri Fest, Sir!" if category == 'vip' else "Welcome & Enjoy the Fest!"
    p.drawCentredString(width/2, height-30*mm, msg)

    p.setFont("Helvetica", 11)
    p.drawString(15*mm, height-55*mm, f"NAME: {name.upper()}")
    p.drawString(15*mm, height-63*mm, f"ID/MOB: {val}")
    p.drawString(15*mm, height-71*mm, f"JOB/BRANCH: {info.upper()}")

    # Fail-safe QR API
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=MAITHRI26-{val}"
    p.drawInlineImage(qr_url, width/2-20*mm, 15*mm, width=40*mm, height=40*mm)

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Pass_{val}.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
