import requests

def call_api(url, method="GET", payload=None):
    if method == "GET":
        return requests.get(url, params=payload).json()
    else:
        return requests.post(url, json=payload).json()
