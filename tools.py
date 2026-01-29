import requests
from dotenv import load_dotenv
import os
import datetime
import os.path
from bs4 import BeautifulSoup
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_weather(city):
    # use google api to get weather
    # get the long and lat of a city
    # send a get request to openweathermap api
    # returns the weather conditions, temperature, wind speed, and city
    load_dotenv()
    api_key = os.getenv("OPENWEATHER_API")
    #print(f"City we are checking {city}")
    
    geocode = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={5}&appid={api_key}")
    data = geocode.json()
    lat, lon = data[0]["lat"], data[0]["lon"]

    weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric")
    weather_data = weather.json()
    weather_type, temp, wind, name = weather_data["weather"][0]["main"], weather_data["main"]["temp"], weather_data["wind"]["speed"], weather_data["name"]
    return weather_type, temp, wind, name

def get_calendar(window=None):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        print("Getting the upcoming 20 events")
        events_result = (
            service.events()
            .list(
                calendarId="d63a6972292ce6dc21e671bdded762b07475158b8d6d0458d02f4bff6b0cfbcf@group.calendar.google.com",
                timeMin=now,
                timeMax=window,
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 20 events
        calendarSummary = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            calendarSummary.append([event["summary"], start])

        return calendarSummary

    except HttpError as error:
        print(f"An error occurred: {error}")


def get_canvas_assignments():

    load_dotenv()

    CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")
    CANVAS_URL = 'https://sdsu.instructure.com/'
    USER = "140546"

    HEADERS = {"Authorization": f"Bearer {CANVAS_TOKEN}"}

    url = f"{CANVAS_URL}api/v1/users/self/courses"
    params = {
        "per_page": 100,
        "include[]": ["term", "enrollments"]
    }
    response = requests.get(url, headers=HEADERS, params=params)
    courses = response.json()
    
    epoch = 0
    for course in courses:
        term = course.get("term")
        if not term:
            continue

        if term.get("name") == "Spring 2026":
            epoch += 1
            print(course.get("name"))
            course_id = course.get("id")
            assignment_url = f"{CANVAS_URL}api/v1/users/self/courses/{course_id}/assignments"
            params = {"per_page": 100}
            response = requests.get(assignment_url, headers=HEADERS, params=params)
            assignments = response.json()
            for assignment in assignments:
                if assignment["has_submitted_submissions"] == True:
                    print(assignment["name"])

            if epoch >= 2:
                return


# print(get_calendar())
get_canvas_assignments()