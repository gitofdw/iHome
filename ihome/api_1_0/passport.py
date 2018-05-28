# coding=utf-8
# 此文件用于用户登录与注册有关的api
import re

from flask import request, jsonify, session
from flask.globals import current_app
from ihome import redis_store, db
from ihome.models import User
from ihome.utils.response_code import RET
from . import api


@api.route("/sessions")
def check_user_login():
    """
    获取用户登录信息
    """
    user_id = session.get("user_id", "")
    username = session.get("user_name", "")

    return jsonify(errno=RET.OK, errmsg="OK", data={"user_id": user_id, "username": username})


@api.route("/sessions", methods=["POST"])
def login():
    """
    用户登录
    1.接收参数(手机号, 密码)并进行校验
    2.根据手机号区查询User信息
    3.校验用户名和密码是否正确
    4.记录用户的登录状态
    5.返回应答,登录成功
    """
    # 1.接收参数(手机号, 密码)并进行校验
    req_dict = request.json
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 2.根据手机号区查询User信息.

    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户信息失败")

    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")
    # 3.校验密码是否正确
    if not user.check_user_password(password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")
    # 4.记录用户的登录状态
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["user_name"] = user.name
    if hasattr(current_app, "next"):
        url = re.match("http://127.0.0.1:5000/(.*)", current_app.next).group(1)
        data = {"next": url}
        return jsonify(errno="4000", data=data)
    # 5.返回应答,登录成功
    return jsonify(errno=RET.OK, errmsg="登录成功")


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
        print real_sms_code
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取短信验证码失败")
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已过期")

    # 3. 对比短信验证码,是否一致
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码输入错误")
    # 判断手机号是否已注册
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户信息失败")
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已注册")

    # 4. 创建User对象并保存注册用户的信息
    user = User()
    user.mobile = mobile
    user.name = mobile
    # todo: 注册密码加密
    user.password = password
    # 5. 把注册用户的信息添加到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存注册用户的信息失败")

    # 记录用户的登录状态
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["user_name"] = user.name
    # 6. 返回应答,注册成功
    return jsonify(errno=RET.OK, errmsg="注册成功")
