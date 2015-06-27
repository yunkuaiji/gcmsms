# -*- encoding: utf-8 -*-
# #############################################################################
#
#
#  2015 广西云会计财税服务有限公司 (http://www.yunkuaiji.me)
#
# #############################################################################
__author__ = 'Edward Pie'
import requests
import json


class GCMServer(object):
    def __init__(self, server_key):
        self.server_key = server_key
        self.headers = {"Authorization": "%s=%s" % ("key", self.server_key), "Content-Type": "application/json"}
        self.url = "https://android.googleapis.com/gcm/send"

    def send_to_one(self, gcm_id, data):
        try:
            payload = {"data": data, "registration_ids": [gcm_id]}
            data = json.dumps(payload)
            response = requests.post(self.url, headers=self.headers, data=data)

            print "Response Status Code : ", response.status_code
            print "Response Body : ", response.json()
        except Exception, e:
            print "Oops! An error occured! ", e.message

    def send_to_many(self, gcm_ids, data):
        try:
            payload = {"data": data, "registration_ids": gcm_ids}
            data=json.dumps(payload)
            response = requests.post(self.url, headers=self.headers, data=data)

            print "Response Status Code : ", response.status_code
            print "Response Body : ", response.json()
        except Exception, e:
            print "Oops! An error occured! ", e.message

def main():
    gcm = "password"
    data = {'number': 'mobile number', 'message': 'odoo 测试 GCMSMS 网关: gcmsend_suceed'}

    reg_id ='android device reg_id'

    server = GCMServer(gcm)
    server.send_to_one(reg_id, data)
################################################################################

if __name__ == '__main__':
    main()