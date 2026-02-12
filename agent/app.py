from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import prompt_agent

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3001"}})
print("Flask on port 8000")

@app.route("/prompt", methods=["POST"])
def get_response():
    print("Received request")
    data = request.get_json()
    user_input = data.get("message", "")
    print(user_input)
    # print(data)
    # response = prompt_agent(user_input)
    response = "Testing"
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)