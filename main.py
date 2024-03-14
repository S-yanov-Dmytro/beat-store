import sqlite3
from flask import Flask, request, redirect, url_for, flash, render_template, session, abort, g, make_response, \
    send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
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

UPLOAD_FOLDER_USER_AVA = 'uploads/user_avatar'
UPLOAD_FOLDER_USER_HEADER = 'uploads/user_header'

app.config['UPLOAD_FOLDER_IMG'] = UPLOAD_FOLDER_IMG
app.config['UPLOAD_FOLDER_MUS'] = UPLOAD_FOLDER_MUS
app.config['UPLOAD_FOLDER_POST'] = UPLOAD_FOLDER_POST

app.config['UPLOAD_FOLDER_USER_AVA'] = UPLOAD_FOLDER_USER_AVA
app.config['UPLOAD_FOLDER_USER_HEADER'] = UPLOAD_FOLDER_USER_HEADER

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
        login TEXT,
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
        avatar text DEFAULT NULL,
        header text DEFAULT NULL,
        instagram text DEFAULT NULL,
        telegram text DEFAULT NULL,
        facebook text DEFAULT NULL,
        tik_tok text DEFAULT NULL,
        vk DEFAULT NULL,
        youtube DEFAULT NULL
        )""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users_card (
        login text NOT NULL,
        photo_path TEXT NOT NULL, 
        music_path TEXT NOT NULL, 
        text_beat TEXT NOT NULL,
        genre TEXT NOT NULL,
        bpm INTEGER NOT NULL,
        energy INTEGER NOT NULL,
        joy INTEGER NOT NULL,
        mood INTEGER NOT NULL,
        tags TEXT NOT NULL
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
    return render_template(['about.html', 'base.html'], current_user=current_user)


@app.route('/create', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['image_file']
        mus = request.files['audio_file']
        text = request.form['text']
        genre = request.form['genre']
        bpm = request.form['bpm']
        energy = request.form['energy']
        joy = request.form['joy']
        mood = request.form['mood']
        tags = request.form['tags']
        if (file and mus and text and genre and bpm and tags and
                current_user.verifyExt(file.filename) and
                current_user.verifyExt(mus.filename)):
            try:
                photo_filename = str(uuid4()) + f".{file.filename.rsplit('.', 1)[1]}"
                audio_filename = str(uuid4()) + f".{mus.filename.rsplit('.', 1)[1]}"

                file.save(os.path.join(app.config['UPLOAD_FOLDER_IMG'], photo_filename))
                mus.save(os.path.join(app.config['UPLOAD_FOLDER_MUS'], audio_filename))

                res = dbase.addCardBeat(current_user.getLogin(),
                                        photo_filename,
                                        audio_filename,
                                        text, genre,
                                        bpm, energy,
                                        joy, mood, tags)
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
        return redirect(url_for('profile', username=current_user.getLogin()))

    if request.method == "POST":
        user = dbase.getUserByLogin(request.form['login'])
        if user and check_password_hash(user['password'], request.form['psw']):
            tm = True if request.form.get('checkbox') else False
            userlogin = UserLogin().create(user)
            login_user(userlogin, remember=tm)
            return redirect(request.args.get('next') or url_for('profile', username=user['login']))

        flash("Неверная пара логин/пароль", category='error')

    return render_template('form.html')


@app.route("/add_post/<username>", methods=['POST', 'GET'])
def add_post(username):
    k = None
    if request.method == 'POST':
        file = request.files['image_file']
        if len(request.form['text']) > 4 and len(request.form['bigtext']) > 10 and current_user.verifyExt(file.filename):
            photo_filename = str(uuid4()) + f".{file.filename.rsplit('.', 1)[1]}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER_POST'], photo_filename))

            res = dbase.addPost(username, request.form['text'], request.form['bigtext'], photo_filename)
            if res:
                return redirect(url_for("show_post", username=username))
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


@app.route("/posts_profile/<username>")
# @login_required
def show_post(username):
    posts = dbase.getPost(username)
    users = dbase.getUserByLogin(username)
    instagram = users['instagram']
    telegram = users['telegram']
    facebook = users['facebook']
    tik_tok = users['tik_tok']
    vk = users['vk']
    youtube = users['youtube']
    print((instagram, telegram, facebook, tik_tok, vk, youtube))
    print(posts)

    return render_template('posts_profile.html',
                           name=users['name'],
                           posts=posts,
                           avatar=users['avatar'],
                           header=users['header'],
                           username=username,
                           current_user=current_user,
                           instagram=instagram,
                           telegram=telegram,
                           facebook=facebook,
                           tik_tok=tik_tok,
                           vk=vk,
                           youtube=youtube)


@app.route("/home")
@app.route("/")
# @login_required
def main():
    data = dbase.getNameTagsBeat()
    data_user = dbase.getNewUsers()
    card = dbase.getCardBeatOnMainPageAll()

    card_genre_rock = dbase.getCardBeat(data='Rock', colum='genre')
    card_genre_pop = dbase.getCardBeat(data='Pop', colum='genre')
    return render_template(['post.html', 'base.html'], data=data, users=data_user,
                           card=card, current_user=current_user, genres_rock=card_genre_rock, genres_pop=card_genre_pop)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        instagram = request.form['instagram']
        telegram = request.form['telegram']
        facebook = request.form['facebook']
        tik_tok = request.form['tik_tok']
        youtube = request.form['youtube']
        vk = request.form['vk']
        if len(request.form['email']) > 5 and request.form['psw'] == request.form['psw-repeat']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], request.form['login'], hash,
                                instagram, telegram, facebook, tik_tok, youtube, vk)
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
                    return redirect(url_for('profile', username=request.form['login']))
                else:
                    flash("Ошибка при получении данных", category='error')
        else:
            flash("Данные не соответствуют", category='error')

    return render_template('register.html')


