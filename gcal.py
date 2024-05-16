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

def get_next_event(creds, service, n: int):
    try:
        service = build("calendar", "v3", credentials=creds)

        now = dt.datetime.now().isoformat() + "Z"

        # Ten upcoming events
        print(f"Getting the upcoming 10 events")
        events_result = service.events().list(calendarId="primary", timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy="startTime").execute()
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
        return start, event["summary"]
    
    except HttpError as error:
        print(f"An error occurred: {error}")

def create_event(creds, page_dict: dict):
    try:
        service = build("calendar", "v3", credentials=creds)

        # now = dt.datetime.now().isoformat() + "Z"

        # # Ten upcoming events
        # print(f"Getting the upcoming 10 events")
        # events_result = service.events().list(calendarId="primary", timeMin=now,
        #                                   maxResults=10, singleEvents=True,
        #                                   orderBy="startTime").execute()
        # events = events_result.get("items", [])

        # if not events:
        #     print("No upcoming events found.")

        # for event in events:
        #     start = event["start"].get("dateTime", event["start"].get("date"))
        #     print(start, event["summary"])
        for page_id, page_info in page_dict.items():
            page_id = page_id
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
            }

            event = service.events().insert(calendarId="primary", body=event).execute()
            # TODO: update notion tosync to False and ingcal to True
            # Check if successfully added, then change notion tosync to False and ingcal to True

            update_data = {"To sync?" : {"checkbox": False}, 
                           "In gcal?": {"checkbox": True}}

            update_page(page_id, update_data)
            
            print(f"Event created: {event.get('htmlLink')}")
    
    except HttpError as error:
        print(f"An error occurred: {error}")

# if __name__ == "__main__":
    # creds = use_credentials()
    
