# -*-coding:utf-8 -*-
# 此蓝图用于提供静态页面
from flask import Blueprint, current_app, make_response
from flask_wtf.csrf import generate_csrf

html = Blueprint("html", __name__)


@html.route('/<re(".*"):file_name>')
def get_static_heml(file_name):
    """获取静态文件下的html页面返回给浏览器"""
    if file_name == "":
        file_name = "index.html"

    # 获取网站图标
    if file_name != "favicon.ico":
        file_name = "html/" + file_name

    response = make_response(current_app.send_static_file(file_name))

    csrf_token = generate_csrf()
    response.set_cookie("csrf_token", csrf_token)
    return response
