from dotenv import dotenv_values
import requests
from datetime import datetime, timezone
import json

secrets = dotenv_values(".env")

NOTION_TOKEN = secrets["NOTION_TOKEN"]
INTERACTIONS_DATABASE_ID = secrets["INTERACTIONS_DATABASE_ID"]
CLIENTS_DATABASE_ID = secrets["CLIENTS_DATABASE_ID"]
TESTING_DATABASE_ID = secrets["TESTING_DATABASE_ID"]

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def get_json_file(data):
    with open('db.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data

def get_pages(DATABASE_ID, num_pages=None):
    '''
    If num_pages is None, get all pages in the database, otherwise just the defined number.
    '''
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)
    
    data = response.json()

    get_json_file(data)

    results = data["results"]
    return results

pages = get_pages(TESTING_DATABASE_ID)
for page in pages:
    page_id = page["id"]
    props = page["properties"]

    page_title = props["Event title"]["title"][0]["text"]["content"]
    page_start_date = props["Date"]["date"]["start"]
    page_end_date = props["Date"]["date"]["start"]
    page_location = props["Location"]["rich_text"][0]["text"]["content"]

    if not props["Description"]["rich_text"]:
        page_description = None
    else:
        page_description = props["Description"]["rich_text"][0]["text"]["content"]

    if not props["Clients"]["relation"]:
        page_client = None
    else:
        page_client = props["Clients"]["relation"][0]["id"]
    
    if not props["Attendees"]["rollup"]["array"]:
        page_attendees = None
    else:
        page_attendees = props["Attendees"]["rollup"]["array"][0]["email"]
    
    page_tosync = props["To sync?"]["checkbox"]
    page_togcal = props["In gcal?"]["checkbox"]