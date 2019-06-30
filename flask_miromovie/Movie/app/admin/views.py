# -*- coding:utf-8 -*-
__author__ = 'meng'
__date__ = '2019/6/4 14:54'

from flask import render_template, url_for, redirect, flash, session, request, abort
from app.admin import admin
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, AuthForm, RoleForm, AdminForm
from app.models import Admin, Tag, Movie, Preview, User, Userlog, \
    Auth, Adminlog, Comment, Moviecol, Oplog, Role
from functools import wraps
from werkzeug.utils import secure_filename
from app import db, app
import os
import datetime
import uuid


# 上下文全局处理器
@admin.context_processor
def tpl_extra():
    data = dict(
        online_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:S")
    )
    return data


# 装饰器访问限制
def admin_login_reg(func):
    @wraps(func)  # 保留原函数的属性
    def decorated_func(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return func(*args, **kwargs)

    return decorated_func


# 权限访问限制
def admin_auth(func):
    @wraps(func)
    def decorate_func(*args, **kwargs):
        admin = Admin.query.join(Role).filter(
            Role.id == Admin.role_id,
            Admin.id == session["admin_id"]
        ).first()
        auths = admin.role.auths
        auths = list(map(lambda v: int(v), auths.split(",")))
        auth_list = Auth.query.all()
        # 返回一个["规则"]的urls
        urls = [v.url for v in auth_list for val in auths if val == v.id]
        rule = request.url_rule
        if str(rule) not in urls:
            abort(404)
        return func(*args, **kwargs)
    return decorate_func


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    # 时间+唯一标识符+后缀
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


# 首页 控制面板
@admin.route('/')
@admin_login_reg
def index():
    return render_template("admin/index.html")


# 登录页面
@admin.route('/login/', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        data = login_form.data  # 把提交的数据提取
        admin = Admin.query.filter_by(name=data["user"]).first()  # 查询数据取一条
        if not admin.check_pwd(data['pwd']):
            flash("密码错误")  # 信息闪现
            return redirect(url_for("admin.login"))
        session["admin"] = data["user"]  # 保存登录后的session
        session["admin_id"] = admin.id
        adminlog = Adminlog(
            admin_id=admin.id,
            ip=request.remote_addr
        )
        db.session.add(adminlog)
        db.session.commit()
        return redirect(url_for("admin.index")) or redirect(request.args.get("next"))  # 回到没登陆错误前的页面

    return render_template('admin/login.html', login_form=login_form)


# 登出
@admin.route('/logout/')
@admin_login_reg
def logout():
    session.pop("admin", None)
    session.pop("admin_id", None)
    return redirect(url_for("admin.login"))


# 修改密码
@admin.route('/pwd/')
@admin_login_reg
def pwd():
    return render_template('admin/pwd.html')


# 添加标签
@admin.route('/tag/add/', methods=["GET", "POST"])
@admin_login_reg
@admin_auth
def tag_add():
    tag_form = TagForm()
    if tag_form.validate_on_submit():
        data = tag_form.data
        num = Tag.query.filter_by(name=data["name"]).count()
        if num == 1:
            flash("名称已经存在", category="exit")
            return redirect(url_for("admin.tag_add"))
        tag = Tag(
            name=data["name"]
        )
        db.session.add(tag)
        db.session.commit()
        flash("添加标签成功", 'ok')
        oplog = Oplog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加标签%s" % data["name"]
        )
        db.session.add(oplog)
        db.session.commit()
        redirect(url_for("admin.tag_add"))
    return render_template('admin/tag_add.html', tag_form=tag_form)


# 编辑标签
@admin.route('/tag/edit/<int:id>/', methods=["GET", "POST"])
@admin_login_reg
def tag_edit(id=None):
    tag_form = TagForm()
    tag = Tag.query.get_or_404(id)  # 查询不到会报404
    if tag_form.validate_on_submit():
        data = tag_form.data
        num = Tag.query.filter_by(name=data["name"]).count()
        if tag.name != data["name"] and num == 1:
            flash("名称已经存在", category="exit")
            return redirect(url_for("admin.tag_edit", id=tag.id))
        tag.name = data["name"]
        db.session.add(tag)
        db.session.commit()
        flash("编辑标签成功", 'ok')
        redirect(url_for("admin.tag_edit", id=tag.id))
    return render_template('admin/tag_edit.html', tag_form=tag_form, tag=tag)


# 标签列表
@admin.route('/tag/list/<int:page>/', methods=["GET"])
@admin_login_reg
def tag_list(page=None):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.addtime.desc()  # 通过addtime的降序排序
    ).paginate(page=page, per_page=3)  # 把查询结果分页，每页一个数据
    return render_template('admin/tag_list.html', page_data=page_data)


