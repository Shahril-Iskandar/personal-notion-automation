import os.path
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from notion import update_page

from utils import generate_random_string

from datetime import datetime


SCOPES = ["https://www.googleapis.com/auth/calendar"]

def parse_datetime(dt_str):
    # Remove the 'Z' and parse the string
    return datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%fZ')

def use_credentials():
    creds = None
  # The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
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

def get_synctoken(creds, calendar_id="primary"):
    try:
        service = build("calendar", "v3", credentials=creds)

        events_result = service.events().list(calendarId=calendar_id, maxResults=250, singleEvents=True).execute()

        synctoken = events_result.get("nextSyncToken")

    except HttpError as error:
        print(f"An error occurred: {error}")
    
    return synctoken

def get_next_250_event_id(creds, calendar_id="primary"):
    '''
    Get the next 250 events in the calendar from today.
    
    Return in list.
    '''
    try:
        service = build("calendar", "v3", credentials=creds)

        now = dt.datetime.now().isoformat() + "Z"

        # upcoming 250 events
        print(f"Getting the upcoming 250 events")
        events_result = service.events().list(calendarId=calendar_id, timeMin=now,
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
        return event_id, events, events_result
    
    except HttpError as error:
        print(f"An error occurred: {error}")

def get_event_id_updated_datetime(creds, calendar_id="primary"):
    '''
    Output Example:
    {'vvin75s7rgj2idqutque6ora30': 
        {'updated': '2024-06-09T07:37:38.186Z', 'summary': 'Event testing', 
        'description': 'https://www.notion.so/Event-testing-e5d5b5038bcd473794cba1cdeaaa017d\n\nDescription here', 'location': 'Physical meet-up', 
        'start': '2024-06-10T09:00:00+08:00', 'end': '2024-06-10T10:00:00+08:00'}, 
    'tueo86rc2j0gh8b9fejq16i8rs': 
        {'updated': '2024-06-09T09:16:36.225Z', 'summary': 'Event testing 2', 
        'description': 'https://www.notion.so/Event-testing-2-d01f6bb93933425ba4334def9e942a2c\n\nDescription changed 5:16pm', 'location': 'Zoom', 
        'start': '2024-06-11T10:00:00+08:00', 'end': '2024-06-11T12:00:00+08:00'}}
    '''
    try:
        service = build("calendar", "v3", credentials=creds)

        now = dt.datetime.now().isoformat() + "Z"

        # upcoming 250 events
        print(f"Getting the upcoming 250 events id and datetime updated")
        events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                        maxResults=250, singleEvents=True,
                                        orderBy="startTime").execute()
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")

        # Get event_id and updated datetime
        events_dict = {}
        for event in events:
            events_dict[event["id"]] = {
                "updated": event["updated"],
                "summary": event['summary'],                
                "description": event['description'],
                "location": event['location'],
                "start": event['start']['dateTime'],
                "end": event['end']['dateTime'],
            }
        return events_dict
    
    except HttpError as error:
        print(f"An error occurred: {error}")

def create_event_gcal(creds, page_dict: dict, calendar_id="primary"):
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
                # new_sync_token = generate_random_string()
                
                event = {
                    "summary": f"{title}",
                    "location": f"{location}",
                    "description": f"{url}\n\n{description}" ,
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

                event = service.events().insert(calendarId=calendar_id, body=event).execute()
                    
                # If successfully added, then change notion tosync to False and ingcal to True
                update_data = {"To sync?" : {"checkbox": False}, 
                                "In gcal?": {"checkbox": True},
                                "Gcal EventID": {"rich_text": [{"text": {"content": event.get("id")}}]}, # Insert unique event id to Notion for future tracking
                                # "SyncToken": {"rich_text": [{"text": {"content": new_sync_token}}]}, # Insert newly created sync token
                                "Updated gcal datetime": {"rich_text": [{"text": {"content": event.get("updated")}}]},
                                }

                update_page(page_id, update_data)

                print(f"Event created: {event.get('htmlLink')}")
    
    except HttpError as error:
        print(f"An error occurred: {error}")
    
def update_event_gcal(creds, page_dict:dict, calendar_id="primary"):
    try:
        service = build("calendar", "v3", credentials=creds)

        for page_id, page_info in page_dict.items():
            if page_info['tosync'] == True and page_info['ingcal'] == True:
                # print(page_info)
                title = page_info['title']
                start_date = page_info['start_date']
                end_date = page_info['end_date']
                location = page_info['location']
                description = page_info['description']
                url =  page_info['url']
                gcal_id = page_info['gcal_id']
                # new_sync_token = generate_random_string()

                event = {
                    "summary": f"{title}",
                    "location": f"{location}",
                    "description": f"{url}\n\n{description}" ,
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

                event = service.events().update(calendarId=calendar_id, eventId=gcal_id, body=event).execute()
                
                update_data = {"To sync?" : {"checkbox": False},
                                # "SyncToken": {"rich_text": [{"text": {"content": new_sync_token}}]},
                                "Updated gcal datetime": {"rich_text": [{"text": {"content": event.get("updated")}}]},
                            }

                update_page(page_id, update_data)
                print(f"Event ID {gcal_id} updated. \n")

    except HttpError as error:
        print(f"An error occurred: {error}")

def delete_event(creds, page_dict:dict, calendar_id="primary"):
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
                service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
                print(f"Event ID {event_id} updated. \n")

    except HttpError as error:
        print(f"An error occurred: {error}")

# if __name__ == "__main__":
    # creds = use_credentials()

def update_gcal_to_notion(creds, page_dict:dict, calendar_id="primary"):
    service = build("calendar", "v3", credentials=creds)

    now = dt.datetime.now().isoformat() + "Z"

    # Get upcoming events
    print(f"Getting the upcoming 250 events")
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                    maxResults=250, singleEvents=True,
                                    orderBy="startTime").execute()
    events = events_result.get("items", [])

    for event in events:
        event_id = event['id']
        description = event['description']
        split_desc = description.split('\n\n')
        description = split_desc[1]

        for page_id, page_info in page_dict.items():
            gcal_id = page_info['gcal_id']

            if event_id == gcal_id:
                print(f"The event ID {event_id} matches the Google Calendar ID {gcal_id}.")

                data = {
                    "Meeting name": {"title": [{"text": {"content": f"{event['summary']}"}}]},
                    "Date": {"date": {"start": f"{event['start']['dateTime']}", "end": f"{event['end']['dateTime']}" }},
                    "Location": {"select": {"name": f"{event['location']}" }},
                    "Description": {"rich_text": [{"text": {"content": f"{description}"}}]},
                    "To sync?": {"checkbox": False},
                    "In gcal?": {"checkbox": True},
                }

                update_page(page_id, data)

                print('Event updated in Notion. \n')

# Update Notion if there's changes made in Google Calendar
def update_gcal_to_notion2(creds, page_dict:dict):    
    events_id_datetime_dict = get_event_id_updated_datetime(creds)

    for notion_id, notion_data in page_dict.items():
        gcal_id = notion_data['gcal_id']
        print(f"Event ID: {gcal_id}")

        if gcal_id in events_id_datetime_dict:
            # print(gcal_id)
            gcal_updated = events_id_datetime_dict[gcal_id]['updated']
            print(f"Google updated time: {gcal_updated}")
            print(f"Notion updated time: {notion_data['updated_datetime']}")

            if notion_data['updated_datetime'] != gcal_updated:
                # Need to add condition to check if event in Gcal or Notion is updated
                datetime_obj1 = parse_datetime(gcal_updated)
                datetime_obj2 = parse_datetime(notion_data['updated_datetime'])

                if datetime_obj1 > datetime_obj2:
                    print(f"Google Calendar updated is later than the one in Notion")
                    print("To update Notion with GCal updated time.")

                    updated_description = events_id_datetime_dict[gcal_id]['description']
                    split_desc = updated_description.split('\n\n')
                    updated_description = split_desc[1]

                    updated_data = {
                        "Meeting name": {"title": [{"text": {"content": f"{events_id_datetime_dict[gcal_id]['summary']}"}}]},
                        "Date": {"date": {"start": f"{events_id_datetime_dict[gcal_id]['start']}", "end": f"{events_id_datetime_dict[gcal_id]['end']}" }},
                        "Location": {"select": {"name": f"{events_id_datetime_dict[gcal_id]['location']}" }},
                        "Description": {"rich_text": [{"text": {"content": f"{updated_description}"}}]},
                        "To sync?": {"checkbox": False},
                        "In gcal?": {"checkbox": True},
                        "Updated gcal datetime": {"rich_text": [{"text": {"content": gcal_updated}}]},
                    }
                # elif datetime_obj1 < datetime_obj2:
                #     print(f"Google Calendar updated is earlier than the one in Notion")
                
                    update_page(notion_id, updated_data)
                    print('Notion has been updated.')

def get_calendar_id(creds):
    service = build("calendar", "v3", credentials=creds)

    page_token = None
    
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            # print(calendar_list_entry['id'])
            if calendar_list_entry['id'] == 'fitness.meez1@gmail.com':
                calendar_id = calendar_list_entry['id']
                break

        page_token = calendar_list.get('nextPageToken')
        
        if not page_token:
            break

    return calendar_id

