from dotenv import dotenv_values
import requests
from datetime import datetime, timezone
import json
from utils import generate_random_string

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

def get_notion_database_pages(DATABASE_ID, num_pages=None):
    '''
    If num_pages is None, get all pages in the database, otherwise just the defined number.
    Results will return the information in a list of json.
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

# testing_pages = get_notion_database_pages(TESTING_DATABASE_ID)

# interaction_pages = get_notion_database_pages(INTERACTIONS_DATABASE_ID)

def extracting_testing_database_page(pages):
    page_dict = {}
    for page in pages:
        page_id = page["id"]
        props = page["properties"]

        if props["To sync?"]["checkbox"] == True:
            page_tosync = props["To sync?"]["checkbox"]
        else:
            continue

        page_title = props["Event title"]["title"][0]["text"]["content"]
        page_start_date = props["Date"]["date"]["start"]
        # page_start_date = datetime.now().astimezone(timezone.utc).isoformat()
        page_end_date = props["Date"]["date"]["end"]
        # page_end_date = datetime.now().astimezone(timezone.utc).isoformat()
        page_location = props["Location"]["select"]["name"]

        if not props["Description"]["rich_text"]:
            page_description = None
        else:
            page_description = props["Description"]["rich_text"][0]["text"]["content"]

        if not props["Clients"]["relation"]:
            page_client_id = None
        else:
            page_client_id = props["Clients"]["relation"][0]["id"]
        
        if not props["Attendees"]["rollup"]["array"]:
            page_attendees = None
        else:
            page_attendees = props["Attendees"]["rollup"]["array"][0]["email"]

        page_togcal = props["In gcal?"]["checkbox"]

        page_dict[page_id] = {
            "title": page_title,
            "start_date": page_start_date,
            "end_date": page_end_date,
            "location": page_location,
            "description": page_description,
            "client_id": page_client_id,
            "attendees": page_attendees,
            "tosync": page_tosync,
            "togcal": page_togcal
        }
    # print(page_title, page_start_date, page_end_date, page_location, page_description, page_client, page_attendees, page_tosync, page_togcal)
    return page_dict

def extracting_interaction_database_page(pages):
    '''
    Extracting information from the database ID and returning a dictionary.
    Dictionary format: key is the page id, value is a dictionary of the page information.
    {
        page_id: {
            "title": page_title,
            "start_date": page_start_date,
            "end_date": page_end_date,
            "location": page_location,
            "description": page_description,
            "client_id": page_client_id,
            "tosync": page_tosync,
            "ingcal": page_ingcal,
            "url": page_url,
            "gcal_id": page_gcal_id,
            "sync_token": page_sync_token,
            "updated_datetime": page_updated_datetime
        }
    }
    '''
    page_dict = {}
    for page in pages:
        page_id = page["id"]
        props = page["properties"]

        if props["To sync?"]["checkbox"] == True or props["In gcal?"]["checkbox"] == True:
            page_tosync = props["To sync?"]["checkbox"]
            page_ingcal = props["In gcal?"]["checkbox"]
        else:
            continue

        page_title = props["Meeting name"]["title"][0]["text"]["content"]
        
        page_start_date = props["Date"]["date"]["start"]
        # page_start_date = datetime.now().astimezone(timezone.utc).isoformat()

        if props["Date"]["date"]["end"] == None:
            page_end_date = page_start_date
        else:
            page_end_date = props["Date"]["date"]["end"]
        # page_end_date = datetime.now().astimezone(timezone.utc).isoformat()

        page_location = props["Location"]["select"]["name"]

        if not props["Description"]["rich_text"]: # If list is empty
            page_description = None
        else:
            page_description = props["Description"]["rich_text"][0]["text"]["content"]

        if not props["Client name"]["relation"]:
            page_client_id = None
        else:
            page_client_id = props["Client name"]["relation"][0]["id"]


        page_url = page["url"]

        if not props["Gcal EventID"]["rich_text"]:
            page_gcal_id = None
        else:
            page_gcal_id = props["Gcal EventID"]["rich_text"][0]["text"]["content"]

        if not props["SyncToken"]["rich_text"]:
            page_sync_token = None
        else:
            page_sync_token = props["SyncToken"]["rich_text"][0]["text"]["content"]

        if not props["Updated gcal datetime"]["rich_text"]:
            page_updated_datetime = None
        else:
            page_updated_datetime = props["Updated gcal datetime"]["rich_text"][0]["text"]["content"]

        page_dict[page_id] = {
            "title": page_title,
            "start_date": page_start_date,
            "end_date": page_end_date,
            "location": page_location,
            "description": page_description,
            "client_id": page_client_id,
            "tosync": page_tosync,
            "ingcal": page_ingcal,
            "url": page_url,
            "gcal_id": page_gcal_id,
            "sync_token": page_sync_token,
            "updated_datetime": page_updated_datetime
        }
    if not page_dict: # If page_dict is empty
        print("No pages detected to sync.")
    # print(page_title, page_start_date, page_end_date, page_location, page_description, page_client, page_attendees, page_tosync, page_togcal)
    return page_dict    

# testing_page_dict = extracting_testing_database_page(testing_pages)

# interaction_page_dict = extracting_interaction_database_page(interaction_pages)

def accessing_extracted_page(page_dict: dict):
    for page_id, page_info in page_dict.items():
        print(f"Page ID: {page_id}")
        print(f"Title: {page_info['title']}")
        print(f"Start Date: {page_info['start_date']}")
        print(f"End Date: {page_info['end_date']}")
        print(f"Location: {page_info['location']}")
        print(f"Description: {page_info['description']}")
        print(f"Client ID: {page_info['client_id']}")
        print(f"Attendees: {page_info['attendees']}")
        print(f"To Sync?: {page_info['tosync']}")
        print(f"In GCal?: {page_info['togcal']}")
        print("\n")

# accessing_extracted_page(testing_page_dict)

def accessing_extracted_interaction_page(page_dict: dict):
    for page_id, page_info in page_dict.items():
        print(f"Page ID: {page_id}")
        print(f"Title: {page_info['title']}")
        print(f"Start Date: {page_info['start_date']}")
        print(f"End Date: {page_info['end_date']}")
        print(f"Location: {page_info['location']}") # To put in calendar location
        print(f"Description: {page_info['description']}") # To put in after url in description
        print(f"Client ID: {page_info['client_id']}")
        print(f"To Sync?: {page_info['tosync']}")
        print(f"In GCal?: {page_info['togcal']}")
        print(f"URL: {page_info['url']}") # To put in calendar description
        print("\n")

# accessing_extracted_interaction_page(interaction_page_dict)

def create_notion_page(data: dict):
    create_url = "https://api.notion.com/v1/pages"

    payload ={"parent": {"database_id": TESTING_DATABASE_ID}, "properties": data}
    
    res = requests.post(create_url, json=payload, headers=headers)
    print(res.status_code)
    return res

# data = {
#     "Meeting name": {"title": [{"text": {"content": "Event 4"}}]},
#     "Date": {"date": {"start": f"{page_start_date}", "end": f"{page_end_date}"}},
#     "Location": {"select": {"name": "Online" }},
#     "Description": {"rich_text": [{"text": {"content": "Description 4"}}]},
#     "Clients": {"relation": [{"id": "993f64b2-9b1e-4a10-b8ab-e6c9fdbfa97e"}]},
#     "To sync?": {"checkbox": False},
#     "In gcal?": {"checkbox": False},
# }

# create_notion_page(data)

# Try see if can get client name from client id

def find_client_name(page_dict: dict):
    clients = get_notion_database_pages(CLIENTS_DATABASE_ID)
    client_page_dict = {}
    for client in clients:
        client_id = client["id"]
        props = client["properties"]
        client_name = props["Name"]["title"][0]["text"]["content"]

        client_page_dict[client_id] = {
            "name": client_name
        }

    # Match the client id found in page id to the client name 
    for page_id, page_info in page_dict.items():
        client_id = page_info['client_id']
        if client_id in client_page_dict:
            client_name = client_page_dict[client_id]['name']
            print(f"Page ID: {page_id} has client: {client_name}")
    return client_page_dict

# client_id_name_dict = find_client_name(interaction_page_dict)

def update_page(page_id: str, data: dict):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {"properties": data}

    res = requests.patch(url, json=payload, headers=headers)
    print(res.status_code)
    return res