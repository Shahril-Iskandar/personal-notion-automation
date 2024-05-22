import os.path
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from notion import update_page

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def use_credentials():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

def get_next_250_event_id(creds):
    '''
    Get the next 250 events in the calendar from today.
    
    Return in list.
    '''
    try:
        service = build("calendar", "v3", credentials=creds)

        now = dt.datetime.now().isoformat() + "Z"

        # Ten upcoming events
        print(f"Getting the upcoming 250 events")
        events_result = service.events().list(calendarId="primary", timeMin=now,
                                        maxResults=250, singleEvents=True,
                                        orderBy="startTime").execute()
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
        
        # Get event_id
        event_id = []
        for event in events:
            # start = event["start"].get("dateTime", event["start"].get("date"))
            # print(start, event["summary"], event["id"])
            event_id.append(event["id"])
        # return start, event["summary"]
        return event_id
    
    except HttpError as error:
        print(f"An error occurred: {error}")

def create_event(creds, page_dict: dict):
    try:
        service = build("calendar", "v3", credentials=creds)

        for page_id, page_info in page_dict.items():
            if page_info['tosync'] == True and page_info['ingcal'] == False:
                title = page_info['title']
                start_date = page_info['start_date']
                end_date = page_info['end_date']
                location = page_info['location']
                description = page_info['description']
                url =  page_info['url']
                
                event = {
                    "summary": f"{title}",
                    "location": f"{location}",
                    "description": f"{url} \n\n{description}" ,
                    "colorId": 6,
                    "start": {
                        "dateTime": f"{start_date}",
                        "timeZone": "Asia/Singapore",
                    },
                    "end": {
                        "dateTime": f"{end_date}",
                        "timeZone": "Asia/Singapore",
                    },
                    # "recurrence": [
                    #     "RRULE:FREQ=DAILY;COUNT=2",
                    # ],
                    # "id" : f"{id}",
                }

                event = service.events().insert(calendarId="primary", body=event).execute()
                    
                # If successfully added, then change notion tosync to False and ingcal to True
                update_data = {"To sync?" : {"checkbox": False}, 
                                "In gcal?": {"checkbox": True},
                                "Gcal ID": {"rich_text": [{"text": {"content": event.get("id")}}]} # Insert unique event id to Notion for future tracking
                                }

                update_page(page_id, update_data)

                print(f"Event created: {event.get('htmlLink')}")
    
    except HttpError as error:
        print(f"An error occurred: {error}")
    
def update_event(creds, page_dict:dict):
    try:
        service = build("calendar", "v3", credentials=creds)

        for page_id, page_info in page_dict.items():
            if page_info['tosync'] == True and page_info['ingcal'] == True:
                title = page_info['title']
                start_date = page_info['start_date']
                end_date = page_info['end_date']
                location = page_info['location']
                description = page_info['description']
                url =  page_info['url']
                gcal_id = page_info['gcal_id']

                event = {
                    "summary": f"{title}",
                    "location": f"{location}",
                    "description": f"{url} \n\n{description}" ,
                    "colorId": 6,
                    "start": {
                        "dateTime": f"{start_date}",
                        "timeZone": "Asia/Singapore",
                    },
                    "end": {
                        "dateTime": f"{end_date}",
                        "timeZone": "Asia/Singapore",
                    },
                }

                service.events().update(calendarId="primary", eventId=gcal_id, body=event).execute()
                
                update_data = {"To sync?" : {"checkbox": False}, 
                            }

                update_page(page_id, update_data)
                print(f"Event ID {gcal_id} updated. \n")

    except HttpError as error:
        print(f"An error occurred: {error}")

def delete_event(creds, page_dict:dict):
    event_ids = get_next_250_event_id(creds)
    print(f"Event IDs retrieved: {event_ids} \n")
    try:
        service = build("calendar", "v3", credentials=creds)

        for _, page_info in page_dict.items():
            gcal_id = page_info['gcal_id']
        print(f"Event ID to be deleted: {gcal_id} \n")
        for event_id in event_ids:
            if event_id != gcal_id:
                print(event_id)
                service.events().delete(calendarId="primary", eventId=event_id).execute()
                print(f"Event ID {event_id} updated. \n")

    except HttpError as error:
        print(f"An error occurred: {error}")

# if __name__ == "__main__":
    # creds = use_credentials()