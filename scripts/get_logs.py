import requests, json, sys
url = 'http://127.0.0.1:8001/logs'
try:
    r = requests.get(url, timeout=5)
    print('STATUS', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
