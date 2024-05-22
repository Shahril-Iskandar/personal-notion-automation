from gcal import use_credentials, create_event, update_event, get_next_250_event_id, update_gcal_to_notion
from notion import INTERACTIONS_DATABASE_ID, get_notion_database_pages, extracting_interaction_database_page

# Notion
interaction_pages = get_notion_database_pages(INTERACTIONS_DATABASE_ID)
interaction_page_dict = extracting_interaction_database_page(interaction_pages)

# Google Calendar
creds = use_credentials()

create_event(creds, interaction_page_dict) # New event ID will be assigned and won't create a new event in Google Calendar

update_event(creds, interaction_page_dict) # Update event in Google Calendar using existing eventID

update_gcal_to_notion(creds, interaction_page_dict) # Update Notion if there's changes made in Google Calendar