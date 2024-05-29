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

@app.route('/mypage', methods=['GET', 'POST'])
def mypage():
    if 'login_user' not in session:
        return redirect(url_for('login'))
    
    error = None
    user_info = None

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (session['login_user'],))
            user_info = cursor.fetchone()
    finally:
        connection.close()
    
    return render_template('mypage.html', error=error, user_info=user_info)

@app.route('/update_nickname', methods=['POST'])
def update_nickname():
    if 'login_user' not in session:
        return redirect(url_for('login'))
    
    new_nickname = request.form['new_nickname']
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET nickname = %s WHERE id = %s"
            cursor.execute(sql, (new_nickname, session['login_user']))
            connection.commit()
    finally:
        connection.close()
    
    return redirect(url_for('mypage'))

@app.route('/update_password', methods=['POST'])
def update_password():
    if 'login_user' not in session:
        return redirect(url_for('login'))

    current_password = request.form['current_password']
    new_password = request.form['new_password']
    hashed_current_password = hash_password(current_password)
    hashed_new_password = hash_password(new_password)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 현재 비밀번호 확인
            sql = "SELECT * FROM users WHERE id = %s AND password = %s"
            cursor.execute(sql, (session['login_user'], hashed_current_password))
            user = cursor.fetchone()
            if user:
                # 새로운 비밀번호로 업데이트
                sql = "UPDATE users SET password = %s WHERE id = %s"
                cursor.execute(sql, (hashed_new_password, session['login_user']))
                connection.commit()
                return redirect(url_for('mypage',  user_info = user, message="Password updated successfully"))
            else:
                # 현재 비밀번호가 일치하지 않는 경우
                return render_template('mypage.html', user_info = user, error="Current password is incorrect")
    except Exception as e:
        # 데이터베이스 오류 처리
        print(f"Error: {e}")
        return render_template('mypage.html', user_info = user, error="An error occurred while updating the password")
    finally:
        connection.close()



@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'login_user' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 사용자 게시글 삭제
            sql_delete_posts = "DELETE FROM posts WHERE writter = %s"
            cursor.execute(sql_delete_posts, (session['login_user'])) 
            connection.commit()
            # 사용자 정보 삭제
            sql_delete_user = "DELETE FROM users WHERE id = %s"
            cursor.execute(sql_delete_user, (session['login_user']))  
            connection.commit()
    except Exception as e:
        print("에러 발생:", e)  
    finally:
        connection.close()
    
    session.pop('login_user', None)
    return redirect(url_for('home'))

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
                    ORDER BY _id DESC;
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
        print("FAILED {}".format(e))
        return "error {}".format(e)
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

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    error = None
    connection = get_db_connection()
    with connection.cursor() as cursor:
        delete_sql = "delete from posts where _id = %s"
        cursor.execute(delete_sql, (post_id,))
        connection.commit()
        return redirect(url_for('opinion_board'))
    
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

@app.route('/get_us_canada')
def get_us_canada():
    error = None
    return render_template('us-canada.html', error=error)

@app.route('/get_asia')
def get_asia():
    error = None
    return render_template('asia.html', error=error)

@app.route('/get_eu')
def get_eu():
    error = None
    return render_template('europe.html', error=error)

@app.route('/get_uk')
def get_uk():
    error = None
    return render_template('uk.html', error=error)

@app.route('/get_africa')
def get_africa():
    error = None
    return render_template('africa.html', error=error)

@app.route('/get_aust')
def get_aust():
    error = None
    return render_template('australia.html', error=error)

@app.route('/get_latin')
def get_latin():
    error = None
    return render_template('latin_america.html', error=error)

@app.route('/get_middle_east')
def get_middle_east():
    error = None
    return render_template('middle_east.html', error=error)

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
    nickname = request.form.get('register_nickname') or request.form.get('new_nickname')
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
