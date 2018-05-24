# coding=utf-8
# 此文件用于用户登录与注册有关的api
import re

from flask import request, jsonify
from flask.globals import current_app

from ihome import redis_store, db
from ihome.models import User
from ihome.utils.response_code import RET
from . import api


@api.route("/users", methods=["POST"])
def register():
    """
    用户注册功能
    1. 接收参数(手机号, 短信验证码, 密码)并进行验证
    2. 从redis中获取短信验证码(如果获取不到,说明短信验证码已过期)
    3. 对比短信验证码,如果一致
    4. 创建User对象并保存注册用户的信息
    5. 把注册用户的信息添加到数据库
    6. 返回应答,注册成功
    :return:
    """
    # 1. 接收参数(手机号, 短信验证码, 密码)并进行验证
    req_dict = request.json
    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="缺少参数")

    if not re.match(r"^1[35789]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号码不正确")

    # 2. 从redis中获取短信验证码(如果获取不到,说明短信验证码已过期)
    try:
        real_sms_code = redis_store.get("smscode:%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取短信验证码失败")
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已过期")

    # 3. 对比短信验证码,是否一致
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码输入错误")

    # 4. 创建User对象并保存注册用户的信息
    user = User()
    user.mobile = mobile
    user.name = mobile
    # todo: 注册密码加密

    # 5. 把注册用户的信息添加到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存注册用户的信息失败")

    # 6. 返回应答,注册成功
    return jsonify(errno=RET.OK, errmsg="注册成功")
