# auto-join-meetings

Only works in Python2 and Google Chrome.

Calendar events must have attached Google Meet link or Zoom link as description of event.

## Enable google calendar api

Follow the steps in this link to enable Google Calendar API - https://developers.google.com/calendar/quickstart/python

Copy credentials.json into the directory where this repo has been cloned.

## Install dependencies

```pip install -r dependencies.txt```

Download required chromedriver version from https://chromedriver.chromium.org/ and move it to the working directory.

Before running script, make sure Gmail account details have been added in auto-open.py lines 160 and 161.

## Running the script

```python auto-open.py```
