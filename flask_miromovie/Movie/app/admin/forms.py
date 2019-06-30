# -*- coding:utf-8 -*-
__author__ = 'meng'
__date__ = '2019/6/4 14:53'

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Admin, Tag, Auth, Role

tags = Tag.query.all()
auth_list = Auth.query.all()
role_list = Role.query.all()


class LoginForm(FlaskForm):
    """管理员登录表单"""
    user = StringField(
        label="账号",  # 字段的标签
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！",
            #"required": "required"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
            #"required": "required"
        }
    )
    submit = SubmitField(
        label='登录',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }

    )

    def validate_user(self, field):
        user = field.data
        admin = Admin.query.filter_by(name=user).count()
        if admin == 0:
            raise ValidationError("账号不存在")


class TagForm(FlaskForm):
    name = StringField(
        label="标签名称",
        description="标签名称",
        validators=[
            DataRequired(message="请输入标签！")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入标签名称！",
            "id": "input_name"
        }
    )
    submit = SubmitField(
        label='添加',
        render_kw={
            "class": "btn btn-primary",
        }

    )


class MovieForm(FlaskForm):
    title = StringField(
        label="片名",
        description="片名",
        validators=[
            DataRequired(message="请输入片名！")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片名！",
            "id": "input_title"
        }
    )
    url = FileField(
        label='文件',
        description="文件",
        validators=[
            DataRequired(message="请上传文件！")
        ],

    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介！")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入简介！",
            "rows": "10",
            "id": "input_info"
        }

    )
    logo = FileField(
        label='封面',
        description="封面",
        validators=[
            DataRequired(message="请上传封面！")
        ],

    )
    star = SelectField(
        label="星级",
        validators=[
            DataRequired("请输入星级！")
        ],
        coerce=int,
        choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
        description="星级",
        render_kw={
            "class": "form-control",
        }
    )
    tag_id = SelectField(
        label="标签",
        validators=[
            DataRequired("请输入标签！")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in tags],
        description="标签",
        render_kw={
            "class": "form-control",
        }
    )

    area = StringField(
        label="地区",
        validators=[
            DataRequired("请输入地区！")
        ],
        description="地区",
        render_kw={
            "class": "form-control",
             "placeholder": "请输入地区！",
        }
    )
    length = StringField(
        label="片长",
        validators=[
            DataRequired("请输入片长！")
        ],
        description="片长",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片长！",
        }
    )
    release_time = StringField(
        label="上映时间",
        validators=[
            DataRequired("请输入上映时间！")
        ],
        description="片长",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入上映时间！",
            "id": "input_release_time"
        }
    )
    submit = SubmitField(
        label='提交',
        render_kw={
            "class": "btn btn-primary",
        }

    )


class PreviewForm(FlaskForm):
    title = StringField(
        label="预告标题",
        description="预告标题",
        validators=[
            DataRequired("请输入预告标题！")
        ],
        render_kw={
            "class": "btn btn-primary",
            "placeholder": "请输入预告标题",
            "id": "input_title"
        }
    )
    logo = FileField(
        label="预告封面",
        description="预告封面",
        validators=[
            DataRequired(message="请上传封面！")
        ],
    )
    submit = SubmitField(
        label='提交',
        render_kw={
            "class": "btn btn-primary",
        }

    )


class AuthForm(FlaskForm):
    name = StringField(
        label="权限名称",
        description="权限名称",
        validators=[
            DataRequired("请输入权限名称！")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限名称",
        }
    )
    url = StringField(
        label="权限地址",
        description="权限地址",
        validators=[
            DataRequired(message="请输入权限地址！")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限地址",
        }
    )
    submit = SubmitField(
        label='提交',
        render_kw={
            "class": "btn btn-primary",
        }

    )


class RoleForm(FlaskForm):
    name = StringField(
        label="角色名称",
        description="角色名称",
        validators=[
            DataRequired("请输入角色名称！")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入角色名称",
        }
    )
    auths = SelectMultipleField(
        label="权限列表",
        validators=[
            DataRequired("请输入权限列表！")
        ],
        description="权限列表",
        coerce=int,
        choices=[(v.id, v.name) for v in auth_list],
        render_kw={
            "class": "form-control",
        }
    )
    submit = SubmitField(
        label='提交',
        render_kw={
            "class": "btn btn-primary",
        }

    )


class AdminForm(FlaskForm):
    """管理员表单"""
    name = StringField(
        label="管理员名称",  # 字段的标签
        validators=[
            DataRequired("请输入管理员名称！")
        ],
        description="管理员名称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员名称！",
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
            #"required": "required"
        }
    )
    repwd = PasswordField(
        label="重复密码",
        validators=[
            DataRequired("请输入重复密码！"),
            EqualTo("pwd", message="两次密码不一致")
        ],
        description="重复密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入重复密码！",
            # "required": "required"
        }
    )
    role_id = SelectField(
        label="所属角色",
        coerce=int,
        choices=[(v.id, v.name) for v in role_list],
        render_kw={
            "class": "form-control",
    }
    )
    submit = SubmitField(
        label='添加',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }

    )

