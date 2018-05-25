# coding=utf8
# 此文件用于获取用户信息相关的api
from flask import session, jsonify
from flask.globals import current_app

from ihome.models import User
from ihome.utils.response_code import RET
from . import api


@api.route('/user')
def get_user_info():
    """
    获取用户个人信息
    0.判断用户是否登录
    1.获取登录用户的id
    2.根据id查询用户的信息(如果查不到,说明用户不存在)
    3.组织数据,返回应答
    """
    # todo:0.判断用户是否登录
    # 1.获取登录用户的id
    user_id = session.get("user_id")

    # 2.根据id查询用户的信息(如果查不到,说明用户不存在)
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户信息失败")

    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")

    # 3.组织数据,返回应答
    resp = {
        "user_id": user.id,
        "username": user.name,
        "avatar_url": user.avatar_url
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=resp)
