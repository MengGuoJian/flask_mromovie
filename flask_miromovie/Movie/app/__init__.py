# -*- coding:utf-8 -*-
__author__ = 'meng'
__date__ = '2019/6/4 14:47'

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql
import os


app = Flask(__name__)
db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:123456@127.0.0.1:3306/movie'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_POOL_SIZE"] = 100
app.config["SECRET_KEY"] = '40ec4c9136494ad18a9435f4698fdfae'
#app.config["DEBUG"] = True
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
app.config["FC_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/user/")

from app.admin import admin as admin_blueprint
from app.home import home as home_blueprint


app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(home_blueprint)


# 404报错
@app.errorhandler(404)
def page_not_found(error):
    return render_template("home/404.html")
