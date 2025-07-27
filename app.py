from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def can_upload():
    return True  # Disable limit for testing

@app.route('/')
def index():
    return render_template('index.html', free_used=False)

@app.route('/setadmin')
def setadmin():
    session['is_admin'] = True
    flash("Admin mode enabled.")
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    yt_url = request.form.get('youtube_url')
    if yt_url:
        flash("⚠️ YouTube download temporarily disabled due to site restrictions.")
        return redirect(url_for('index'))

    if 'audio_file' in request.files:
        file = request.files['audio_file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
            file.save(filepath)
            return send_file(filepath, as_attachment=True)

    flash("No file provided.")
    return redirect(url_for('index'))

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')
