from flask import Blueprint, request, url_for, render_template, redirect, g, flash

from .adminlogin import login_admin, isLogged, logout_admin
from .admin_db import AdminDatabase

from loguru import logger

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

db = None

@admin.before_request
def before_request():
    global db
    db = g.get("link_db")


@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request


@admin.route('/')
def index():
    dbase = AdminDatabase(db)
    user = dbase.getAllUser()
    count_beats = dbase.countBeat()
    count_posts = dbase.countPosts()
    count_user = dbase.countUser()
    if not isLogged():
        return redirect(url_for('.login'))
    return render_template('admin/admin_info.html', user=user, beats=count_beats, posts=count_posts,
                           users=count_user)


@admin.route("/login", methods=['POST', 'GET'])
def login():
    if isLogged():
        return redirect(url_for('.index'))
    if request.method == 'POST':
        if request.form['login'] == "bobr" and request.form['psw'] == "qwerty":
            login_admin()
            logger.info('Админ вошел в систему')

            return redirect(url_for('.index'))
        else:
            flash("Неверная пара логин/пароль", category='error')

    return render_template('admin/admin_login.html')


@admin.route('/logout', methods=['POST', 'GET'])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()

    return redirect(url_for('.login'))


@admin.route("/delete_user/<username>")
def delete_user(username):
    dbase = AdminDatabase(db)
    dbase.deleteUser(username)
    return redirect(url_for('.index'))
