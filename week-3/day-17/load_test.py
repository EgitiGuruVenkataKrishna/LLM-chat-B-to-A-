import requests

URL = "http://localhost:8000/generate"

for i in range(100):
    r = requests.get(URL)
    print(i, r.status_code)