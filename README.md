This is THEIOS, a personal AI Agent that has access to my calendar, canvas to see if I have assignemnts for school, and has access to a weather API. Currently these are all the tools he has access to. Theios' name comes from the Greek word for guide or assistant as he is meant to help me organize myself for the week. I purposely don't give Theios access to the internet so that he can't just get information from other sources and must use the tools I provide and interpret the information I know the APIs give him. 

The agent uses a GPT 5 nano model to "think" and interpret information. The Python script to prompt the model and run the agentic loop is connected by a Flask server that communicates with an Express server which is connected to the React webpage. The webpage is not meant to be used primarily, the next steps for this would be to implement a texting service that will give me a review of whats up for the week. The webpage is simply to clarify data such as if my recap says I have a test on X day, I might want to ask Theios if its raining that day or if other information conflicts. The webpage would be a link included in the text to ask Theios these sorts of questions. 

For future progress:
    - Building a texting service and send automated texts weekly
    - Add short term memory
    - Add a scolling, stock style, text on the webpage with weekly announcements about whats on the schedule

Tech Stack:
React
HTML
CSS
Python
Node.js
Flask
Express.js
Javascript
Docker