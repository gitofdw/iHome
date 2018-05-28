# -*- coding:utf-8 -*-
from flask import session, g, jsonify, request, current_app
from werkzeug.routing import BaseConverter
import functools
from ihome.utils.response_code import RET


class RegexConverter(BaseConverter):
    """自定义正则转换器"""

    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 进行登录验证
        user_id = session.get("user_id")

        if user_id:
            # 用户已登录
            # 使用g变量临时保存登录用户id, g变量中的内容可以在每次请求开始到请求结束的范围使用
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 用户未登录
            current_app.next = request.headers["Referer"]
            # print g.next
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    return wrapper
