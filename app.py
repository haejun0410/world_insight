from flask import Flask, render_template, request, session, jsonify, redirect, url_for
import pymysql
import hashlib
from setting import Config
from genNews import GenerateNews
from datetime import datetime, timedelta

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

# 메인 페이지
@app.route('/')
def home():
    error = None
    return render_template('home.html', error=error)

# 게시판
@app.route('/opinion_board')
def opinion_board():
    error = None
    return render_template("opinion_board.html", error = error)

# 지도 화면
@app.route('/maps')
def maps():
    GenerateNews.generate_news()
    error = None
    return render_template("maps.html", error = error, google_maps_api_key = app.config['GOOGLE_MAPS_API_KEY'])

# 로그인 창
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
                    print("Login Success")
                    session['login_user'] = id
                    print(session)
                    return redirect(url_for('home'))
                else:
                    error = "INVALID"
        finally:
            connection.close()

    return render_template('login.html', error=error)

# 로그아웃 기능
@app.route('/logout')
def logout():
    session.pop('login_user', None)
    return redirect(url_for('home'))

# 회원 가입 창
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

        return redirect(url_for('login'))
    return render_template('register.html', error=error)

# 게시글 작성 창
@app.route('/post_write', methods = ['GET', 'POST'])
def post_write():
    error = None
    if request.method == 'POST':
        title = request.form['Title']
        Content = request.form['Content']
        writter = session['login_user']
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO posts (title, writter, contents) VALUES(%s, %s, %s)"
                cursor.execute(sql,(title, writter, Content))
                connection.commit()
        finally:
            connection.close()
        return redirect(url_for('opinion_board'))
    return render_template('write_post.html',error = error)

# 게시물 불러오는 기능
@app.route('/get_posts')
def get_posts():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                    SELECT DATE_FORMAT(posts.created_at, '%Y/%m/%d/%H:%i') AS created_at, title, views, nickname, _id
                    FROM posts 
                    JOIN users ON posts.writter = users.id
                    ORDER BY _id;
                """
            cursor.execute(sql)
            posts = cursor.fetchall()
            return jsonify(posts)
    except Exception as e:
        print("Error fecthing posts: ", e)
        return jsonify([])
    finally:
        connection.close()

# 게시글 보여주는 창
@app.route('/post/<int:post_id>')
def show_post(post_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            if 'viewed_posts' not in session :
                session['viewed_posts'] = {}
            if post_id not in session['viewed_posts'] or (datetime.now() - session['viewed_posts'][post_id] >= timedelta(minutes=1)):
                session['viewed_posts'][post_id] = datetime.now()
                update_sql = "UPDATE posts SET views = views + 1 WHERE _id = %s"
                cursor.execute(update_sql, (post_id, ))
                connection.commit()

            # 게시물 정보 
            post_sql = """
                SELECT * 
                FROM posts
                JOIN users ON posts.writter = users.id
                WHERE posts._id = %s;
            """
            cursor.execute(post_sql, (post_id,))
            post = cursor.fetchone()

            # 게시물에 대한 댓글 
            comments_sql = """
                SELECT DATE_FORMAT(comments.created_at, '%%Y-%%m-%%d %%H:%%i') AS created_at, 
                        users.nickname AS nickname, 
                        comments.content AS content,
                        comments._id
                        FROM comments
                        JOIN users ON comments.user_id = users.id
                        WHERE comments.post_id = %s
                        ORDER BY comments._id
                    """
            cursor.execute(comments_sql, (post_id,))
            comments = cursor.fetchall()
            return render_template('post_contents.html', post=post, comments=comments)
    except Exception as e:
        print("FAILED")
    finally:
        connection.close()

# 게시글 수정 창
@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    error = None
    if 'login_user' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if request.method == 'POST':
                title = request.form['Title']
                content = request.form['Content']

                update_sql = "UPDATE posts SET title = %s, contents = %s WHERE _id = %s AND writter = %s"
                cursor.execute(update_sql, (title, content, post_id, session['login_user']))
                connection.commit()
                return redirect(url_for('opinion_board'))

            else:
                # Fetch existing post data
                post_sql = "SELECT title, contents FROM posts WHERE _id = %s AND writter = %s"
                cursor.execute(post_sql, (post_id, session['login_user']))
                post = cursor.fetchone()
                if not post:
                    return "Unauthorized to edit this post"

                return render_template('edit_post.html', post=post, error=error)
    except Exception as e:
        print("Error editing post:", e)
        error = "Error editing post."
    finally:
        connection.close()

    return render_template('edit_post.html', error=error)

# 댓글 추가하는 기능
@app.route("/add_comment", methods = ["POST"])
def add_comment():
    try:
        data = request.json
        post_id = data['postId']
        content = data['content']
        user_id = session['login_user']
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO comments (post_id, user_id, content) VALUES(%s, %s, %s)"
            cursor.execute(sql,(post_id, user_id, content))
            connection.commit()
    finally:
        connection.close()
    return redirect(url_for('show_post', post_id=post_id))

# 댓글 불러오는 기능(id 체크)
@app.route('/get_comments/<int:post_id>')
def get_comment(post_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                SELECT DATE_FORMAT(comments.created_at, '%%Y-%%m-%%d %%H:%%i') AS created_at, comments._id, users.nickname AS nickname, comments.content AS content
                FROM comments
                JOIN users ON comments.user_id = users.id
                WHERE comments.post_id = %s
                ORDER BY comments._id;
            """
            cursor.execute(sql, (post_id,))
            comments = cursor.fetchall()
            return jsonify(comments)
    except Exception as e:
        print("Error fetching comments: ", e)
        return jsonify([])
    finally:
        connection.close()

# 아이디 중복 체크 기능
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

# 닉네임 중복 확인
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

# 로그인 상태 확인
@app.route('/check_login')
def check_login():
    if 'login_user' in session:
        return jsonify({"logged_in": True})
    else:
        return jsonify({"logged_in": False})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
