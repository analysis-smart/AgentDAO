import json
import os

if os.path.exists('1.txt'):
    with open('1.txt','rb') as f:
        file_data = f.read()
else:
    file_data = None


agent_obj = {
    'par':{
        "input_data":{
            "input":"你好",
            "chat_history": []
        },
        # 'name_str':'%s' % json.dumps({'name':'xiaoyu'})
        
    },
    # 'files': file_data,
    'url':'agent'
}