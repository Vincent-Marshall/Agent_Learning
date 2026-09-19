# test.py
import requests

resp = requests.get('https://httpbin.ceshiren.com/get', timeout=10)
print(resp.status_code)
print(resp.json())
