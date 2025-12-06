def update_folder_path(page_id, folder_path):
    """Updates the Folder Path property and inserts a clickable link."""
    from .notion import update_page_property
    file_url = f"file://{folder_path}"
    update_page_property(
        page_id=page_id,
        property_name="Folder Path",
        value=file_url  # url type supports file:// links
    )


def get_page_by_title(title):
    """
    Search for a Notion page by its title. Returns the first matching page object or None.
    """
    from .notion import BASE_URL, headers
    import requests
    url = f"{BASE_URL}/search"
    payload = {"query": title, "filter": {"value": "page", "property": "object"}}
    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            for page in results:
                # Defensive: check for title property in different places
                props = page.get("properties", {})
                if "title" in props:
                    title_prop = props["title"].get("title", [])
                    if title_prop and title_prop[0].get("plain_text", "") == title:
                        return page
                # Fallback: check for direct title in page
                if "title" in page and page["title"]:
                    if page["title"][0]["text"]["content"] == title:
                        return page
        return None
    except Exception as e:
        print(f"[Notion] Error searching for page by title: {e}")
        return None
