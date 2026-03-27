# List of tools for model to use
tools = [
    # Tool to get weather information
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather conditions such as sky conditions, temperature, and wind speed for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city we want to check the weather for."
                    },
                },
                "required": ["city"],
            },
        },
    },



    # TOOLS FOR CALENDAR ACTIONS
    {
        "type": "function",
        "function": {
            "name": "get_calendar",
            "description": "Get the first 20 events from the user's Google Calendar for the current week and will return the event name, date, and start time, if it has a start time, in a list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "window": {
                        "type": "string",
                        "description": """
                        The time window for which to retrieve calendar events, formatted as an ISO 8601 timestamp. For example, '2026-01-31T23:59:59Z' to 
                        get events up to January 31, 2026. If the user does not provide a window, do not pass this parameter. If the user for example wants
                        events for the week, calculate the end of the week from the current date and provide the timestamp in ISO 8601 format. 
                        """,
                    }

                },
                "additionalProperties": False
            },
        },
    },
    # def add_calendar_event(title, day, start_time, end_time, decription, location=None, calendarType=False):
    {
        "type": "function",
        "function": {
            "name": "add_calendar_event",
            "description": 
            """
            This function will create an event on my calendar. 
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": """
                        Title of the event.
                        """,
                    },
                    "day": {
                        "type": "string",
                        "description": """
                        The day the event will take place in YYYY-MM-DD format.
                        """,
                    },
                    "start_time": {
                        "type": "string",
                        "description": """
                        The time the event starts in HH:MM format.
                        """,
                    },
                    "end_time": {
                        "type": "string",
                        "description": """
                        The time the event ends in HH:MM format.
                        """,
                    },
                    "description": {
                        "type": "string",
                        "description": """
                        A description of the event.
                        """,
                    },"calendarType": {
                        "type": "bool",
                        "description": """
                        If the user says to use their private calendar set the bool parameter to True. Otherwise leave empty.
                        """,
                    }

                },
                "additionalProperties": False
            },
        },
    },
    # def find_free_time(day):
    {
        # def add_calendar_event(title, day, start_time, end_time, decription, location=None, calendarType=False):
        "type": "function",
        "function": {
            "name": "find_free_time",
            "description": 
            """
            This function will return an array of tuples that are ranges of free time during a day.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": """
                        This parameter is the day we want to check if we have free time in YYYY-MM-DD format.
                        """,
                    },

                },
                "additionalProperties": False
            },
        },
    },



    # TOOLS FOR CANVAS
    {
        "type": "function",
        "function": {
            "name": "get_canvas_assignments",
            "description": """
            Get a list of courses and the assignments that are due within the given time window from the user's Canvas account. The assignments will only
            be included if they are not yet submitted. The function returns a list of dictionaries, each has the course name and the given assignments
            due within the window.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "window": {
                        "type": "string",
                        "description": """
                        The window parameter a datetime formatted timestamp representing the end of the time window. For example, if today is
                        January 31, 2026 and the user wants assignemnts due in the next two weeks, the window parameter would be '2026-02-14 23:59:59.441012+00:00'.
                        If no window is provided, it will be default get assignments due within the next 7 days. If the user does not specify a window, do not pass one.
                        """
                    },
                },
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_canvas_announcements",
            "description": """
            This function will get any announcements made within the window time. It will return an array of dictionaries with the title and message
            of announcements.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "start_window": {
                        "type": "string",
                        "description": """
                        The start_window parameter needs to be in YYYY-MM-DD. This parameter is required and if no window space is specificed then 
                        use the current day.
                        """
                    },
                    "end_window": {
                        "type": "string",
                        "description": """
                        The start_window parameter needs to be in YYYY-MM-DD. This parameter is not required but if a range of days such as 'this week'
                        then provide the parameter a week ahead of the start_window.
                        """
                    },
                },
                "additionalProperties": False
            },
        },
    },
]