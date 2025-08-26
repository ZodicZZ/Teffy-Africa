from flask import Flask, render_template, redirect, request, session, url_for, jsonify, make_response
import firebase_admin
from firebase_admin import credentials, auth, db, storage
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = '1111'
@app.route('/')
def home():
    return render_template('Farmer-Dash-Transaction-Validation.html')
if __name__ == '__main__':
    app.run(debug=True)