@app.route('/register_update/<username>', methods=['POST', 'GET'])
def register_update(username):
    users = dbase.getUserByLogin(username)
    try:

        if request.method == 'POST':
            new_name = request.form['name_update'] if request.form.get('name_update') else current_user.getName()
            new_email = request.form['email_update'] if request.form.get('email_update') else current_user.getEmail()
            new_login = request.form['login_update'] if request.form.get('login_update') else current_user.getLogin()

            new_instagram = request.form['instagram'] if request.form.get('instagram') else current_user.getInstagram()
            new_telegram = request.form['telegram'] if request.form.get('telegram') else current_user.getTelegram()
            new_facebook = request.form['facebook'] if request.form.get('facebook') else current_user.getFacebook()
            new_tik_tok = request.form['tik_tok'] if request.form.get('tik_tok') else current_user.getTikTok()
            new_vk = request.form['vk'] if request.form.get('vk') else current_user.getVK()
            new_youtube = request.form['youtube'] if request.form.get('youtube') else current_user.getYouTube()

            # try:
            res = dbase.updateUser(current_user.get_id(), new_name, new_email, new_login, new_instagram, new_telegram,
                                   new_facebook, new_tik_tok, new_vk, new_youtube)
            if res == 400:
                flash("Данная почта уже используется", category='error')
                return render_template('change_profile.html', avatar=users['avatar'], header=users['header'])
            if res == 401:
                flash("Имя пользователя уже занято", category='error')
                return render_template('change_profile.html', avatar=users['avatar'], header=users['header'])
        if request.form['login_update']:
            return redirect(url_for('profile', username=request.form['login_update']))
        else:
            return redirect(url_for('profile', username=username))

    except Exception as e:
        flash("Произошла ошибка при обновлении данных пользователя", category='error')
        print(e)

    return render_template('change_profile.html', avatar=users['avatar'], header=users['header'])


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли с аккаунта', category='error')
    return redirect(url_for('login'))


