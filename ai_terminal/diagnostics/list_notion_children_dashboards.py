import os
from notion.notion import get

def list_children(page_id):
    endpoint = f"blocks/{page_id}/children?page_size=100"
    resp = get(endpoint)
    results = resp.get("results", [])
    for child in results:
        obj_type = child.get("type")
        child_id = child.get("id")
        title = ""
        if obj_type == "child_page":
            title = child.get("child_page", {}).get("title", "")
        elif obj_type == "page":
            title = child.get("properties", {}).get("title", [{}])[0].get("plain_text", "")
        print(f"Type: {obj_type} | ID: {child_id} | Title: {title}")

if __name__ == "__main__":
    page_id = "2bc9333e656d800d9013f5e786799dfa"
    list_children(page_id)
