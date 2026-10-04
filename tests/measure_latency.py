import urllib.request
import time
import json

endpoints = [
    ('/', 'GET', None),
    ('/health', 'GET', None),
    ('/advisor', 'GET', None),
    ('/disease', 'GET', None),
    ('/yield', 'GET', None),
    ('/recommend', 'GET', None),
    ('/price', 'GET', None),
    ('/models', 'GET', None),
    ('/login', 'GET', None),
    ('/register', 'GET', None),
    ('/api/models', 'GET', None),
    ('/api/yield', 'POST', {'crop': 'rice', 'rainfall': 200, 'temperature': 25, 'humidity': 80, 'soil_ph': 6.5, 'nitrogen': 90, 'phosphorus': 42, 'potassium': 43, 'area': 2.0}),
    ('/api/recommend', 'POST', {'nitrogen': 90, 'phosphorus': 42, 'potassium': 43, 'temperature': 25, 'humidity': 80, 'ph': 6.5, 'rainfall': 200}),
    ('/api/price', 'POST', {'crop': 'rice'}),
    ('/api/advisor', 'POST', {'nitrogen': 90, 'phosphorus': 42, 'potassium': 43, 'temperature': 25, 'humidity': 80, 'ph': 6.5, 'rainfall': 200, 'area': 2.0, 'has_disease_risk': True}),
]

print(f"{'Endpoint':<22} {'Method':<8} {'Status':<8} {'Latency':<12}")
print("-" * 52)
for path, method, payload in endpoints:
    url = f"http://127.0.0.1:5000{path}"
    req = urllib.request.Request(url, method=method)
    if payload:
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(payload).encode('utf-8')
    else:
        data = None
    start = time.perf_counter()
    resp = urllib.request.urlopen(req, data=data)
    dur_ms = (time.perf_counter() - start) * 1000
    print(f"{path:<22} {method:<8} {resp.status:<8} {dur_ms:.2f} ms")
