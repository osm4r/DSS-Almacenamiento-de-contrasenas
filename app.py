from flask import Flask, request, redirect, url_for, render_template
from argon2 import PasswordHasher


app = Flask(__name__)
ph = PasswordHasher(hash_len=32, salt_len=16, time_cost=2, memory_cost=102400)


# Funciones de hashing y salado
def generate_salt():
    return os.urandom(16)


def hash_password(password, salt):
    pepper = b'MySuperSecretPepper'
    password_peppered = password.encode() + pepper
    return ph.hash(password_peppered, salt)


# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        salt = generate_salt()
        password_hash = hash_password(password, salt)
        db.execute('INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)', 
                   username, password_hash, salt)
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and ph.verify(user['password_hash'], password.encode() + b'MySuperSecretPepper'):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect username or password')
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        return render_template('dashboard.html', username=user['username'])
    return redirect(url_for('login'))


# Configuración de la base de datos
import os
import sqlite3


db = sqlite3.connect('password.db')
db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, salt TEXT)')
db.commit()


if __name__ == '__main__':
    app.secret_key = os.urandom(16)
    app.run(debug=True)