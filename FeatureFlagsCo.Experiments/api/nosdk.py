from flask.wrappers import Response
from ExperimentApiPy import app
from flask import jsonify, request
from datetime import datetime
import requests
from config.config_handling import get_config_value
from requests.auth import HTTPBasicAuth 
import json


import numpy as np
import scipy as sp
from scipy import stats
from datetime import datetime
import math

_es_config = get_config_value('elastic', 'es_host')
_es_hosts = _es_config
_es_username= get_config_value('elasticusername', 'es_username')
_es_passwd = get_config_value('elasticpasswd', 'es_passwd')

@app.route('/api/nosdk', methods=['POST'])
def nosdk():

    #########################################################
    #inputdata json format:
    #  {'Flag' : 
    #        {'Id' : FlagId,
    #         'BaselineVariation': 'var2', 
    #          'Variations: [value1, value2, value3]
    #          }, 
    #    'EventName': xxx,
    #    'StartExptTime': '946731600000', 
    #    'EndExptTime': Timestamp2
    #   }
    ##########################################################
   
    # Get data from frontend
    Index = "ffvariationrequestindex"
    startime = datetime.now()
    data = request.get_json()
    # Query Flag data
    query_body_A = {
                "from": 0,
                "query": {
                    "bool": {
                    "must": [
                        {
                        "match": {
                            'FeatureFlagId.keyword': data['Flag']['Id'] 
                        }
                        }, {
                                "match": {
                                    "EnvId.keyword": data['Flag']['Id'].split('__')[3]
                                }
                        }
                    ],
                    "filter": {
                        "range": {
                            "TimeStamp": {
                                # when no start time selected: defaut time to 2000-01-01:01H
                                "gte": "2000-01-01T01:00:00" if data['StartExptTime'] == "" else data['StartExptTime'],
                                # when no end time selected: defaut time to NOW
                                "lte":  datetime.now() if  data['EndExptTime'] == "" else data['EndExptTime']
                            }
                        }
                    }
                    }
                },
                "sort": [
                    {
                        "TimeStamp": {
                            "order": "desc"
                        }
                    }
                ],
                "aggs": {
                    "keys": {
                    "composite": {
                        "sources": [
                        {
                            "UserKeyId": {
                            "terms": {
                                "field": "UserKeyId.keyword"
                            }
                            }
                        },
                        {
                            "VariationLocalId": {
                            "terms": {
                                "field": "VariationLocalId.keyword"
                            }
                            }
                        }
                        ],
                        "size": 10000
                    }
                    }
                },
                "size": 0
                }
                    
    
    r1 = requests.post(_es_hosts + '/ffvariationrequestindex/_search', auth = HTTPBasicAuth(_es_username, _es_passwd), headers={"content-type":"application/json"} ,data = json.dumps(query_body_A))
    endtime1 = datetime.now()

    query_body_B ={
                    "from": 0,
                    "query": {
                        "bool": {
                            "must": [{
                                "match": {
                                            'EventName.keyword' : data['EventName']
                                }
                            }, {
                                "match": {
                                    "EnvironmentId.keyword": data['Flag']['Id'].split('__')[3]
                                }
                            }],
                            "filter": {
                                "range": {
                                    "TimeStamp": {
                                            # when no start time selected: defaut time to 2000-01-01:01H
                                            "gte": "2000-01-01T01:00:00" if data['StartExptTime'] == "" else data['StartExptTime'],
                                            # when no end time selected: defaut time to NOW
                                            "lte":  datetime.now() if  data['EndExptTime'] == "" else data['EndExptTime']
                                    }
                                }
                            }
                        }
                    },
                    "sort": [
                        {
                            "TimeStamp": {
                                "order": "desc"
                            }
                        }
                    ],
                    "aggs": {
                        "keys": {
                            "composite": {
                                "sources": [{
                                    "UserKeyId": {
                                        "terms": {
                                            "field": "User.FFUserKeyId.keyword"
                                        }
                                    }
                                }],
                                "size": 10000
                            }
                        }
                    },
                    "size": 0
                }

    r2 = requests.post(_es_hosts + '/experiments/_search', auth = HTTPBasicAuth(_es_username, _es_passwd), headers={"content-type":"application/json"} ,data = json.dumps(query_body_B))
    endtime2 = datetime.now()

    # results = {
    #     "request1": {"timeInSeconds": (endtime1-startime).total_seconds(), "data": r1.json()},
    #     "request2": {"timeInSeconds": (endtime2-endtime1).total_seconds(), "data": r2.json()}
    # }

    res_A = r1.json()
    res_B = r2.json()
    # Stat of Flag
    var_baseline = data['Flag']['BaselineVariation']
    dict_var_user = {}
    dict_var_occurence = {}

    for item in res_A['aggregations']['keys']['buckets']:
        value = item['key']['VariationLocalId']
        user  = item['key']['UserKeyId']
        if  value not in list(dict_var_occurence.keys()) :
            dict_var_occurence[ value ]  = 1
            dict_var_user[ value ]  = [user]
        else :
            dict_var_occurence[ value] = dict_var_occurence[ value] + 1
            dict_var_user[ value ]  =  dict_var_user[ value] + [user]

    print('dictionary of flag var:occurence')
    print(dict_var_occurence)  
      
    for item in dict_var_user.keys():
        dict_var_user[item] = list(set(dict_var_user[item]))


    # Stat of Expt.
    dict_expt_occurence = {}
    for item in res_B['aggregations']['keys']['buckets']:
        user  = item['key']['UserKeyId']
        for it in dict_var_user.keys():
            if user in dict_var_user[it] :
                if it not in list(dict_expt_occurence.keys()):
                    dict_expt_occurence[it] = 1
                else:
                    dict_expt_occurence[it] = 1 + dict_expt_occurence[it]

    print('dictionary of expt var:occurence')
    print(dict_expt_occurence)

    # Get Confidence interval
    def mean_confidence_interval(data, confidence=0.95):
        a = 1.0 * np.array(data)
        n = len(a)
        m, se = np.mean(a), sp.stats.sem(a)
        h = se * sp.stats.t.ppf((1 + confidence) / 2., n-1)
        return m, m-h, m+h

    output = []
    # If  (baseline variation usage = 0) or  (baseline variation customer event = 0 )
    if var_baseline not in list(dict_var_occurence.keys()) or var_baseline not in dict_expt_occurence.keys():
        for item in dict_var_occurence.keys(): 
            if item in  dict_expt_occurence.keys():
                dist_item = [1 for i in range(dict_expt_occurence[item])] + [0 for i in range(dict_var_occurence[item]-dict_expt_occurence[item])]
                rate, min, max = mean_confidence_interval(dist_item)
                if math.isnan(min) or math.isnan(max):
                    confidenceInterval = [-1, -1]
                else:
                    confidenceInterval = [ 0 if round(min,2)<0 else round(min,2), 1 if round(max,2)>1 else round(max,2)]
                pValue = -1
                output.append({ 'variation': item,
                                'conversion' : dict_expt_occurence[item],  
                                'uniqueUsers' : dict_var_occurence[item], 
                                'conversionRate':   round(rate,2),
                                'changeToBaseline' : -1,
                                'confidenceInterval': confidenceInterval, 
                                'pValue': -1 ,
                                'isBaseline': True if data['Flag']['BaselineVariation'] == item else False, 
                                'isWinner': False,
                                'isInvalid': True 
                                } 
                            )
    else:
        BaselineRate = dict_expt_occurence[var_baseline]/dict_var_occurence[var_baseline]
        # Preprare Baseline data sample distribution for Pvalue Calculation 
        dist_baseline = [1 for i in range(dict_expt_occurence[var_baseline])] + [0 for i in range(dict_var_occurence[var_baseline]-dict_expt_occurence[var_baseline])] 
        for item in dict_var_occurence.keys(): 
            if item in  dict_expt_occurence.keys():
                dist_item = [1 for i in range(dict_expt_occurence[item])] + [0 for i in range(dict_var_occurence[item]-dict_expt_occurence[item])]
                rate, min, max = mean_confidence_interval(dist_item)
                if math.isnan(min) or math.isnan(max):
                    confidenceInterval = [-1, -1]
                else:
                    confidenceInterval = [ 0 if round(min,2)<0 else round(min,2), 1 if round(max,2)>1 else round(max,2)]
                pValue = round(1-stats.ttest_ind(dist_baseline, dist_item).pvalue,2)
                output.append({ 'variation': item,
                                'conversion' : dict_expt_occurence[item],  
                                'uniqueUsers' : dict_var_occurence[item], 
                                'conversionRate':   round(rate,3),
                                'changeToBaseline' : round(rate,3) - round(BaselineRate,3),
                                'confidenceInterval': confidenceInterval, 
                                'pValue': -1 if math.isnan(pValue) else pValue,
                                'isBaseline': True if data['Flag']['BaselineVariation'] == item else False, 
                                'isWinner': False,
                                'isInvalid': True if (pValue < 0.95) or math.isnan(pValue) else False
                                } 
                            )
        # Get winner variation
        listValid = [output.index(item) for item in output if item['isInvalid'] == False]

        # If at least one variation is valid:
        if len(listValid) != 0: 
            dictValid = {}
            for index in listValid:
                dictValid[index] = output[index]['conversionRate']
            maxRateIndex = [k for k, v in sorted(dictValid.items(), key=lambda item: item[1])][-1]    
            # when baseline has the highest conversion rate
            if output[maxRateIndex]['changeToBaseline'] > 0:  
                output[maxRateIndex]['isWinner'] = True

    print('ExptResults:')
    print(output)
    endtime = datetime.now()
    print('processing time:') 
    print((endtime-startime))
    return jsonify(output)