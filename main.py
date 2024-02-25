import sqlite3
from flask import Flask, request, redirect, url_for, flash, render_template, session, abort, g, make_response, \
    send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from fdb import FDatabase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from userlogin import UserLogin
from time import sleep
from uuid import uuid4


app = Flask(__name__)
app.secret_key = 'sdfvddfvwvwvwr'
MAX_CONTENT_LENGTH = 1024 * 1024

UPLOAD_FOLDER_IMG = 'uploads/image'
UPLOAD_FOLDER_MUS = 'uploads/audio'
UPLOAD_FOLDER_POST = 'posts/image'

app.config['UPLOAD_FOLDER_IMG'] = UPLOAD_FOLDER_IMG
app.config['UPLOAD_FOLDER_MUS'] = UPLOAD_FOLDER_MUS
app.config['UPLOAD_FOLDER_POST'] = UPLOAD_FOLDER_POST
app.config['DATABASE'] = 'database.db'


DATAB = 'db.db'
DEBUG = True
app.config.update(dict(DATAB=os.path.join(app.root_path, 'db.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для просмотра данных акаунтов нужно авторизоваться'
login_manager.login_message_category = 'error'


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


def connect():
    conn = sqlite3.connect(app.config['DATAB'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect()
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text text NOT NULL,
        bigtext text NOT NULL,
        photo_post TEXT NOT NULL
        )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name text NOT NULL,
        email text NOT NULL,
        login text NOT NULL,
        password text NOT NULL,
        avatar BLOB DEFAULT NULL,
        header BLOB DEFAULT NULL
        )""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users_card (
        login text NOT NULL,
        photo_path TEXT NOT NULL, 
        music_path TEXT NOT NULL, 
        text_beat TEXT NOT NULL
    )""")

    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDatabase(db)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['image_file']
        mus = request.files['audio_file']
        text = request.form['text']
        print(text)
        if file and mus and text and current_user.verifyExt(file.filename) and current_user.verifyExt(mus.filename):
            try:
                photo_filename = str(uuid4()) + f".{file.filename.rsplit('.', 1)[1]}"
                audio_filename = str(uuid4()) + f".{mus.filename.rsplit('.', 1)[1]}"

                file.save(os.path.join(app.config['UPLOAD_FOLDER_IMG'], photo_filename))
                mus.save(os.path.join(app.config['UPLOAD_FOLDER_MUS'], audio_filename))

                res = dbase.addCardBeat(current_user.getLogin(),
                                        photo_filename,
                                        audio_filename,
                                        text)
                if res:
                    flash("Музыка добавлена успешно", category='success')
            except Exception as ex:
                print(ex)
        else:
            flash("Ошибка обновления аватара", category='error')
    return render_template('create.html')


@app.route('/uploads/photo/<path:filename>')
def uploaded_photo(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_IMG'], filename)


@app.route('/uploads/audio/<path:filename>')
def uploaded_audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_MUS'], filename)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        user = dbase.getUserByLogin(request.form['login'])
        if user and check_password_hash(user['password'], request.form['psw']):
            tm = True if request.form.get('checkbox') else False
            userlogin = UserLogin().create(user)
            login_user(userlogin, remember=tm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash("Неверная пара логин/пароль", category='error')

    return render_template('form.html')


@app.route("/add_post", methods=['POST', 'GET'])
def add_post():
    k = None
    if request.method == 'POST':
        file = request.files['image_file']
        if len(request.form['text']) > 4 and len(request.form['bigtext']) > 10 and current_user.verifyExt(file.filename):
            photo_filename = str(uuid4()) + f".{file.filename.rsplit('.', 1)[1]}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER_POST'], photo_filename))

            res = dbase.addPost(request.form['text'], request.form['bigtext'], photo_filename)
            if res:
                return redirect(url_for("show_post"))
            else:
                flash("Ошибка добавления статьи", category='error')
        else:
            flash("Ошибка добавления статьи", category='error')

    return render_template('form_site.html')


@app.route('/posts/photo/<path:filename>')
def posts_photo(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_POST'], filename)


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('error.html')


@app.route("/")
@app.route("/home")
# @login_required
def show_post():
    posts = dbase.getPost()
    print(posts)

    return render_template('post.html', posts=posts)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        if len(request.form['email']) > 5 and request.form['psw'] == request.form['psw-repeat']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], request.form['login'], hash)
            if res == 400:
                flash("Данная почта уже используется", category='error')
            if res == 401:
                flash("Имя пользователя уже занято", category='error')
            else:
                user = dbase.getUserByLogin(request.form['login'])
                if user and check_password_hash(user['password'], request.form['psw']):
                    tm = True if request.form.get('checkbox') else False
                    userlogin = UserLogin().create(user)
                    login_user(userlogin, remember=tm)
                    sleep(1)
                    return redirect(url_for('profile'))
                else:
                    flash("Ошибка при получении данных", category='error')
        else:
            flash("Данные не соответствуют", category='error')

    return render_template('register.html')


@app.route('/register_update', methods=['POST', 'GET'])
def register_update():

    if request.method == 'POST':
        new_name = request.form['name_update'] if request.form.get('name_update') else current_user.getName()
        new_email = request.form['email_update'] if request.form.get('email_update') else current_user.getEmail()
        new_login = request.form['login_update'] if request.form.get('login_update') else current_user.getLogin()

        try:
            res = dbase.updateUser(current_user.get_id(), new_name, new_email, new_login)
            if res == 400:
                flash("Данная почта уже используется", category='error')
                return render_template('change_profile.html')
            if res == 401:
                flash("Имя пользователя уже занято", category='error')
                return render_template('change_profile.html')

            return redirect(url_for('profile'))
        except Exception as e:
            flash("Произошла ошибка при обновлении данных пользователя", category='error')
            print(e)

    return render_template('change_profile.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли с аккаунта', category='error')
    return redirect(url_for('login'))


@app.route("/profile")
@login_required
def profile():
    post = dbase.getCardBeat(current_user.getLogin())
    profile_url = url_for('profile', login=login)
    return render_template('profile.html', posts=post)


@app.route('/change_profile')
@login_required
def change_profile():
    return render_template('change_profile.html',
                           get_name=current_user.getName(),
                           get_email=current_user.getEmail(),
                           get_login=current_user.getLogin())



@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/jpg'
    return h


@app.route('/header')
@login_required
def header():
    img = current_user.getHeader(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/jpg'
    return h


@app.route('/upload_avatar', methods=['POST', 'GET'])
@login_required
def upload_avatar():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id(), 'avatar')

                if res:
                    flash("Аватар был успешно обновлен", category='success')
                else:
                    flash("Произошла ошибка", category='error')
            except Exception as ex:
                print(ex)
        else:
            flash("Ошибка обновления аватара", category='error')

    return redirect(url_for('change_profile'))


@app.route('/upload_header', methods=['POST', 'GET'])
@login_required
def upload_header():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id(), 'header')

                if res:
                    flash("Аватар был успешно обновлен", category='success')
                else:
                    flash("Произошла ошибка", category='error')
            except Exception as ex:
                print(ex)
        else:
            flash("Ошибка обновления аватара", category='error')

    return redirect(url_for('change_profile'))


@app.route('/upload_profile', methods=['POST', 'GET'])
@login_required
def upload_profile():
    return redirect(url_for('profile'))


if __name__ == "__main__":
    app.run(debug=True)
