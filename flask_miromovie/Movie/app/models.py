# -*- coding:utf-8 -*-
__author__ = 'meng'
__date__ = '2019/6/4 14:51'
import datetime
from app import db


# 会员
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 昵称
    pwd = db.Column(db.String(100))  # 密码
    email = db.Column(db.String(100), unique=True)  # 邮箱
    phone = db.Column(db.String(11), unique=True)  # 手机
    info = db.Column(db.Text)  # 个性简介
    face = db.Column(db.String(255), unique=True)  # 头像
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    uuid = db.Column(db.String(255), unique=True)  # 唯一标志符
    userlog = db.relationship('Userlog', backref='user')  # 会员日志外键关系
    comments = db.relationship('Comment', backref='user')  # 用户评论
    moviecols = db.relationship('Moviecol', backref='user')  # 用户收藏

    def __repr__(self):
        return "<User %r>" % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


# 会员登录日志
class Userlog(db.Model):
    __tablename__ = 'userlog'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员
    ip = db.Column(db.String(100))  # 登录ip
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 登录时间

    def __repr__(self):
        return '<Userlog %r>' % self.id


# 标签
class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 标题
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 添加时间
    movie = db.relationship("Movie", backref='tag')  # 电影外键关系关联

    def __repr__(self):
        return '<Tag %r>' % self.name


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)  # 标题
    url = db.Column(db.String(255), unique=True)  # 播放地址
    info = db.Column(db.Text)  # 个性简介
    logo = db.Column(db.String(255), unique=True)  # logo封面
    star = db.Column(db.SmallInteger)  # 星级
    playnums = db.Column(db.BigInteger)  # 播放次数
    commentnums = db.Column(db.BigInteger)  # 评论量
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))  # 所属标签
    area = db.Column(db.String(255))  # 上映地区
    release_time = db.Column(db.Date)  # 上映日期，日期类型
    length = db.Column(db.String(100))  # 电影播放长度
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 添加时间
    comments = db.relationship('Comment', backref='movie')  # 电影评论关联
    moviecols = db.relationship('Moviecol', backref='movie')  # 电影收藏

    def __repr__(self):
        return '<Movie %r>' % self.title


# 上映预告
class Preview(db.Model):
    __tablename__ = 'preview'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)  # 标题
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 添加时间
    logo = db.Column(db.String(255), unique=True)  # logo封面

    def __repr__(self):
        return '<Preview %r>' % self.title


# 评论
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    content = db.Column(db.Text)  # 内容
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 添加时间

    def __repr__(self):
        return '<Comment %r>' % self.id


# 电影收藏
class Moviecol(db.Model):
    __tablename__ = 'moviecol'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 添加时间

    def __repr__(self):
        return '<Moviecol %r>' % self.id


# 权限
class Auth(db.Model):
    __tablename__ = 'auth'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 名称
    url = db.Column(db.String(255), unique=True)  # url地址
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 添加时间

    def __repr__(self):
        return '<Auth %r>' % self.name


# 角色
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 名称
    auths = db.Column(db.String(600))  # 权限列表
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 添加时间
    admin = db.relationship('Admin', backref='role')  # 管理员外键关联

    def __repr__(self):
        return '<Role %r>' % self.name


# 管理员
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 管理员账号
    pwd = db.Column(db.String(100))  # 管理员密码
    is_super = db.Column(db.SmallInteger)  # 是否为超级管理员，0为超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 所属角色
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 添加时间
    adminlog = db.relationship('Adminlog', backref='admin')  # 管理员登录日志外键关联
    oplog = db.relationship('Oplog', backref='admin')  # 管理员操作日志外键关联

    def __repr__(self):
        return '<Admin %r>' % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)  # 比较传入的密码和数据库中的密码


# 管理员登录日志
class Adminlog(db.Model):
    __tablename__ = 'adminlog'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
    ip = db.Column(db.String(100))  # 登录ip
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 添加时间

    def __repr__(self):
        return '<Adminlog %r>' % self.id


# 操作日志
class Oplog(db.Model):
    __tablename__ = 'oplog'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
    ip = db.Column(db.String(100))  # 登录ip
    reason = db.Column(db.String(600))  # 操作原因
    addtime = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 添加时间

    def __repr__(self):
        return '<Oplog %r>' % self.id


# if __name__ == '__main__':
#     db.create_all()  # 创建表
    '''
    role = Role(
        name=u'超级管理员01',
        auths='',
    )
    db.session.add(role)  # 添加字段
    db.session.commit()  # 提交，不然不会添加
    '''
    '''
    from werkzeug.security import generate_password_hash

    admin = Admin(
        name='meng',
        pwd=generate_password_hash("meng"),
        is_super=0,
        role_id=1
    )
    db.session.add(admin)  # 添加字段
    db.session.commit()  # 提交，不然不会添加
    '''