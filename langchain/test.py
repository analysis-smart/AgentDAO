import requests
import test_obj

control = input('dev?pro?:')
if control == 'dev':
    base_url = 'http://127.0.0.1:8000/'
elif control == 'pro':
    base_url = 'http://127.0.0.1:8000/'
else:
    exit()
url_list = [test_obj.agent_obj]

import time
import json
import base64
t1 = time.time()
for obj in url_list:
    if 'files' in obj:
        files = obj['files']
    else:
        files = None
    if control == 'nlp':
        json_str = json.dumps(obj['par'])
        b64 = base64.b64encode(json_str.encode('utf-8'))
        res = requests.post(base_url + obj['url'],data=b64)
    else:
        print(obj['par'])
        res = requests.post(base_url + obj['url'],files=files,data=obj['par'])
    if control =='nlp':
        res_str = res.content.decode(res.encoding)
        res_list = res_str.strip().split("\n")
        print(res_list)
        exit()
    if res.status_code == 200:
        print(res)
        res_json = res.json()
        print(res_json)
    else:
        print('fail:')
        print(res)
        print(res.status_code)
        print(res.text)
    t2 = time.time()
    print(t2 - t1)