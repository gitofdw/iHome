# coding=utf-8
# 此文件中的api用于提供图片验证码和短信验证码
import random
import re

from flask import make_response, request, jsonify, current_app
from ihome import redis_store, constants
from ihome.utils.SendTemplateSMS import CCPR
from ihome.utils.response_code import RET
from . import api
from ihome.utils.captcha.captcha import captcha


@api.route("/sms_code", methods=["POST"])
def send_sms_code():
    """
    发送短信验证码:
    1. 接收参数(手机号, 图片验证码, 图片验证码表示), 并进行参数校验
    2. 从redis中读取图片验证码(若读取不到,表示验证码已过期)
    3. 对比图片验证码是否一致
    4. 如果一致使用云通讯发送短信
    5. 返回应答,发送短信成功
    """
    # 1.接收参数(手机号, 图片验证码, 图片验证码表示), 并进行参数校验
    req_dict = request.json
    # print req_dict
    mobile = req_dict.get("mobile")
    image_code = req_dict.get("image_code")
    image_code_id = req_dict.get("image_code_id")
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="缺少参数")
    if not re.match(r"^1[35789]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号码不正确")
    # 2.从redis中读取图片验证码(若读取不到, 表示验证码已过期)
    try:
        real_image_code = redis_store.get("imagecode:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取图片验证码失败")
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")

    # 3.对比图片验证码是否一致
    if real_image_code != image_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 4.如果一致使用云通讯发送短信
    # 4.1随机生成一个6位验证码
    sms_code = "%06s" % random.randint(0, 999999)
    # 4.2使用云通讯发送验证码
    try:
        res = CCPR().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    if res != 1:
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信验证码失败")
    # 4.3在redis中保存短信验证码
    try:
        redis_store.set("smscode:%s" % mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")

    # 5.返回应答, 发送短信成功
    return jsonify(errno=RET.OK, errmsg="发送短信成功")


@api.route("/image_code")
def get_image_code():
    """产生图片验证码"""
    # 1.接收参数(图片标识码)并进行校验
    image_code_id = request.args.get("cur_id")
    if not image_code_id:
        return jsonify(errno=RET.PARAMERR, errmsg="缺少参数")
    # 2.生成图片验证码
    # 通过captcha产生验证码
    name, text, content = captcha.generate_captcha()
    # 3.在redis数据库中保存图片验证码
    # redis_store.set("key", "value", "expires")
    try:
        redis_store.set("imagecode:%s" % image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")

    # 4.返回图片验证码
    response = make_response(content)
    response.headers["Content-Type"] = "image/jpg"

    return response
