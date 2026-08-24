import requests
import json

BASE = 'http://127.0.0.1:8003'

def post(path, payload):
    url = BASE + path
    try:
        r = requests.post(url, json=payload, timeout=10)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, r.text
    except Exception as e:
        return None, str(e)

print('Cost:', post('/api/cost-prediction', {'feature1':10,'feature2':0.5}))
print('Demand:', post('/api/demand-forecast', {'recent_series':[100,110,105]}))
print('Eval:', post('/api/technical-evaluation', {'query':'warranty'}))
