import requests, json, sys
url = 'http://127.0.0.1:8001/chat'
payload = {
    'session_id': 'test-session',
    'query': 'What is the attendance for STU001 this month?',
    'student_id': 'STU001',
    'use_gemini': False
}
try:
    r = requests.post(url, json=payload, timeout=10)
    print('STATUS', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
