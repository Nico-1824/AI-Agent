import json
from tools import WeatherFunctions, CalenderFunctions, CanvasFunctions, AssitantTools
from ollama import chat
from tool_list import tools
from datetime import *
import sys
sys.stdout.reconfigure(line_buffering=True)

weather_functions, calender_functions, canvas_functions, assitant_tools = WeatherFunctions(), CalenderFunctions(), CanvasFunctions(), AssitantTools()







###############################################################
#/////// FUNCTION TO CALL THE AGENT FOR A RESPONSE \\\\\\\\\\\\
###############################################################

def prompt_agent(input):
    # input list we will add to and provide to the model

    today = datetime.now().strftime("%Y-%m-%d")

    input_list = [

        {"role": "system", 
         "content": f"""
         You are an assistant called Theo. If the user asks for data that a tool can provide, call the corresponding tool using the exact tool name. 
         If you do not have a tool to do a task, do all the tasks you are able to and then at the end say which you can't preform. For context today's
         date is {today}.
         """},
        {"role": "user", "content": input},
    ]


    # Agentic Loop
    # 1. User asks question
    # 2. Model responds with tool calls
    # 3. You execute the tools, add results to input_list
    # 4. Call model AGAIN with updated input_list
    # 5. Model either calls more tools OR gives final answer
    # 6. Repeat until no more tool calls

    response = chat(
        model='qwen2.5:7b',
        messages=input_list,
        tools=tools,
    )

    # Save response for input feedback
    input_list.append({"role": "assistant", "content": response.message.content})

    # Check the response for tool calls

    while response.message.tool_calls:
        print(response.message.tool_calls)
        for tool_call in response.message.tool_calls:

            if tool_call.function.name == "get_weather":
                # execute tool to get the weather
                #print(f"Argument for tool {item.arguments[9:-2]}")
                print("Getting weather info...")
                weather_type, temp, wind, name = weather_functions.get_weather(tool_call.function.arguments["city"])

                # add tool response to input list
                input_list.append({
                    "role": "tool",
                    "content": json.dumps({
                        "weather_type": weather_type,
                        "temperature": temp,
                        "wind_speed": wind,
                        "city": name,
                    })
                })
            elif tool_call.function.name == "get_calendar":
                # execute the tool and get the calendar events
                print("Getting calendar info...")
                calendar_events = calender_functions.get_calendar(tool_call.function.arguments["window"])

                # add tool response to input list
                input_list.append({
                    "role": "tool",
                    "content": json.dumps({
                        "events": calendar_events
                    })
                })
            elif tool_call.function.name == "add_calendar_event":

                print("Adding to calendar")
                # def add_calendar_event(title, day, start_time, end_time, decription, calendarType=False)
                title = tool_call.function.arguments["title"]
                day = tool_call.function.arguments["day"]
                start_time = tool_call.function.arguments["start_time"]
                end_time = tool_call.function.arguments["end_time"]
                description = tool_call.function.arguments.get("description")
                calendarType = tool_call.function.arguments.get("calendarType")

                calendar_status = calender_functions.add_calendar_event(title, day, start_time, end_time, description, calendarType)

                input_list.append({
                    "role": "tool",
                    "content": json.dumps(calendar_status)
                })

            elif tool_call.function.name == "find_free_time":

                print("Finding Free Time")
                free_time = calender_functions.find_free_time(tool_call.function.arguments["day"])

                input_list.append({
                    "role": "tool",
                    "content": json.dumps(free_time)
                })

            elif tool_call.function.name == "get_canvas_assignments":
                # execute the tool and get the calendar events
                print("Getting canvas assignments...")
                canvas_events = canvas_functions.get_canvas_assignments(tool_call.function.arguments["window"])

                # add tool response to input list
                input_list.append({
                    "role": "tool",
                    "content": json.dumps({
                        "assignments": json.dumps(canvas_events)
                    })
                })

            elif tool_call.function.name == "get_canvas_announcements":
                print("Getting announcements")
                end_window = tool_call.function.arguments.get("end_window")
                canvas_announcements = canvas_functions.get_canvas_announcements(tool_call.function.arguments["start_window"], end_window)

                input_list.append({
                    "role": "tool",
                    "content": json.dumps({
                        "announcements": json.dumps(canvas_announcements)
                    })
                })

        # Check again if any tools need to be called again (Tool chaining)
        print("Calling model again with: ", input_list)
        response = chat(
            model='qwen2.5:7b',
            messages=input_list,
            tools=tools,
        )

    input_list.append({"role": "system", "content": "Summarize what you did in one short conversational sentence, as if you are speaking out loud. No quotes, no labels, no markdown."})
    print("Final input to model:", input_list)

    response = chat(
        model='qwen2.5:7b',
        messages=input_list
    )

    # Print model output
    print(f"\n\n{response.message.content}")
    assitant_tools.talk(response_text)
    return




