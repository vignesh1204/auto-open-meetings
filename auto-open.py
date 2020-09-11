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
SLEEP_WINDOW_SECS = 60 * 30
OPEN_MEETING_MINUTES_BEFORE = 0
speech_engine = pyttsx3.init()
speech_engine.setProperty('rate',150)


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
    events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=now_plus_window, maxResults=5, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    meet_link = ""
    for event in events:
        start_time = datetime.datetime.strptime(event['start'].get('dateTime', event['start'].get('date')), '%Y-%m-%dT%H:%M:%S+05:30')
        print(start_time, event['summary'])

        #checking if its cloud computing class lol
        if 'Babukarthik' in event['summary']:
            meet_link = 'https://' + event['description'].split()[-1]
            print("Google Meet Link(Babu): ", meet_link)

        #checking if Google meet link is attached
        if 'conferenceData' in event:
            if 'meet' in event['conferenceData'].get('entryPoints')[0].get('uri'):
                meet_link = event['conferenceData'].get('entryPoints')[0].get('uri')
                print("Google Meet Link(Others): ", meet_link)
        #checking if meeting is on Zoom
        elif 'description' in event and 'zoom' in event['description']:
            meet_link = event['description']
            print("Zoom Link: ", meet_link)
        
        if meet_link and is_time_in_future(start_time):
            return {
                'meet_link': meet_link,
                'start_time': start_time,
                'meeting_name': event.get('summary')
            }
        print ('\n')

def is_time_in_future(meet_start_time):
    return meet_start_time > datetime.datetime.now()

def open_meeting_in_browser(meet_link):
    print('Initiating meeting at:', meet_link)
    webbrowser.open(meet_link, new=1)

def get_time_till_next_meeting(meeting_start_time):
    if meeting_start_time:
        print ("Next meeting in : ", (meeting_start_time - datetime.datetime.now()).seconds, "seconds")
        return (meeting_start_time - datetime.datetime.now()).seconds
    return SLEEP_WINDOW_SECS + 10

def alert_on_meeting():
    #text to speech function to alert
    alert_message = "Meeting will start now! Click on join now!"
    speech_engine.say(alert_message)
    speech_engine.runAndWait()

def main():
    meeting_should_be_shown_soon = False
    meeting_link = None
    secs_till_next_meeting = SLEEP_WINDOW_SECS + 10
    meeting_name = ''

    while True:
        # showing the next meeting
        if meeting_should_be_shown_soon and meeting_link:
            open_meeting_in_browser(meeting_link)
            meeting_should_be_shown_soon = False
            meeting_link = None
            alert_on_meeting()
            meeting_name = ''
        # getting the next meeting
        else:
            meeting_details = get_meeting_info()
            if meeting_details:
                meeting_link = meeting_details.get('meet_link')
                meeting_start_time = meeting_details.get('start_time')
                meeting_name = meeting_details.get('meeting_name')
                secs_till_next_meeting = get_time_till_next_meeting(meeting_start_time)
            else:
                print ("No upcoming meetings in the given window.\nExiting application.")
                break
        if SLEEP_WINDOW_SECS > secs_till_next_meeting:
            meeting_should_be_shown_soon = True
            print ("Should be shown soon!")
        time.sleep(min(SLEEP_WINDOW_SECS, secs_till_next_meeting))


if __name__ == '__main__':
    main()