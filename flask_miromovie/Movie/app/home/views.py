# -*- coding:utf-8 -*-
__author__ = 'meng'
__date__ = '2019/6/4 14:53'

from flask import render_template, url_for, redirect, flash, session, request, abort
from app.home.forms import RegistForm, LoginForm, UserdetailForm, CommentForm
from app.models import Admin, Tag, Movie, Preview, User, Userlog, \
    Auth, Adminlog, Comment, Moviecol, Oplog, Role
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from app import db, app
import os
import datetime
import uuid
from app.home import home


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    # 时间+唯一标识符+后缀
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


# 装饰器访问限制
def home_login_reg(func):
    @wraps(func)  # 保留原函数的属性
    def decorated_func(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return func(*args, **kwargs)
    return decorated_func


# 电影首页
@home.route('/')
def index():
    tags = Tag.query.all()
    tid = request.args.get("tid", 0)
    page_data = Movie.query
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))
    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))
    time = request.args.get("time", 0)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )
    pm = request.args.get("pm", 0)
    if int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(
                Movie.playnums.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.playnums.asc()
            )
    cm = request.args.get("cm", 0)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(
                Movie.commentnums.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.commentnums.asc()
            )
    page = request.args.get("page", 1)
    page_data = page_data.paginate(page=int(page), per_page=2)
    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm
    )
    return render_template('home/index.html',tags=tags, p=p, page_data=page_data)


# 上映预告
@home.route('/animation/')
def animation():
    data = Preview.query.all()
    return render_template('home/animation.html', data=data)


# 登录页面
@home.route('/login/',methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if user is None:
            flash("用户不存在！", 'err')
            return redirect(url_for("home.login"))
        if not user.check_pwd(data["pwd"]):
            flash('密码错误', 'err')
            return redirect(url_for("home.login"))
        session["user"] = user.name
        session["user_id"] = user.id
        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(url_for("home.user")) or redirect(request.args.get("next"))
    return render_template('home/login.html', form=form)


# 登出
@home.route('/logout/')
@home_login_reg
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    return redirect(url_for("home.login"))


# 注册页面
@home.route('/register/', methods=["GET", "POST"])
def register():
    form = RegistForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            pwd=generate_password_hash(data["pwd"]),
            uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功", 'ok')
    return render_template('home/register.html', form=form)


# 用户中心页面
@home.route('/user/', methods=["GET", "POST"])
@home_login_reg
def user():
    form = UserdetailForm()
    user = User.query.get_or_404(int(session["user_id"]))
    form.face.validators = []
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        if not form.face.data.filename == '':
            file_face = secure_filename(form.face.data.filename)
            if not os.path.exists(app.config["FC_DIR"]):
                os.makedirs(app.config["FC_DIR"])
                os.chmod(app.config["FC_DIR"], "rw")
            user.face = change_filename(file_face)
            form.face.data.save(app.config["FC_DIR"]+user.face)
        name_count = User.query.filter_by(name=data["name"].count)
        if data["name"] != user.name and name_count == 1:
            flash("昵称已经存在", "err")
            return redirect(url_for("home.user"))
        email_count = User.query.filter_by(email=data["email"].count)
        if data["email"] != user.email and email_count == 1:
            flash("邮箱已经存在", "err")
            return redirect(url_for("home.user"))
        phone_count = User.query.filter_by(phone=data["phone"].count)
        if data["phone"] != user.phone and phone_count == 1:
            flash("手机已经存在", "err")
            return redirect(url_for("home.user"))
        user.name = data["name"]
        user.phone = data["phone"]
        user.email = data["email"]
        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("修改成功", 'ok')
        return redirect(url_for("home.user"))
    return render_template('home/user.html', form=form, user=user)


# 修改密码页面
@home.route('/pwd/')
@home_login_reg
def pwd():
    return render_template('home/pwd.html')


# 登录日志页面
@home.route('/loginlog/<int:page>/', methods=["GET"])
@home_login_reg
def loginlog(page=None):
    if page is None:
        page = 1
    page_data = Userlog.query.filter_by(
        user_id=int(session["user_id"])
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('home/loginlog.html', page_data=page_data)


# 用户评论页面
@home.route('/comments/<int:page>/', methods=["GET"])
@home_login_reg
def comments(page=None):
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == session["user_id"]
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=3)
    return render_template('home/comments.html', page_data=page_data)


# 电影收藏页面
@home.route('/moviecol/<int:page>/', methods=["GET"])
@home_login_reg
def moviecol(page=None):
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == session["user_id"]
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=3)
    return render_template('home/moviecol.html', page_data=page_data)


# 电影添加收藏页面
@home.route('/moviecol/add/', methods=["GET"])
@home_login_reg
def moviecol_add():
    uid = request.args.get("uid", "")
    mid = request.args.get("mid", "")
    moviecol = Moviecol.query.filter_by(
         user_id=int(uid),
        movie_id=int(mid)
    ).count()
    if moviecol == 1:
        data = dict(ok=0)
        flash("已收藏", "1")
    if moviecol == 0:
        moviecol = Moviecol(
            user_id=int(uid),
            movie_id=int(mid)
        )
        db.session.add(moviecol)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)


# 搜索页面
@home.route('/search/<int:page>/', methods=["GET"])
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get("key", "")
    movie_count = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')
    ).count()
    page_data = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=1)
    return render_template('home/search.html', movie_count=movie_count,
                           page_data=page_data, key=key)


# 电影播放页面
@home.route('/play/<int:id>/<int:page>/', methods=["GET", "POST"])
def play(id=None, page=None):
    moviecol = Moviecol.query.filter_by(
        movie_id=int(id),
        user_id=int(session["user_id"])
    ).count()
    movie = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    movie.playnums += 1
    movie.commentnums += 1
    form = CommentForm()
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data["content"],
            movie_id=movie.id,
            user_id=session['user_id']
        )
        db.session.add(comment)
        db.session.commit()
        movie.commentnums += 1
        flash("添加评论成功", 'ok')
        return redirect(url_for("home.play", id=movie.id, page=1))
    return render_template('home/play.html', movie=movie, form=form, page_data=page_data, moviecol=moviecol)
