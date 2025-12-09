import os
import requests

def get(endpoint):
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = _headers()
    resp = requests.get(url, headers=headers)
    return resp.json()

def post(endpoint, payload):
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = _headers()
    resp = requests.post(url, headers=headers, json=payload)
    return resp.json()

def patch(endpoint, payload):
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = _headers()
    resp = requests.patch(url, headers=headers, json=payload)
    return resp.json()

def delete(endpoint):
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = _headers()
    resp = requests.delete(url, headers=headers)
    return resp.json()

def _headers():
    token = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
    version = os.getenv("NOTION_VERSION", "2022-06-28")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": version,
        "Content-Type": "application/json"
    }
