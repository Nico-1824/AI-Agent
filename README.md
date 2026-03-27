This is THEO, a personal AI voice assistant that has access to my Google Calendar, Canvas LMS to track school assignments, and a weather API. Theo's name comes from the Greek word for guide or assistant, Theois, as he is meant to help me organize myself and stay on top of my schedule.

Theo runs entirely locally on device — no internet access, no cloud models. He listens for his name as a wake word and responds to voice commands using speech-to-text and text-to-speech, making him a fully hands-free assistant. I purposely don't give Theo access to the internet so that he must use only the tools I provide and interpret the information I know the APIs return.

The agent uses a local Qwen 2.5 7B model running through Ollama to think and interpret information. Voice input is handled by faster-whisper for transcription and macOS native TTS for responses. The agentic loop is built in raw Python using a ReAct pattern — the model reasons about what tools to call, executes them, observes the results, and chains multiple tool calls together before giving a final response.

The old React/Flask/Express web interface has been replaced entirely in favor of a voice-first experience that runs as a background service on macOS.


Tech Stack:
Python
Ollama
Whisper
WakeWord
Google Calendar