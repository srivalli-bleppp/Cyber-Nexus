import os
import uuid

from flask import Flask, jsonify, request
from dotenv import load_dotenv
from openai import OpenAI

from backend.database import get_connection


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




@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    if not data or "event" not in data or "user_id" not in data:
        return jsonify({
            "error": "Missing 'event' or 'user_id' in request body"
        }), 400

    security_event = data["event"]
    user_id = data["user_id"]

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

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO security_events
        (user_id, event, analysis)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            security_event,
            ai_result
        )
    )

    connection.commit()
    connection.close()

    return jsonify({
        "event": security_event,
        "analysis": ai_result
    })



@app.route("/events", methods=["GET"])
def get_events():

    connection = get_connection()

    events = connection.execute(
        """
        SELECT
            security_events.id,
            security_events.user_id,
            users.username,
            users.role,
            security_events.event,
            security_events.analysis,
            security_events.created_at
        FROM security_events
        LEFT JOIN users
            ON security_events.user_id = users.user_id
        ORDER BY security_events.created_at DESC
        """
    ).fetchall()

    connection.close()

    return jsonify([
        dict(event)
        for event in events
    ])



@app.route("/users/<user_id>/events", methods=["GET"])
def get_user_events(user_id):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT
            user_id,
            username,
            role,
            status
        FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    if not user:
        connection.close()

        return jsonify({
            "error": "User not found"
        }), 404

    events = connection.execute(
        """
        SELECT
            id,
            user_id,
            event,
            analysis,
            created_at
        FROM security_events
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return jsonify({
        "user": dict(user),
        "events": [
            dict(event)
            for event in events
        ]
    })



@app.route("/stats", methods=["GET"])
def get_stats():

    connection = get_connection()

    total_events = connection.execute(
        "SELECT COUNT(*) FROM security_events"
    ).fetchone()[0]

    medium_events = connection.execute(
        """
        SELECT COUNT(*)
        FROM security_events
        WHERE analysis LIKE '%MEDIUM%'
        """
    ).fetchone()[0]

    high_events = connection.execute(
        """
        SELECT COUNT(*)
        FROM security_events
        WHERE analysis LIKE '%HIGH%'
        """
    ).fetchone()[0]

    critical_events = connection.execute(
        """
        SELECT COUNT(*)
        FROM security_events
        WHERE analysis LIKE '%CRITICAL%'
        """
    ).fetchone()[0]

    low_events = connection.execute(
        """
        SELECT COUNT(*)
        FROM security_events
        WHERE analysis LIKE '%LOW%'
        """
    ).fetchone()[0]

    connection.close()

    return jsonify({
        "total_events": total_events,
        "low": low_events,
        "medium": medium_events,
        "high": high_events,
        "critical": critical_events
    })



@app.route("/users", methods=["GET"])
def get_users():

    connection = get_connection()

    users = connection.execute(
        """
        SELECT
            user_id,
            username,
            role,
            status
        FROM users
        """
    ).fetchall()

    connection.close()

    return jsonify([
        dict(user)
        for user in users
    ])



@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data or "username" not in data:
        return jsonify({
            "error": "Username is required"
        }), 400

    username = data["username"]

    connection = get_connection()

    user = connection.execute(
        """
        SELECT
            user_id,
            username,
            role,
            status
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    connection.close()

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    if user["status"] != "active":
        return jsonify({
            "error": "User is inactive"
        }), 403

    return jsonify({
        "message": "Login successful",
        "user": dict(user)
    })



@app.route("/investigate/<user_id>", methods=["POST"])
def investigate(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, username, role, status FROM users WHERE user_id = ?",
        (user_id,)
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    cursor.execute(
        """
        SELECT id, user_id, event, analysis, created_at
        FROM security_events
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    events = cursor.fetchall()

    risk_score = 0

    for event in events:
        analysis = (event["analysis"] or "").upper()

        if "CRITICAL" in analysis:
            risk_score += 40
        elif "HIGH" in analysis:
            risk_score += 30
        elif "MEDIUM" in analysis:
            risk_score += 20
        elif "LOW" in analysis:
            risk_score += 5

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        severity = "CRITICAL"
    elif risk_score >= 45:
        severity = "HIGH"
    elif risk_score >= 20:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    incident_id = "INC-" + uuid.uuid4().hex[:8].upper()

    cursor.execute(
        """
        INSERT INTO incidents
        (incident_id, user_id, risk_score, severity, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (incident_id, user_id, risk_score, severity, "OPEN")
    )

    conn.commit()
    conn.close()

    return jsonify({
        "incident_id": incident_id,
        "user_id": user_id,
        "risk_score": risk_score,
        "severity": severity,
        "status": "OPEN",
        "event_count": len(events)
    }), 201


@app.route("/incidents", methods=["GET"])
def get_incidents():

    connection = get_connection()

    incidents = connection.execute(
        """
        SELECT
            incidents.incident_id,
            incidents.user_id,
            users.username,
            users.role,
            incidents.risk_score,
            incidents.severity,
            incidents.status
        FROM incidents
        LEFT JOIN users
            ON incidents.user_id = users.user_id
        ORDER BY incidents.rowid DESC
        """
    ).fetchall()

    connection.close()

    return jsonify([
        dict(incident)
        for incident in incidents
    ])



@app.route("/incidents/<incident_id>", methods=["GET"])
def get_incident(incident_id):

    connection = get_connection()


    incident = connection.execute(
        """
        SELECT
            incidents.incident_id,
            incidents.user_id,
            incidents.risk_score,
            incidents.severity,
            incidents.status,

            users.username,
            users.role,
            users.status AS user_status

        FROM incidents

        LEFT JOIN users
            ON incidents.user_id = users.user_id

        WHERE incidents.incident_id = ?
        """,
        (incident_id,)
    ).fetchone()

    if not incident:
        connection.close()

        return jsonify({
            "error": "Incident not found"
        }), 404

    incident = dict(incident)


    events = connection.execute(
        """
        SELECT
            id,
            user_id,
            event,
            analysis,
            created_at
        FROM security_events
        WHERE user_id = ?
        ORDER BY created_at ASC
        """,
        (incident["user_id"],)
    ).fetchall()

    events = [
        dict(event)
        for event in events
    ]

    connection.close()


    ai_analysis = []

    for event in events:

        ai_analysis.append({
            "event_id": event["id"],
            "analysis": event["analysis"],
            "created_at": event["created_at"]
        })


    return jsonify({

        "incident": {
            "incident_id": incident["incident_id"],
            "status": incident["status"]
        },

        "user": {
            "user_id": incident["user_id"],
            "username": incident["username"],
            "role": incident["role"],
            "status": incident["user_status"]
        },

        "risk": {
            "score": incident["risk_score"],
            "level": incident["severity"]
        },

        "severity": {
            "level": incident["severity"]
        },

        "events": events,

        "ai_analysis": ai_analysis
    })



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        debug=True,
        port=8000
    )