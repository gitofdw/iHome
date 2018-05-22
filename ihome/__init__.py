# -*- coding:utf-8 -*-


import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from config import config
from ihome.utils.commons import RegexConverter

# 数据库
db = SQLAlchemy()
# 全局可用的redis
redis_store = None
# 开启csrf保护
csrf = CSRFProtect()


def create_app(config_name):

    app = Flask(__name__)

    # 配置
    app.config.from_object(config[config_name])
    # 初始化数据库
    db.init_app(app)
    # 设置redis
    global redis_store
    redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 开启csrf保护
    csrf.init_app(app)
    # 开启session
    Session(app)

    app.url_map.converters['re'] = RegexConverter

    # 注册蓝图,在使用时再引入
    import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix='/api/v1.0')

    # 注册html静态文件的蓝图
    import web_html
    app.register_blueprint(web_html.html)

    return app
