import os
import random
import string
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_id():
    return ''.join(random.choices(string.digits, k=10))

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({"message": "No files part"}), 400

    files = request.files.getlist('files')
    farmer_name = request.form['farmer_name']

    unique_id = generate_unique_id()
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)
    os.makedirs(folder_path, exist_ok=True)

    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{farmer_name}_{unique_id}_{file.filename}")
            file_path = os.path.join(folder_path, filename)
            file.save(file_path)
            uploaded_files.append(filename)

    return jsonify({
        "message": "Files uploaded successfully",
        "unique_id": unique_id,
        "uploaded_files": uploaded_files
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
