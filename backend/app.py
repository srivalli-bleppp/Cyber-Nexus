import os
import sqlite3
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

# Database setup
DATABASE = "cybernexus.db"


def init_db():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            analysis TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


init_db()


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
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    if not data or "event" not in data:
        return jsonify({
            "error": "Missing 'event' in request body"
        }), 400

    security_event = data["event"]

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a cybersecurity analysis assistant for Cyber-Nexus. "
                    "Analyze the security event provided by the user. "
                    "Return your answer using exactly this format:\n\n"
                    "Threat Level: LOW, MEDIUM, HIGH, or CRITICAL\n"
                    "Confidence: a number between 0 and 1\n"
                    "Indicators: a short list of suspicious indicators\n"
                    "Recommendation: a practical defensive action\n\n"
                    "Keep the response concise and defensive. "
                    "Do not provide instructions for carrying out attacks."
                )
            },
            {
                "role": "user",
                "content": security_event
            }
        ],
        max_tokens=300
    )

    ai_result = response.choices[0].message.content

    # Save the event and analysis to the database
    connection = sqlite3.connect(DATABASE)

    connection.execute(
        """
        INSERT INTO security_events (event, analysis)
        VALUES (?, ?)
        """,
        (security_event, ai_result)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "event": security_event,
        "analysis": ai_result
    })
@app.route("/events", methods=["GET"])
def get_events():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    events = connection.execute(
        """
        SELECT id, event, analysis, created_at
        FROM security_events
        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return jsonify([
        dict(event) for event in events
    ])

@app.route("/stats", methods=["GET"])
def get_stats():
    connection = sqlite3.connect(DATABASE)

    total_events = connection.execute(
        "SELECT COUNT(*) FROM security_events"
    ).fetchone()[0]

    medium_events = connection.execute(
        "SELECT COUNT(*) FROM security_events WHERE analysis LIKE '%MEDIUM%'"
    ).fetchone()[0]

    high_events = connection.execute(
        "SELECT COUNT(*) FROM security_events WHERE analysis LIKE '%HIGH%'"
    ).fetchone()[0]

    critical_events = connection.execute(
        "SELECT COUNT(*) FROM security_events WHERE analysis LIKE '%CRITICAL%'"
    ).fetchone()[0]

    low_events = connection.execute(
        "SELECT COUNT(*) FROM security_events WHERE analysis LIKE '%LOW%'"
    ).fetchone()[0]

    connection.close()

    return jsonify({
        "total_events": total_events,
        "low": low_events,
        "medium": medium_events,
        "high": high_events,
        "critical": critical_events
    })

if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )