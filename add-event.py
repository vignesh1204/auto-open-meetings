from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import webbrowser
import time
import pytz
import pyttsx3

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
SLEEP_WINDOW_SECS = 60 * 5
OPEN_MEETING_MINUTES_BEFORE = 2
speech_engine = pyttsx3.init()


def get_creds():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_meeting_info():
    creds = get_creds()
    service = build('calendar', 'v3', credentials=creds)

    #Call the Calendar API and get now time
    now = datetime.datetime.utcnow().isoformat() + 'Z' 
    #Setting time window for 8 hours after which app will stop running
    now_plus_window = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).isoformat() + 'Z'
    print('\nGetting the upcoming events\n')
    events_result = service.events().list(calendarId='primary', timeMin=now, maxResults=5, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    for event in events:
        start_time = datetime.datetime.strptime(event['start'].get('dateTime', event['start'].get('date')), '%Y-%m-%dT%H:%M:%S+05:30')
        print(start_time, event['summary'])

def add_event(summary, desc, start_time, end_time):
    creds = get_creds()
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': summary,
        'description': desc,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata',
        },
        'recurrence': [
            'RRULE:FREQ=WEEKLY;UNTIL=20201201T170000Z'
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {
                    'method': 'popup', 
                    'minutes': 2
                }
            ],
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))

def main():
    get_meeting_info()

    #adding ML classes
    add_event('ML Class on Zoom', 'https://us04web.zoom.us/j/78741683738?pwd=RFZNNnBkZEVpVm11V2swVmVLSkZPZz09', '2020-09-14T09:00:00+05:30', '2020-09-14T09:40:00+05:30')
    add_event('ML Class on Zoom','https://us04web.zoom.us/j/78741683738?pwd=RFZNNnBkZEVpVm11V2swVmVLSkZPZz09', '2020-09-15T10:30:00+05:30', '2020-09-15T11:10:00+05:30')
    add_event('ML Class on Zoom','https://us04web.zoom.us/j/78741683738?pwd=RFZNNnBkZEVpVm11V2swVmVLSkZPZz09', '2020-09-16T11:30:00+05:30', '2020-09-16T12:10:00+05:30')
    add_event('ML Class on Zoom','https://us04web.zoom.us/j/78741683738?pwd=RFZNNnBkZEVpVm11V2swVmVLSkZPZz09', '2020-09-17T12:15:00+05:30', '2020-09-17T12:55:00+05:30')

    #adding IOT classes
    add_event('IOT Class on Zoom', 'https://us04web.zoom.us/j/79705372563?pwd=dEtRK1U1MTBUM3RzZndzN0lGdzJyQT09', '2020-09-14T12:15:00+05:30', '2020-09-14T12:55:00+05:30')
    add_event('IOT Class on Zoom', 'https://us04web.zoom.us/j/79705372563?pwd=dEtRK1U1MTBUM3RzZndzN0lGdzJyQT09', '2020-09-15T14:20:00+05:30', '2020-09-15T15:00:00+05:30')
    add_event('IOT Class on Zoom', 'https://us04web.zoom.us/j/79705372563?pwd=dEtRK1U1MTBUM3RzZndzN0lGdzJyQT09', '2020-09-17T09:45:00+05:30', '2020-09-17T10:25:00+05:30')
    add_event('IOT Class on Zoom', 'https://us04web.zoom.us/j/79705372563?pwd=dEtRK1U1MTBUM3RzZndzN0lGdzJyQT09', '2020-09-18T11:30:00+05:30', '2020-09-18T12:10:00+05:30')
    print ("All zoom classes added")

    get_meeting_info()

if __name__ == '__main__':
    main()