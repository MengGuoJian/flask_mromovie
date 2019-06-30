# -*- coding:utf-8 -*-
__author__ = 'meng'
__date__ = '2019/6/4 14:48'

from flask import Blueprint

# 定义蓝图
home = Blueprint('home', __name__, url_prefix='/home')
from app.home import views
