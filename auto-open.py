from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import webbrowser
import time
import pytz
import pyttsx3

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
SLEEP_WINDOW_SECS = 60 * 40
OPEN_MEETING_MINUTES_BEFORE = 0
speech_engine = pyttsx3.init()
speech_engine.setProperty('rate', 175)

class Join:
    def __init__(self, platform, username, password, url):
        opt = Options()
        opt.add_argument("--disable-infobars")
        opt.add_argument("start-maximized")
        opt.add_argument("--disable-extensions")

        #giving permission to chrome
        opt.add_experimental_option("prefs", { \
            "profile.default_content_setting_values.media_stream_mic": 1, 
            "profile.default_content_setting_values.media_stream_camera": 1, 
            "profile.default_content_setting_values.notifications": 1 
        })
        if platform == 'Meet':
            #logging into google through stack overflow
            self.driver = webdriver.Chrome(chrome_options=opt, executable_path='./chromedriver')
            self.driver.get('https://stackoverflow.com/users/signup?ssrc=head&returnurl=%2fusers%2fstory%2fcurrent%27')
            sleep(3)
            self.driver.find_element_by_xpath('//*[@id="openid-buttons"]/button[1]').click()
            self.driver.find_element_by_xpath('//input[@type="email"]').send_keys(username)
            self.driver.find_element_by_xpath('//*[@id="identifierNext"]').click()
            sleep(3)
            self.driver.find_element_by_xpath('//input[@type="password"]').send_keys(password)
            self.driver.find_element_by_xpath('//*[@id="passwordNext"]').click()
            sleep(2)
            self.driver.get(url)
            sleep(4)
            elem = self.driver.find_element_by_css_selector('body')
            #muting audio
            elem.send_keys(Keys.CONTROL + 'd')
            sleep(1)
            #muting video
            elem.send_keys(Keys.CONTROL + 'e')
            sleep(1)
            #joining
            self.driver.find_element_by_xpath('//*[@class="XCoPyb"]/div[1]').click()
            sleep(2400)
        elif platform == 'Zoom':
            self.driver = webdriver.Chrome(chrome_options=opt, executable_path='./chromedriver')
            self.driver.get(url)
            sleep(10)
            speech_engine.say("Manual operation required.")
            sleep(2400)


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

    meet_link = ''
    platform = ''
    for event in events:
        start_time = datetime.datetime.strptime(event['start'].get('dateTime', event['start'].get('date')), '%Y-%m-%dT%H:%M:%S+05:30')
        print(start_time, event['summary'])

        #checking if its test event
        if 'TestMeetingNew' in event['summary']:
            meet_link = 'https://' + event['description'].split()[-1]
            platform = 'Meet'
            print("Google Meet Link(Test): ", meet_link)

        #checking if Google meet link is attached
        if 'conferenceData' in event:
            if 'meet' in event['conferenceData'].get('entryPoints')[0].get('uri'):
                meet_link = event['conferenceData'].get('entryPoints')[0].get('uri')
                platform = 'Meet'
                print("Google Meet Link(Others): ", meet_link)
        #checking if meeting is on Zoom
        elif 'description' in event and 'zoom' in event['description']:
            meet_link = event['description']
            platform = 'Zoom'
            print("Zoom Link: ", meet_link)
        
        if meet_link and is_time_in_future(start_time):
            return {
                'meet_link': meet_link,
                'platform': platform,
                'start_time': start_time,
                'meeting_name': event.get('summary')
            }
        print ('\n')

def is_time_in_future(meet_start_time):
    return meet_start_time > datetime.datetime.now()

def open_meeting_in_browser(meet_link, platform):
    print('Initiating meeting at:', meet_link)

    #Add Gmail ID and password before running
    username = 'vignesh1999@gmail.com'
    password = 'OneTwoThree123hello'
    Join(platform, username, password, meet_link)

def get_time_till_next_meeting(meeting_start_time):
    if meeting_start_time:
        print ("Next meeting in : ", (meeting_start_time - datetime.datetime.now()).seconds, "seconds")
        return (meeting_start_time - datetime.datetime.now()).seconds
    return SLEEP_WINDOW_SECS + 10

def alert_on_meeting():
    #text to speech function to alert
    alert_message = "Meeting will start now!"
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
            alert_on_meeting()
            open_meeting_in_browser(meeting_link, meeting_platform)
            meeting_should_be_shown_soon = False
            meeting_link = None
            meeting_name = ''
        # getting the next meeting
        else:
            meeting_details = get_meeting_info()
            if meeting_details:
                meeting_link = meeting_details.get('meet_link')
                meeting_start_time = meeting_details.get('start_time')
                meeting_name = meeting_details.get('meeting_name')
                meeting_platform = meeting_details.get('platform')
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