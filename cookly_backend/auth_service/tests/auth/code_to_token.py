import requests

url = "http://127.0.0.1:8000/api/code-to-token"

payload = {
    "auth_code": "ef3ef6ef-e1bf-400e-97c1-c90e0cd2f612",
    "code_challenger": "HMRHlfzOTQy4ILCAA6ChG9ZoTrylTIYz7l4WKlvf3C8",
    "redirect_url": "string",
    "scopes": ["string"],
}

headers = {"Content-Type": "application/json"}

# response = requests.post(url, json=payload, headers=headers)
response = requests.request("GET", url, headers=headers)
