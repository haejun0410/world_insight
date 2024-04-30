from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from flaskext.mysql import MySQL
import hashlib

mysql = MySQL()
app = Flask(__name__)

app.config.from_object(config['default'])
mysql.init_app(app)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    error = None
    return render_template('home.html',error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        id = request.form['id']
        password = request.form['pw']
        hashed_pw = hash_password(password)

        conn = mysql.connect()
        cursor = conn.cursor()

        sql = "SELECT id FROM users WHERE id = %s AND password = %s"
        value = (id, hashed_pw)
        cursor.execute(sql, value)

        data = cursor.fetchone()
        cursor.close()
        conn.close()

        if data : 
            session['login_user'] = id
            return redirect(url_for('home'))
        else:
            error = "INVALID"
    return render_template('login.html', methods = ['GET', 'POST'])

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

        conn = mysql.connect()
        cursor = conn.cursor()

        sql = "INSERT INTO users (id, password, name, nickname, phone_number) VALUES (%s, %s, %s, %s, %s)"
        value = (id, hashed_pw, name, nickname, phone_number)
        cursor.execute(sql, value)

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('home'))
    return render_template('register.html', error=error)

@app.route('/check_id_duplicate', methods=['POST'])
def check_id_duplicate():
    try:
        id = request.form.get('register_id')

        if not id:
            return jsonify({"id_exists": False})

        conn = mysql.connect()
        cursor = conn.cursor()

        sql_id = "SELECT id FROM users WHERE id = %s"
        cursor.execute(sql_id, (id,))
        id_data = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({"id_exists": id_data is not None})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_nickname_duplicate', methods=['POST'])
def check_nickname_duplicate():
    try:
        nickname = request.form.get('register_nickname')

        if not nickname:
            return jsonify({"nickname_exists": False})

        conn = mysql.connect()
        cursor = conn.cursor()

        sql_nickname = "SELECT nickname FROM users WHERE nickname = %s"
        cursor.execute(sql_nickname, (nickname,))
        nickname_data = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({"nickname_exists": nickname_data is not None})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)