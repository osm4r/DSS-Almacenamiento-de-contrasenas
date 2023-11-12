from flask import Flask, request, redirect, url_for, render_template, session, flash
from argon2 import PasswordHasher
from datetime import datetime, timedelta

app = Flask(__name__)
ph = PasswordHasher(hash_len=32, salt_len=16, time_cost=2, memory_cost=102400)


# Funciones de hashing y salado
def generate_salt():
    return os.urandom(16)


def hash_password(password, salt):
    pepper = b'MySuperSecretPepper'
    password_peppered = password.encode() + pepper
    # print("pswd peppered: ", password_peppered)
    # print("salt: ", salt)
    # password_hashed = ph.hash(password_peppered, salt=salt)
    # print("password_hashed: ", password_hashed)
    return ph.hash(password_peppered, salt=salt)


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
                   (username, password_hash, salt))
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        # print(user)

        # Obtener o inicializar el contador de intentos de inicio de sesión fallidos en la sesión
        login_attempts = session.get('login_attempts', 0)
        # password_verified = user and ph.verify(user[2], password.encode() + b'MySuperSecretPepper')

        try:
            if user and ph.verify(user[2], password.encode() + b'MySuperSecretPepper'):
                session['user_id'] = user[0]
                # Restablecer el contador de intentos de inicio de sesión fallidos en caso de éxito
                session['login_attempts'] = 0
                return redirect(url_for('dashboard'))
        except Exception as e:
            # Incrementar el contador de intentos de inicio de sesión fallidos
            session['login_attempts'] = login_attempts + 1

            # Verificar si se ha alcanzado el límite de intentos
            if login_attempts >= 3:  # Puedes ajustar este límite según tus necesidades
                # Bloquear la cuenta durante 5 minutos (300 segundos)
                session['account_locked_until'] = datetime.utcnow() + timedelta(seconds=300)
                flash('Too many login attempts. Your account is locked for 5 minutes.')
                return redirect(url_for('index'))

            flash('Incorrect username or password')

            # Verificar si la cuenta está bloqueada temporalmente
            account_locked_until = session.get('account_locked_until')
            if account_locked_until and datetime.utcnow() < account_locked_until:
                flash(f'Your account is locked. Please try again after {int((account_locked_until - datetime.utcnow()).total_seconds())} seconds.')
                return redirect(url_for('index'))
                
            # Manejar cualquier excepción, por ejemplo, si hay un problema al verificar la contraseña
            flash('An error occurred while processing your request.')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        return render_template('dashboard.html', username=user[1])
    return redirect(url_for('login'))


# Configuración de la base de datos
import os
import sqlite3

app.secret_key = os.urandom(16)

db = sqlite3.connect('password.db', check_same_thread=False)
db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, salt TEXT)')
db.commit()


if __name__ == '__main__':
    # app.secret_key = os.urandom(16)
    app.run(debug=True)