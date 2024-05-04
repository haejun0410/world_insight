from flask import Flask, render_template, request, session, jsonify, redirect, url_for
import pymysql
from setting import Config
import hashlib

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    error = None
    return render_template('home.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        id = request.form['id']
        password = request.form['pw']
        hashed_pw = hash_password(password)

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT id FROM users WHERE id = %s AND password = %s"
                cursor.execute(sql, (id, hashed_pw))
                data = cursor.fetchone()
                if data:
                    session['login_user'] = id
                    return redirect(url_for('home'))
                else:
                    error = "INVALID"
        finally:
            connection.close()

    return render_template('login.html', error=error)

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        id = request.form['register_id']
        password = request.form['register_pw']
        name = request.form['register_name']
        nickname = request.form['register_nickname']
        phone_number = request.form['register_phone_number']
        hashed_pw = hash_password(password)

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO users (id, password, name, nickname, phone_number) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (id, hashed_pw, name, nickname, phone_number))
                connection.commit()
        finally:
            connection.close()

        return redirect(url_for('home'))
    return render_template('register.html', error=error)

@app.route('/check_id_duplicate', methods=['POST'])
def check_id_duplicate():
    id = request.form.get('register_id')
    if not id:
        return jsonify({"id_exists": False})

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id FROM users WHERE id = %s"
            cursor.execute(sql, (id,))
            id_data = cursor.fetchone()
            return jsonify({"id_exists": id_data is not None})
    finally:
        connection.close()

@app.route('/check_nickname_duplicate', methods=['POST'])
def check_nickname_duplicate():
    nickname = request.form.get('register_nickname')
    if not nickname:
        return jsonify({"nickname_exists": False})

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT nickname FROM users WHERE nickname = %s"
            cursor.execute(sql, (nickname,))
            nickname_data = cursor.fetchone()
            return jsonify({"nickname_exists": nickname_data is not None})
    finally:
        connection.close()

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
