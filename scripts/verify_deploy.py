import requests, json, sys
base = 'https://ai-school-erp-assistant.onrender.com'
endpoints = [('/health', 'GET'), ('/dashboard', 'GET'), ('/chat', 'POST')]

for path, method in endpoints:
    url = base + path
    try:
        if method == 'GET':
            r = requests.get(url, timeout=10)
            print('===', path, 'STATUS', r.status_code)
            try:
                print(json.dumps(r.json(), indent=2))
            except Exception:
                print(r.text[:1000])
        else:
            payload = {'session_id': 'verify-session', 'student_id': 'STU001', 'query': 'Show my attendance', 'use_gemini': False}
            r = requests.post(url, json=payload, timeout=15)
            print('===', path, 'STATUS', r.status_code)
            try:
                print(json.dumps(r.json(), indent=2))
            except Exception:
                print(r.text[:1000])
    except Exception as e:
        print('===', path, 'ERROR', str(e))
        sys.exit(1)
print('Verification complete')
