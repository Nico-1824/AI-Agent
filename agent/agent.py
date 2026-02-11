from openai import OpenAI
import json
from dotenv import load_dotenv
from tools import get_weather, get_calendar, get_canvas_assignments

load_dotenv()

client = OpenAI()

# List of tools for model to use
tools = [
    # Tool to get weather information
    {
        "type": "function",
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

    # Tool to get calendar events
    {
        "type": "function",
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

    # Tool to get school assignments from Canvas
    {
        "type": "function",
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
]



###############################################################
#/////// FUNCTION TO CALL THE AGENT FOR A RESPONSE \\\\\\\\\\\\
###############################################################

def prompt_agent(input):
    # input list we will add to and provide to the model
    input_list = [
        {"role": "system", "content": "You are an assistant called Theios. If the user asks for data that a tool can provide, call the corresponding tool using the exact tool name."},
        {"role": "user", "content": input},
    ]


    # Agentic Loop
    response = client.responses.create(
        model="gpt-5-nano",
        tools=tools,
        input=input_list,
    )

    # Save response for input feedback
    input_list += response.output

    # Check the response for tool calls
    for item in response.output:
        if item.type == "function_call":
            if item.name == "get_weather":
                # execute tool to get the weather
                #print(f"Argument for tool {item.arguments[9:-2]}")
                print("Getting weather info...")
                weather_type, temp, wind, name = get_weather(json.loads(item.arguments)["city"])

                # add tool response to input list
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        "weather_type": weather_type,
                        "temperature": temp,
                        "wind_speed": wind,
                        "city": name,
                    })
                })
            elif item.name == "get_calendar":
                # execute the tool and get the calendar events
                print("Getting calendar info...")
                calendar_events = get_calendar(json.loads(item.arguments)["window"])

                # add tool response to input list
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        "events": calendar_events
                    })
                })
            elif item.name == "get_canvas_assignments":
                # execute the tool and get the calendar events
                print("Getting canvas assignments...")
                canvas_events = get_canvas_assignments(json.loads(item.arguments)["window"])

                # add tool response to input list
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        "assignments": canvas_events
                    })
                })

    print("Final input to model:", input_list)

    response = client.responses.create(
        model="gpt-5-nano",
        instructions="""
        You are an assistant called Theios and must summarize the information given by the tools and make it short and concise, do not ask if the user needs 
        anything more, just provide the information. You will return a response that will be displayed in a textbox and must be clean and easy to read.
        """,
        tools=tools,
        input=input_list,
    )

    # Print model output
    print(f"\n\n{response.output_text}")
    return response.output_text