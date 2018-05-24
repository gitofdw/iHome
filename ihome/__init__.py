# -*- coding:utf-8 -*-
import redis
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import config
from ihome.utils.commons import RegexConverter

# 数据库
db = SQLAlchemy()
# 全局可用的redis
redis_store = None
# 开启csrf保护
csrf = CSRFProtect()


def set_logging(log_level):
    # 设置日志的记录等级
    logging.basicConfig(level=log_level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):

    app = Flask(__name__)

    config_cls = config[config_name]

    # 日志等级设置
    set_logging(config_cls.LOG_LEVEL)
    # 配置
    app.config.from_object(config_cls)
    # 初始化数据库
    db.init_app(app)
    # 设置redis
    global redis_store
    redis_store = redis.StrictRedis(host=config_cls.REDIS_HOST, port=config_cls.REDIS_PORT)
    # 开启csrf保护
    csrf.init_app(app)
    # 开启session
    Session(app)

    # 添加路由转换器,必须在注册蓝图之前,因为在蓝图中有使用这个路由不然注册蓝图前加载不到
    app.url_map.converters['re'] = RegexConverter

    # 注册蓝图,在使用时再引入
    from ihome.api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0')

    # 注册html静态文件的蓝图
    from ihome.web_html import html
    app.register_blueprint(html)

    return app
