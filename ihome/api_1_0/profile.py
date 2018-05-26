# coding=utf8
# 此文件用于获取用户信息相关的api
from flask import session, jsonify
from flask.globals import current_app, request

from ihome import db, constants
from ihome.utils.image_storage import storage_image
from ihome.models import User
from ihome.utils.response_code import RET
from . import api


@api.route("/user/name", methods=["PUT"])
def set_user_name():
    """
    设置用户的用户名:
    # 0. todo: 判断用户是否登录
    # 1. 接收参数(用户名)并进行校验
    # 2. 判断用户名是否重复
    # 3. 设置用户的用户名
    # 4. 返回应答, 设置成功
    """
    #
    # 0. todo: 判断用户是否登录
    # 1. 接收参数(用户名)并进行校验
    req_dict = request.json
    username = req_dict.get("username")

    if not username:
        return jsonify(errno=RET.PARAMERR, errmsg="缺少参数")
    # 2. 判断用户名是否重复
    try:
        user = User.query.filter(User.name == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户信息失败")

    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="用户名已存在")
    user_id = session.get("user_id")

    # 根据id查询用户的信息(如果查不到,说明用户不存在)
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户信息失败")

    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")

    # 3. 设置用户的用户名
    user.name = username
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="设置用户名失败")

    # 4. 返回应答, 设置成功
    return jsonify(errno=RET.OK, errmsg="设置用户名成功")


@api.route("/user/avatar", methods=["POST"])
def set_user_avatar():
    """
    设置用户头像信息:
    # 0. todo: 判断用户是否登录
    # 1. 获取用户上传的头像文件对象
    # 2. 把头像文件上传到七牛云
    # 3. 设置用户头像记录
    # 4. 返回应答, 上传头像成功
    """
    # 0. todo: 判断用户是否登录
    # 1. 获取用户上传的头像文件对象
    file = request.files.get("avatar")
    if not file:
        return jsonify(errno=RET.PARAMERR, errmsg="缺少文件")
    # 2. 把头像文件上传到七牛云
    try:
        key = storage_image(file.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    # 3. 设置用户头像记录
    user_id = session.get("user_id")

    # 根据id查询用户的信息(如果查不到,说明用户不存在)
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户信息失败")

    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")

    user.avatar_url = key

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="设置用户头像失败")

    # 4. 返回应答, 上传头像成功
    avatar_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg="设置头像成功", data={"avatar_url": avatar_url})


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
    # resp = {
    #     "user_id": user.id,
    #     "username": user.name,
    #     "avatar_url": constants.QINIU_DOMIN_PREFIX + user.avatar_url if user.avatar_url else ''
    # }

    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())
