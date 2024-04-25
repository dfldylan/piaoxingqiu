# -*- coding: gbk -*-
import requests
import json

def send_wechat_message(content):
    token = 'a87bb4ebcc9e413290ba4971bb6720e9'
    url = "http://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": "程序结束通知",
        "content": content
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(url, data=json.dumps(data), headers=headers)
