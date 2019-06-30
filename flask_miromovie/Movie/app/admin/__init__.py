# -*- coding:utf-8 -*-
__author__ = 'meng'
__date__ = '2019/6/4 14:47'

from flask import Blueprint

# 定义蓝图
admin = Blueprint('admin', __name__)
import views