from pvrecorder import PvRecorder
from faster_whisper import WhisperModel
import wave, struct, tempfile, os

whisper = WhisperModel("tiny", device="cpu", compute_type="int8")


def listen_for_wake_word(wake_word="theo", chunk_duration=3):
    """Record in chunks and check for wake word using Whisper."""
    recorder = PvRecorder(device_index=-1, frame_length=512)
    recorder.start() #turns on the mic to record
    print(f"Listening for wake word: '{wake_word}'...")

    while True:
        # Record a short chunk
        frames = []
        for _ in range(0, int(16000 / 512 * chunk_duration)):
            frames.append(recorder.read())

        # Save chunk to temp file
        tmp = tempfile.mktemp(suffix=".wav")
        with wave.open(tmp, "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(16000)
            f.writeframes(struct.pack("h" * len(frames) * 512, *[s for frame in frames for s in frame]))

        # Transcribe chunk
        segments, _ = whisper.transcribe(tmp, beam_size=1)
        text = " ".join([s.text for s in segments]).strip().lower()
        os.remove(tmp)

        if wake_word in text:
            print(f"Wake word detected! Heard: '{text}'")
            assitant_tools.talk("Yes sir?")
            recorder.stop()
            recorder.delete()

            audio_path = record_command()
            command = transcribe(audio_path)
            print(f"Command input: {command}")
            assitant_tools.talk("Checking sir")
            prompt_agent(command)

            # check for more commands
            while True:
                assitant_tools.talk("Anything else Sir?")
                audio_path = record_command(silence_duration=3)
                command = transcribe(audio_path)
                print(f"Command input: {command}")
                if not command.strip():
                    print("No more commands")
                    break
                assitant_tools.talk("Checking sir")
                prompt_agent(command)
            
            print("Listening for waking word again...")
            recorder = PvRecorder(device_index=-1, frame_length=512)
            recorder.start()
        
import webrtcvad

def record_command(sample_rate=16000, silence_duration=1.5):
    """Record until user stops talking."""
    vad = webrtcvad.Vad(2)  # aggressiveness 0-3, higher = less sensitive
    recorder = PvRecorder(device_index=-1, frame_length=480)
    recorder.start()

    print("Speak your command...")

    frames = []
    silent_frames = 0
    speaking = False

    # How many silent frames = end of speech
    max_silent_frames = int(silence_duration * sample_rate / 480)

    while True:
        pcm = recorder.read()
        raw = struct.pack("h" * len(pcm), *pcm)

        is_speech = vad.is_speech(raw, sample_rate)

        if is_speech:
            speaking = True
            silent_frames = 0
            frames.append(raw)
        elif speaking:
            # Was speaking, now silent
            silent_frames += 1
            frames.append(raw)  # keep silence frames so audio isn't cut abruptly

            if silent_frames > max_silent_frames:
                print("Done listening.")
                break

    recorder.stop()
    recorder.delete()

    # Save to temp wav
    tmp = tempfile.mktemp(suffix=".wav")
    with wave.open(tmp, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(b"".join(frames))

    return tmp

def transcribe(audio_path):
    segments, _ = whisper.transcribe(audio_path, beam_size=5)
    text = " ".join([s.text for s in segments])
    os.remove(audio_path)  # cleanup temp file
    return text.strip()


if (__name__ == "__main__"):
    listen_for_wake_word()