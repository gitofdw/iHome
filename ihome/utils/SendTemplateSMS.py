# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from ihome.libs.ytx.CCPRestSDK import REST
import ConfigParser

# ���ʺ�
accountSid = '8aaf0708635e4ce001638d430faf1e42'

# ���ʺ�Token
accountToken = '94aeb6b74d5d45fabe48e02545f91f9a'

# Ӧ��Id
appId = '8aaf0708635e4ce001638d4310111e49'

# �����ַ����ʽ���£�����Ҫдhttp://
serverIP = 'app.cloopen.com'

# ����˿�
serverPort = '8883'

# REST�汾��
softVersion = '2013-12-26'


class CCPR(object):
    def __init__(self):
        # ��ʼ��REST SDK
        self.rest = REST(serverIP, serverPort, softVersion)
        self.rest.setAccount(accountSid, accountToken)
        self.rest.setAppId(appId)

    # ����ģ�����
    # @param to �ֻ�����
    # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
    # @param $tempId ģ��Id

    def send_template_sms(self, to, datas, tempId):
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # print result
        if result.get("statusCode") == "000000":
            return 1
        else:
            return 0


# sendTemplateSMS(�ֻ�����,��������,ģ��Id)
if __name__ == '__main__':
    # sendTemplateSMS("17620489652", ["1222", 5], 1)
    CCPR().send_template_sms("17620489652", ["1222", 5], 1)
