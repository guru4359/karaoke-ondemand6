from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
import subprocess

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def can_upload():
    if session.get('is_admin'):
        return True
    last_upload = session.get('last_upload')
    if not last_upload:
        return True
    last_time = datetime.strptime(last_upload, '%Y-%m-%d')
    return (datetime.now() - last_time).days >= 7

@app.route('/')
def index():
    return render_template('index.html', free_used=not can_upload())

@app.route('/setadmin')
def setadmin():
    session['is_admin'] = True
    flash("Admin mode enabled.")
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if not can_upload():
        flash("Free weekly song limit reached. Please subscribe or wait a week.")
        return redirect(url_for('index'))

    session['last_upload'] = datetime.now().strftime('%Y-%m-%d')

    yt_url = request.form.get('youtube_url')
    if yt_url:
        filename = f"{uuid.uuid4()}.m4a"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            result = subprocess.run(['yt-dlp', '-f', 'bestaudio[ext=m4a]', '-o', filepath, yt_url],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                flash(f"YouTube download failed: {result.stderr}")
                return redirect(url_for('index'))
            return send_file(filepath, as_attachment=True)
        except Exception as e:
            flash(f"Failed to process YouTube link: {str(e)}")
            return redirect(url_for('index'))

    if 'audio_file' in request.files:
        file = request.files['audio_file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
            file.save(filepath)
            return send_file(filepath, as_attachment=True)

    flash("No file or link provided.")
    return redirect(url_for('index'))

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')
