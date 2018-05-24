# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from ihome.libs.ytx.CCPRestSDK import REST
import ConfigParser

# 主帐号
accountSid = '8aaf0708635e4ce001638d430faf1e42'

# 主帐号Token
accountToken = '94aeb6b74d5d45fabe48e02545f91f9a'

# 应用Id
appId = '8aaf0708635e4ce001638d4310111e49'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


class CCPR(object):
    def __init__(self):
        # 初始化REST SDK
        self.rest = REST(serverIP, serverPort, softVersion)
        self.rest.setAccount(accountSid, accountToken)
        self.rest.setAppId(appId)

    # 发送模板短信
    # @param to 手机号码
    # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
    # @param $tempId 模板Id

    def send_template_sms(self, to, datas, tempId):
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # print result
        if result.get("statusCode") == "000000":
            return 1
        else:
            return 0


# sendTemplateSMS(手机号码,内容数据,模板Id)
if __name__ == '__main__':
    # sendTemplateSMS("17620489652", ["1222", 5], 1)
    CCPR().send_template_sms("17620489652", ["1222", 5], 1)
