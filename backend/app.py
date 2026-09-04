import os

from flask import Flask, jsonify, request
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)


client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key=os.getenv("FEATHERLESS_API_KEY")
)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Cyber-Nexus backend is running!"
    })


@app.route("/test-ai", methods=["GET"])
def test_ai():
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2",
        messages=[
            {
                "role": "user",
                "content": "Say hello to Cyber-Nexus!"
            }
        ],
        max_tokens=100
    )

    return jsonify({
        "response": response.choices[0].message.content
    })


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({
            "error": "Missing 'message' in request body"
        }), 400

    user_message = data["message"]

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2",
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ],
        max_tokens=500
    )

    return jsonify({
        "response": response.choices[0].message.content
    })



if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )