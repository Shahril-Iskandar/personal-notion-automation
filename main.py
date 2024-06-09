from gcal import use_credentials, create_event_gcal, update_event_gcal, get_next_250_event_id, update_gcal_to_notion2, get_calendar_id, get_event_id_updated_datetime
from notion import INTERACTIONS_DATABASE_ID, get_notion_database_pages, extracting_interaction_database_page, update_page
# Notion
interaction_pages = get_notion_database_pages(INTERACTIONS_DATABASE_ID)
# print(interaction_pages)

interaction_page_dict = extracting_interaction_database_page(interaction_pages)
print(interaction_page_dict)

# Google Calendar
creds = use_credentials()

# calendar_id = get_calendar_id(creds) # Get the calendar ID of the Google Calendar
# calendar_id = 'fitness.meez1@gmail.com'
calendar_id = 'primary'

# synctoken = get_synctoken(creds)
# event_id, events, events_results = get_next_250_event_id(creds, calendar_id) # Get the next 250 events in Google Calendar
# print(events)

###### Notion to Google Calendar
# create_event_gcal(creds, interaction_page_dict, calendar_id) # New event ID will be assigned and won't create a new event in Google Calendar
# update_event_gcal(creds, interaction_page_dict, calendar_id) # Update event in Google Calendar using existing eventID

##### Google Calendar to Notion
update_gcal_to_notion2(creds, interaction_page_dict) # Update Notion if there's changes made in Google Calendar