@app.route("/profile/<username>")
@login_required
def profile(username):
    # Получаем логин текущегоб пользователя
    # login = current_user.getLogin()
    # Получаем посты для профиля пользователя
    posts = dbase.getCardBeat(data=username, colum='login')
    user_data = dbase.getUserByLogin(username)
    print(user_data['login'])
    print(user_data['name'])
    print(user_data['id'])
    post_len = len(posts)

    instagram = user_data['instagram']
    telegram = user_data['telegram']
    facebook = user_data['facebook']
    tik_tok = user_data['tik_tok']
    vk = user_data['vk']
    youtube = user_data['youtube']
    print((instagram, telegram, facebook, tik_tok, vk, youtube))
    profile_url = url_for('profile', username=username)
    print(profile_url)
    return render_template(['profile.html','base.html'],
                           posts=posts,
                           post_len=post_len,
                           name=user_data['name'],
                           avatar=user_data['avatar'],
                           header=user_data['header'],
                           username=username,
                           current_user=current_user,
                           instagram=instagram, telegram=telegram,
                           facebook=facebook, tik_tok=tik_tok,
                           vk=vk, youtube=youtube)


@app.route('/change_profile/<username>')
@login_required
def change_profile(username):
    users = dbase.getUserByLogin(username)
    return render_template(['change_profile.html', 'base.html'],
                           get_name=current_user.getName(),
                           get_email=current_user.getEmail(),
                           get_login=current_user.getLogin(),
                           avatar=users['avatar'],
                           header=users['header'],
                           username=username,
                           current_user=current_user,
                           instagram=current_user.getInstagram(), telegram=current_user.getTelegram(),
                           facebook=current_user.getFacebook(), tik_tok=current_user.getTikTok(),
                           vk=current_user.getVK(), youtube=current_user.getYouTube())


def getAvatarByLogin(app, login):
    img = None
    user = dbase.getUserByLogin(login)
    if user:
        if not user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='img/default.jpg'),
                                       "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию: " + str(e))
        else:
            img = user['avatar']
    return img


@app.route('/userava/<username>/<path:filename>')
def userava(username, filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_USER_AVA'], filename)


def getHeaderByLogin(app, login):
    img = None
    user = dbase.getUserByLogin(login) 
    if user:
        if not user['header']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='img/default_header.jpg'),
                                       "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию: " + str(e))
        else:
            img = user['header']
    return img


@app.route('/header/<username>/<path:filename>')
def header(username, filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_USER_HEADER'], filename)


@app.route('/upload_avatar/<username>', methods=['POST', 'GET'])
@login_required
def upload_avatar(username):
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                photo_filename = str(uuid4()) + f".{file.filename.rsplit('.', 1)[1]}"

                file.save(os.path.join(app.config['UPLOAD_FOLDER_USER_AVA'], photo_filename))

                res = dbase.updateUserAvatar(avatar=photo_filename,
                                             login=username,
                                             type_avatar='avatar')
                if res:
                    flash("Аватар был успешно обновлен", category='success')
                else:
                    flash("Произошла ошибка", category='error')
            except Exception as ex:
                print(ex)
        else:
            flash("Ошибка обновления аватара", category='error')

    return redirect(url_for('change_profile', username=username))


@app.route('/upload_header/<username>', methods=['POST', 'GET'])
@login_required
def upload_header(username):
    users = dbase.getUserByLogin(username)
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                photo_filename = str(uuid4()) + f".{file.filename.rsplit('.', 1)[1]}"

                file.save(os.path.join(app.config['UPLOAD_FOLDER_USER_HEADER'], photo_filename))

                res = dbase.updateUserAvatar(avatar=photo_filename,
                                             login=username,
                                             type_avatar='header')

                if res:
                    flash("Аватар был успешно обновлен", category='success')
                else:
                    flash("Произошла ошибка", category='error')
            except Exception as ex:
                print(ex)
        else:
            flash("Ошибка обновления аватара", category='error')

    return redirect(url_for('change_profile', username=username, users=users))


@app.route('/upload_profile', methods=['POST', 'GET'])
@login_required
def upload_profile():
    return redirect(url_for('profile'))


@app.route('/search')
def search():
    query = request.args.get('query')
    post = dbase.getCardBeat(data=query, colum='text_beat')
    post_genre = dbase.getCardBeat(data=query, colum='genre')
    print(query)
    users = dbase.getUserByTextSearch(query)

    return render_template('search.html', posts=(post + post_genre), search=query, users=users)


if __name__ == "__main__":
    app.run(debug=True)