# 删除标签
@admin.route('/tag/del/<int:id>/', methods=["GET"])
@admin_login_reg
def tag_del(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("标签已删除", "ok")
    return redirect(url_for("admin.tag_list", page=1))


# 添加电影
@admin.route('/movie/add/', methods=["GET", "POST"])
@admin_login_reg
def movie_add():
    movie_form = MovieForm()
    if movie_form.validate_on_submit():
        data = movie_form.data
        file_url = secure_filename(movie_form.url.data.filename)
        file_logo = secure_filename(movie_form.logo.data.filename)
        # 如果不存在路径就创建，给予可读可写权限
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        # 数据保存
        movie_form.url.data.save(app.config["UP_DIR"] + url)
        movie_form.logo.data.save(app.config["UP_DIR"] + logo)
        movie = Movie(
            title=data["title"],
            url=url,
            logo=logo,
            star=int(data["star"]),
            info=data["info"],
            playnums=0,
            commentnums=0,
            tag_id=int(data["tag_id"]),
            area=data["area"],
            release_time=data["release_time"],
            length=data["length"]
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功", 'ok')
        return redirect(url_for("admin.movie_add"))
    return render_template('admin/movie_add.html', movie_form=movie_form)


# 编辑电影
@admin.route('/movie/edit/<int:id>/', methods=["GET", "POST"])
@admin_login_reg
def movie_edit(id=None):
    movie_form = MovieForm()
    # 因为url和logo应该是存在的，所以不需要验证过滤
    movie_form.url.validators = []
    movie_form.logo.validators = []
    movie_query = Movie.query.get_or_404(int(id))
    # 一些数据value赋值不行可以通过后台添加
    if request.method == "GET":
        movie_form.info.data = movie_query.info
        movie_form.tag_id.data = movie_query.tag_id
        movie_form.star.data = movie_query.star
    if movie_form.validate_on_submit():
        data = movie_form.data
        movie_count = Movie.query.filter_by(title=data["title"]).count()
        # 避免电影重名
        if movie_count == 1 and movie_query.title != data["title"]:
            flash("片名已存在", 'err')
            return redirect(url_for("admin.movie_edit", id=int(id)))
        # 如果不存在路径就创建，给予可读可写权限
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")

        if movie_form.url.data.filename != "":
            file_url = secure_filename(movie_form.url.data.filename)
            movie_query.url = change_filename(file_url)
            movie_form.url.data.save(app.config["UP_DIR"] + movie_query.url)

        if movie_form.logo.data.filename != "":
            file_logo = secure_filename(movie_form.logo.data.filename)
            movie_query.logo = change_filename(file_logo)
            movie_form.logo.data.save(app.config["UP_DIR"] + movie_query.logo)
        # 数据保存
        movie_query.title = data["title"],
        movie_query.star = int(data["star"]),
        movie_query.info = data["info"],
        movie_query.tag_id = int(data["tag_id"]),
        movie_query.area = data["area"],
        movie_query.release_time = data["release_time"],
        movie_query.length = data["length"]
        db.session.add(movie_query)
        db.session.commit()
        flash("修改电影成功", 'ok')
        return redirect(url_for("admin.movie_edit", id=int(id)))
    return render_template('admin/movie_edit.html', movie_form=movie_form, movie_query=movie_query)


# 电影列表
@admin.route('/movie/list/<int:page>/', methods=["GET"])
@admin_login_reg
def movie_list(page=None):
    if page is None:
        page = 1
    page_data = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id
    ).order_by(
        Tag.addtime.desc()  # 通过addtime的降序排序
    ).paginate(page=page, per_page=3)  # 把查询结果分页，每页3个数据
    return render_template('admin/movie_list.html', page_data=page_data)


# 删除电影
@admin.route('/movie/del/<int:id>/', methods=["GET"])
@admin_login_reg
def movie_del(id=None):
    movie = Movie.query.get_or_404(int(id))
    db.session.delete(movie)
    db.session.commit()
    flash("删除电影成功", "ok")
    return redirect(url_for("admin.movie_list", page=1))


# 添加上映预告
@admin.route('/preview/add/', methods=["GET", "POST"])
@admin_login_reg
def preview_add():
    prev_form = PreviewForm()
    if prev_form.validate_on_submit():
        data = prev_form.data
        file_logo = secure_filename(prev_form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")
        logo = change_filename(file_logo)
        prev_form.logo.data.save(app.config["UP_DIR"] + logo)
        preview = Preview(
            title=data['title'],
            logo=logo
        )
        db.session.add(preview)
        db.session.commit()
        flash("添加预告成功", "ok")
        return redirect(url_for("admin.preview_add"))
    return render_template('admin/preview_add.html', prev_form=prev_form)


# 上映预告列表
@admin.route('/preview/list/<int:page>/', methods=["GET"])
@admin_login_reg
def preview_list(page=None):
    if page is None:
        page = 1
    page_data = Preview.query.order_by(
        Preview.addtime.desc()  # 通过addtime的降序排序
    ).paginate(page=page, per_page=3)  # 把查询结果分页，每页3个数据
    return render_template('admin/preview_list.html', page_data=page_data)


# 删除预告
@admin.route('/preview/del/<int:id>/', methods=["GET"])
@admin_login_reg
def preview_del(id=None):
    preview = Preview.query.get_or_404(int(id))
    db.session.delete(preview)
    db.session.commit()
    flash("删除预告成功", "ok")
    return redirect(url_for("admin.preview_list", page=1))


# 编辑预告
@admin.route('/preview/edit/<int:id>/', methods=["GET", "POST"])
@admin_login_reg
def preview_edit(id=None):
    prev_form = PreviewForm()
    prev_form.logo.validators = []
    prev = Preview.query.get_or_404(int(id))
    if request.method == "GET":
        # 赋值初值
        prev_form.title.data = prev.title
    if prev_form.validate_on_submit():
        data = prev_form.data
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")
        if prev_form.logo.data.filename == "":
            file_logo = secure_filename(prev_form.logo.data.filename)
            logo = change_filename(file_logo)
            prev_form.logo.data.save(app.config["UP_DIR"] + logo)
        prev.title = data["title"]
        db.session.add(prev)
        db.session.commit()
        flash("修改预告成功", "ok")
        return redirect(url_for("admin.preview_edit", id=int(id)))
    return render_template('admin/preview_edit.html', prev_form=prev_form, prev=prev)


# 会员列表
@admin.route('/user/list/<int:page>/')
@admin_login_reg
def user_list(page=None):
    if page is None:
        page = 1
    page_data = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=3)
    return render_template('admin/user_list.html', page_data=page_data)


# 查看会员
@admin.route('/user/view/<int:id>/')
@admin_login_reg
def user_view(id=None):
    user = User.query.get_or_404(int(id))
    return render_template('admin/user_view.html', user=user)


# 删除会员
@admin.route('/user/del/<int:id>/', methods=["GET"])
@admin_login_reg
def user_del(id=None):
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash("删除会员成功", "ok")
    return redirect(url_for("admin.user_list", page=1))


# 评论列表
@admin.route('/comment/list/<int:page>/', methods=["GET"])
@admin_login_reg
def comment_list(page=None):
    if page is None:
        page = 1
    page_data = Comment.query.join(Movie).join(User).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/comment_list.html', page_data=page_data)


# 删除评论
@admin.route('/comment/del/<int:id>/', methods=["GET"])
@admin_login_reg
def comment_del(id=None):
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功", "ok")
    return redirect(url_for("admin.comment_list", page=1))


# 收藏列表
@admin.route('/moviecol/list/<int:page>/', methods=["GET"])
@admin_login_reg
def moviecol_list(page=None):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(Movie).join(User).filter(
        Movie.id == Moviecol.movie_id,
        User.id == Moviecol.user_id
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/moviecol_list.html', page_data=page_data)


# 删除收藏
@admin.route('/moviecol/del/<int:id>/', methods=["GET"])
@admin_login_reg
def moviecol_del(id=None):
    moviecol = Moviecol.query.get_or_404(int(id))
    db.session.delete(moviecol)
    db.session.commit()
    flash("删除收藏成功", "ok")
    return redirect(url_for("admin.moviecol_list", page=1))


# 操作日志列表
@admin.route('/oplog/list/<int:page>/', methods=["GET"])
@admin_login_reg
def oplog_list(page=None):
    if page is None:
        page = 1
    page_data = Oplog.query.join(Admin).filter(
        Admin.id == Oplog.admin_id
    ).order_by(
        Oplog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/oplog_list.html', page_data=page_data)


# 管理员日志列表
@admin.route('/adminloginlog/list/<int:page>/', methods=["GET"])
@admin_login_reg
def adminloginlog_list(page=None):
    if page is None:
        page = 1
    page_data = Adminlog.query.join(Admin).filter(
        Admin.id == Adminlog.admin_id
    ).order_by(
        Adminlog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/adminloginlog_list.html', page_data=page_data)


# 会员日志列表
@admin.route('/userloginlog/list/<int:page>/', methods=["GET"])
@admin_login_reg
def userloginlog_list(page=None):
    if page is None:
        page = 1
    page_data = Userlog.query.join(User).filter(
        User.id == Userlog.user_id
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/userloginlog_list.html', page_data=page_data)


# 添加角色
@admin.route('/role/add/', methods=["GET", "POST"])
def role_add():
    form = RoleForm()
    if form.validate_on_submit():
        data = form.data
        role = Role(
            name=data["name"],
            auths=",".join(map(lambda v: str(v), data["auths"]))
        )
        db.session.add(role)
        db.session.commit()
        flash("添加角色成功", "ok")
    return render_template('admin/role_add.html', form=form)


# 角色列表
@admin.route('/role/list/<int:page>/', methods=["GET"])
@admin_login_reg
def role_list(page=None):
    if page is None:
        page = 1
    page_data = Role.query.order_by(
        Role.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/role_list.html', page_data=page_data)


# 删除角色
@admin.route('/role/del/<int:id>/', methods=["GET"])
@admin_login_reg
def role_del(id=None):
    role = Role.query.get_or_404(int(id))
    db.session.delete(role)
    db.session.commit()
    flash("删除角色成功", "ok")
    return redirect(url_for("admin.role_list", page=1))


# 编辑角色
@admin.route('/role/edit/<int:id>/', methods=["GET", "POST"])
def role_edit(id=None):
    form = RoleForm()
    role = Role.query.get_or_404(int(id))
    if request.method == "GET":
        auths = role.auths
        # 表单提交设置时为int的列表
        form.auths.data = list(map(lambda v: int(v), auths.split(",")))
    if form.validate_on_submit():
        data = form.data
        role.name = data["name"],
        # 保存数据库时为字符串的列表
        role.auths = ",".join(map(lambda v: str(v), data["auths"]))
        db.session.add(role)
        db.session.commit()
        flash("修改角色成功", "ok")
    return render_template('admin/role_edit.html', form=form, role=role)


# 添加权限
@admin.route('/auth/add/', methods=["GET", "POST"])
@admin_login_reg
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth = Auth(
            name=data["name"],
            url=data["url"]
        )
        db.session.add(auth)
        db.session.commit()
        flash("添加权限成功", "ok")
    return render_template('admin/auth_add.html', form=form)


# 权限列表
@admin.route('/auth/list/<int:page>/', methods=["GET"])
@admin_login_reg
def auth_list(page=None):
    if page is None:
        page = 1
    page_data = Auth.query.order_by(
        Auth.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/auth_list.html', page_data=page_data)


# 删除权限
@admin.route('/auth/del/<int:id>/', methods=["GET"])
@admin_login_reg
def auth_del(id=None):
    auth = Auth.query.get_or_404(int(id))
    db.session.delete(auth)
    db.session.commit()
    flash("删除权限成功", "ok")
    return redirect(url_for("admin.auth_list", page=1))


# 编辑权限
@admin.route('/auth/edit/<int:id>/', methods=["GET", "POST"])
@admin_login_reg
def auth_edit(id=None):
    form = AuthForm()
    auth = Auth.query.get_or_404(int(id))
    if form.validate_on_submit():
        data = form.data
        auth.url = data["url"]
        auth.name = data["name"]
        db.session.add(auth)
        db.session.commit()
        flash("编辑权限成功", "ok")
    return render_template('admin/auth_edit.html', form=form, auth=auth)


# 添加管理员
@admin.route('/admin/add/', methods=["GET", "POST"])
@admin_login_reg
def admin_add():
    form = AdminForm()
    from werkzeug.security import generate_password_hash
    if form.validate_on_submit():
        data = form.data
        admin = Admin(
            name=data["name"],
            pwd=generate_password_hash(data['pwd']),
            role_id=data["role_id"],
            is_super=1
        )
        db.session.add(admin)
        db.session.commit()
        flash("添加管理员成功", 'ok')
    return render_template('admin/admin_add.html',form=form)


# 管理员列表
@admin.route('/admin/list/<int:page>/', methods=["GET"])
@admin_login_reg
def admin_list(page=None):
    if page is None:
        page = 1
    page_data = Admin.query.join(Role).filter(
        Role.id == Admin.role_id
    ).order_by(
        Admin.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template('admin/admin_list.html',page_data=page_data)
