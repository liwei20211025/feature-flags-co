import requests
from datetime import datetime

environmentSecret = 'NmFkLWMwODUtNCUyMDIxMTAxMjIzMDUxOV9fMThfXzI1X181MF9fZGVmYXVsdF9kYzVlMw=='
url_ffEvent = 'https://ffc-api-ce2-dev.chinacloudsites.cn/Variation/GetMultiOptionVariation'
url_customEvent = 'https://ffc-api-ce2-dev.chinacloudsites.cn/ExperimentsDataReceiver/PushData'

# ffEvent
for group in range(0, 3):
    for user in range(1, 10):
        ffUserName = "u_group"+str(group)+"_"+str(user)
        data = {
            "featureFlagKeyName": "mytest",
            "environmentSecret": environmentSecret,
            "ffUserName": ffUserName,
            "ffUserEmail": ffUserName+"@testliang.com",
            "ffUserCountry": "China",
            "ffUserKeyId": ffUserName+"@testliang.com",
        }
        params = {'sessionKey': environmentSecret,
                  'format': 'xml', 'platformId': 1}
        print('ffUser: '+ffUserName)
        response = requests.post(url_ffEvent, params=params, json=data)
        print(response.text)
        print('==================')

# User CustomEvent
for group in range(0, 3):
    for user in range(1, 10 - group):
        ffUserName = "u_group"+str(group)+"_"+str(user)
        data = [
            {
                "route": "index/paypage",
                "secret": environmentSecret,
                # "timeStamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "type": "CustomEvent",
                "eventName": "clickme",
                "user": {
                        "ffUserName": ffUserName,
                        "ffUserEmail": ffUserName+"@testliang.com",
                        "ffUserCountry": "China",
                        "ffUserKeyId": ffUserName+"@testliang.com",
                        "ffUserCustomizedProperties": [
                            {
                                "name": "string",
                                "value": "string"
                            }
                        ]
                },
                "appType": "PythonApp",
                "customizedProperties": [
                    {
                        "name": "string",
                        "value": "string"
                    }
                ]
            }
        ]
        params = {'sessionKey': environmentSecret,
                  'format': 'xml', 'platformId': 1}
        print('ffUser: '+ffUserName)
        response = requests.post(url_customEvent, params=params, json=data)
        print(response.status_code)
        print('==================')
