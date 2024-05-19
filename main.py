from gcal import use_credentials, create_event, get_next_250_event_id, update_event
from notion import INTERACTIONS_DATABASE_ID, get_notion_database_pages, extracting_interaction_database_page

# Notion
interaction_pages = get_notion_database_pages(INTERACTIONS_DATABASE_ID)
interaction_page_dict = extracting_interaction_database_page(interaction_pages)

# Google Calendar
creds = use_credentials()

# print(interaction_page_dict)
# create_event(creds, interaction_page_dict)

# Check google calender
event_id = get_next_250_event_id(creds)

# Get Notion to sync
# If gcal is true, check for the id, then update it.
id_to_update = []
for page_id, page_info in interaction_page_dict.items():
    id = page_info['gcal_id']

    if id in event_id:
        print(f"ID: {id} is to be updated in gcal.")
        id_to_update.append(id)
print(id_to_update)

update_event(creds, interaction_page_dict)