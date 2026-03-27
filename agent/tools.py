import requests
from dotenv import load_dotenv
import os
import datetime
from pathlib import Path
from tzlocal import get_localzone
import json
import subprocess

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()






##########################################################################################
############################## GET WEATHER ###############################################
##########################################################################################

class WeatherFunctions:
    def get_weather(self, city):
        # use google api to get weather
        # get the long and lat of a city
        # send a get request to openweathermap api
        # returns the weather conditions, temperature, wind speed, and city
        api_key = os.getenv("OPENWEATHER_API")
        #print(f"City we are checking {city}")
        
        geocode = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={5}&appid={api_key}")
        data = geocode.json()
        lat, lon = data[0]["lat"], data[0]["lon"]

        try:
            weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric")
            weather_data = weather.json()
            weather_type, temp, wind, name = weather_data["weather"][0]["main"], weather_data["main"]["temp"], weather_data["wind"]["speed"], weather_data["name"]
            return weather_type, temp, wind, name
        except Exception as e:
            print(f"Error getting weather data: {e}")
            return "Error", "Error", "Error", "Error"











##########################################################################################
############################## SETUP CALENDAR SERVICE ##############################################
##########################################################################################

class CalenderFunctions:
    def get_calendar_service(self, readonly=False):
        SCOPES = [
            "https://www.googleapis.com/auth/calendar.readonly" if readonly
            else "https://www.googleapis.com/auth/calendar"
        ]
        BASE_DIR = Path(__file__).resolve().parents[0]
        CREDS_FILE = BASE_DIR / "credentials.json"
        TOKEN_FILE = BASE_DIR / "token.json"

        creds = None
        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)
        


    ##########################################################################################
    ############################## GET CALENDAR ##############################################
    ##########################################################################################


    def get_calendar(self, window=None):

        try:
            service = self.get_calendar_service(readonly=True)

            # Call the Calendar API
            now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            # print("Getting the upcoming 20 events")
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

        except Exception as error:
            print(f"An error occurred: {error}")










    ##########################################################################################
    ############################## PUT CALENDAR EVENTS ####################################
    ##########################################################################################

    def add_calendar_event(self, title, day, start_time, end_time, decription=None, calendarType=False):

        service = self.get_calendar_service()


        #################################################################################
        ########### USED TO FORMAT THE DATE TO FIT IN THE CALENDAR API ###########
        #################################################################################
        def format_date():
            """
            day: '2026-03-23'
            start_time: '09:00'
            end_time: '17:00'
            'start': {
                'dateTime': '2015-05-28T09:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': '2015-05-28T17:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            """
            tz = get_localzone()
            start = datetime.datetime.strptime(f"{day} {start_time}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)
            end = datetime.datetime.strptime(f"{day} {end_time}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)
            
            return {
                "start": {
                    'dateTime': start.isoformat(), 'timeZone': str(tz)
                },
                "end": {
                    'dateTime': end.isoformat(), 'timeZone': str(tz)
                }
            }
        

        ###########################
        # CONTINUE ADDING EVENT #
        ###########################
        
        times = format_date()


        new_event = {
            "summary": title,
            "description": decription,
            "start": times["start"],
            "end":times["end"],
        }

        personalCalendar = "d63a6972292ce6dc21e671bdded762b07475158b8d6d0458d02f4bff6b0cfbcf" if calendarType == False else "primary"
        event = service.events().insert(calendarId=personalCalendar, body=new_event).execute()
        print(f"Event has been created on {day} at {start_time}")
        return f"Event created on {day} at {start_time}" 










    ##########################################################################################
    ############################## FIND FREE TIME ####################################
    ##########################################################################################

    def find_free_time(self, day):
        service = self.get_calendar_service()
        events_result = (
            service.events()
            .list(
                calendarId="d63a6972292ce6dc21e671bdded762b07475158b8d6d0458d02f4bff6b0cfbcf@group.calendar.google.com",
                timeMin=day + "T00:00:00-07:00",
                timeMax=day + "T23:59:59-07:00",
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return ["Free all day"]
        
        free_time = []
        current_time = day + "T00:00:00-7:00"
        for event in events:
            # start: event["start"]["dateTime"], end: event["end"]["dateTime"]
            time_slot = (current_time, event["start"]["dateTime"])
            current_time = event["end"]["dateTime"]
            free_time.append(time_slot)

        if current_time < "T23:59:59-7:00":
            free_time.append((current_time, "T23:59:59-7:00"))

        return free_time


        


    















##########################################################################################
############################## GET CANVAS ASSIGNEMNTS ####################################
##########################################################################################
class CanvasFunctions:
    def get_canvas_assignments(self, window=None):

        CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")
        CANVAS_URL = 'https://sdsu.instructure.com/'
        USER = "140546"

        HEADERS = {"Authorization": f"Bearer {CANVAS_TOKEN}"}

        url = f"{CANVAS_URL}api/v1/users/self/courses"
        params = {
            "per_page": 100,
            "include[]": ["term", "enrollments"]
        }

        try:
            response = requests.get(url, headers=HEADERS, params=params)
            courses = response.json()

            output = []

            # getting the assignments for spring 2026
            for course in courses:
                term = course.get("term")
                if not term:
                    continue

                if term.get("name") == "Spring 2026":
                    # print(course.get("name"))
                    course_id = course.get("id")
                    assignment_url = f"{CANVAS_URL}api/v1/users/self/courses/{course_id}/assignments"
                    params = {"per_page": 100}
                    response = requests.get(assignment_url, headers=HEADERS, params=params)
                    assignments = response.json()
                    
                    if window is None:
                        window = str(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7))

                    assignments_due = []
                    for assignment in assignments:
                        if assignment["has_submitted_submissions"] != True:
                            if assignment["due_at"] and assignment["due_at"] < window:
                                # print(assignment.get("name"))
                                # add assignments for given course to an array with due date
                                assignments_due.append([assignment.get("name"), assignment.get("due_at")])
                    
                    # append to output a dictionary of the assignmetns due for each course
                    output.append({
                        "course": course.get("name"),
                        "assignments_due": assignments_due
                    })

            return output
        except Exception as e:
            print(f"Error getting canvas info {e}")
            return "Could not get canvas data" 
        




    ############################################################
    ################## GET CANVAS ANNOUNCEMENTS ################
    ############################################################
    def get_canvas_announcements(self, start_window, end_window=None):
        ##########################################
        # Format of the time: 2026-03-10T00:56:22Z
        ##########################################
        
        end_window = start_window if end_window == None else end_window

        CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")
        CANVAS_URL = 'https://sdsu.instructure.com/'
        USER = "140546"

        HEADERS = {"Authorization": f"Bearer {CANVAS_TOKEN}"}

        url = f"{CANVAS_URL}api/v1/users/self/courses"
        params = {
            "per_page": 100,
            "include[]": ["term", "enrollments"]
        }

        try:
            response = requests.get(url, headers=HEADERS, params=params)
            courses = response.json()
            # print("Got courses")

            announcements_available = []

            # getting the announcements for spring 2026
            for course in courses:
                term = course.get("term")
                if not term:
                    continue

                if term.get("name") == "Spring 2026":
                    # print(course.get("name"))
                    course_id = course.get("id")
                    announcements_url = f"{CANVAS_URL}api/v1/courses/{course_id}/discussion_topics"
                    params = {
                        "only_announcements": True,
                        "per_page": 10
                    }
                    response = requests.get(announcements_url, headers=HEADERS, params=params)
                    announcements = response.json()
                    # print(json.dumps(announcements, indent=4))
                    for item in announcements:
                        # print(item.get("posted_at"))
                        if item.get("posted_at") > start_window + "T00:00:00Z" and item.get("posted_at") < end_window + "T23:59:59Z":
                            summary = {
                                "title": item.get("title"),
                                "message": item.get("message" \
                                "")
                            }
                            announcements_available.append(summary)
            
            return announcements_available

        except Exception as e:
            print(f"FAILURE: {e}")







#######################################
############ ASSISTANT TOOLS ##########
#######################################
class AssitantTools:
    def talk(self, sentence):
        # This function will take in a sentence which will be a string and will be the method of responding to users using T2S.
        subprocess.run(["say", sentence])

    def clarify(self, question):

        # talk(question)

        response = input(question)

        return response

# print(get_calendar())
# print(get_canvas_assignments())
# print(find_free_time("2026-03-23"))
# print(add_calendar_event("Test", "2026-03-24", "12:00", "13:00", "This is a test"))
# get_canvas_announcements('2026-03-10')

# aT = AssitantTools()
# print(aT.clarify("When do you want to hangout with your friends? \n"))