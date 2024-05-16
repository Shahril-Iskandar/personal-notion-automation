from gcal import use_credentials, create_event
from notion import get_json_file, get_notion_database_pages, extracting_interaction_database_page
from dotenv import dotenv_values
import requests
from datetime import datetime, timezone
import json

SCOPES = ["https://www.googleapis.com/auth/calendar"]

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

# Notion
interaction_pages = get_notion_database_pages(INTERACTIONS_DATABASE_ID)
interaction_page_dict = extracting_interaction_database_page(interaction_pages)

# Google Calendar
creds = use_credentials()
# print(interaction_page_dict)
create_event(creds, interaction_page_dict)