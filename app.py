import os
import datetime
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google():
    """Authenticate with Google APIs."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            # Fixed port 8080 for OAuth redirect
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def create_google_meet_event(summary, description, start_time, end_time):
    """Create a Google Calendar event with a Google Meet link."""
    creds = authenticate_google()
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
        'conferenceData': {
            'createRequest': {
                'requestId': 'sample123',  # Unique ID for the request
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                },
            },
        },
    }

    event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
    meet_link = event['hangoutLink']
    return meet_link

# Streamlit GUI
st.title("Google Meet Scheduler")

with st.form("meet_form"):
    st.write("Schedule a Google Meet")
    summary = st.text_input("Meeting Title")
    description = st.text_area("Meeting Description")
    
    # Date and time inputs
    meeting_date = st.date_input("Meeting Date", datetime.date.today())
    meeting_time = st.time_input("Meeting Time", datetime.time(9, 0))  # Default: 9:00 AM
    
    # Combine date and time into datetime object
    start_time = datetime.datetime.combine(meeting_date, meeting_time)
    end_time = start_time + datetime.timedelta(hours=1)  # 1-hour duration
    
    # Submit button
    submitted = st.form_submit_button("Schedule Meeting")

    if submitted:
        meet_link = create_google_meet_event(
            summary,
            description,
            start_time.isoformat(),
            end_time.isoformat()
        )
        st.success(f"Meeting scheduled successfully! Join here: {meet_link}")