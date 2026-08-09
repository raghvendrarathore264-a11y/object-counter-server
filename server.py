from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

# -----------------------------
# Supabase configuration
# -----------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

TABLE_URL = f"{SUPABASE_URL}/rest/v1/daily_counts"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Current count received from ESP8266
current_count = 0


# -----------------------------
# Get today's date
# India timezone
# -----------------------------
def today():
    return datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()


# -----------------------------
# Save today's count
# -----------------------------
def save_daily_count(new_count):

    date_today = today()

    try:
        # Check if today's record already exists
        response = requests.get(
            TABLE_URL,
            headers=HEADERS,
            params={
                "date": f"eq.{date_today}",
                "select": "id,date,count"
            },
            timeout=10
        )

        if response.status_code != 200:
            print("Supabase GET error:", response.text)
            return False

        records = response.json()

        # If today's record exists
        if records:

            record_id = records[0]["id"]
            old_count = records[0]["count"]

            # Keep the highest count received today
            final_count = max(old_count, new_count)

            update_response = requests.patch(
                TABLE_URL,
                headers=HEADERS,
                params={
                    "id": f"eq.{record_id}"
                },
                json={
                    "count": final_count
                },
                timeout=10
            )

            print("Supabase update:", update_response.status_code)

        # If today's record doesn't exist
        else:

            insert_response = requests.post(
                TABLE_URL,
                headers=HEADERS,
                json={
                    "date": date_today,
                    "count": new_count
                },
                timeout=10
            )

            print("Supabase insert:", insert_response.status_code)

        return True

    except Exception as e:
        print("Supabase error:", e)
        return False


# -----------------------------
# Main dashboard
# -----------------------------
@app.route("/")
def home():

    date_today = today()

    # Get history
    history = []

    try:
        response = requests.get(
            TABLE_URL,
            headers=HEADERS,
            params={
                "select": "date,count",
                "order": "date.desc",
                "limit": 30
            },
            timeout=10
        )

        if response.status_code == 200:
            history = response.json()

    except Exception as e:
        print("History error:", e)

    history_html = ""

    for row in history:

        history_html += f"""
        <tr>
            <td>{row["date"]}</td>
            <td>{row["count"]}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta name="viewport"
              content="width=device-width, initial-scale=1">

        <meta http-equiv="refresh" content="5">

        <title>Object Counter</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                text-align: center;
                margin: 0;
                padding: 25px;
            }}

            .container {{
                max-width: 600px;
                margin: auto;
            }}

            .card {{
                background: white;
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}

            h1 {{
                font-size: 30px;
            }}

            .count {{
                font-size: 90px;
                font-weight: bold;
                margin: 20px;
            }}

            .today {{
                font-size: 18px;
                color: #666;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}

            th, td {{
                padding: 14px;
                border-bottom: 1px solid #ddd;
                font-size: 18px;
            }}

            th {{
                background: #eee;
            }}

            .status {{
                color: green;
                font-weight: bold;
            }}

        </style>

    </head>

    <body>

        <div class="container">

            <div class="card">

                <h1>📦 Object Counter</h1>

                <div class="count">
                    {current_count}
                </div>

                <div class="today">
                    Today's current count
                </div>

                <p class="status">
                    🟢 System Active
                </p>

            </div>


            <div class="card">

                <h2>📅 Counting History</h2>

                <table>

                    <tr>
                        <th>Date</th>
                        <th>Objects</th>
                    </tr>

                    {history_html}

                </table>

            </div>

        </div>

    </body>

    </html>
    """


# -----------------------------
# ESP8266 sends count here
# -----------------------------
@app.route("/update", methods=["POST"])
def update():

    global current_count

    data = request.get_json()

    if not data or "count" not in data:
        return jsonify({
            "status": "error",
            "message": "Count not provided"
        }), 400

    current_count = int(data["count"])

    print("Received count:", current_count)

    # Save to Supabase
    save_daily_count(current_count)

    return jsonify({
        "status": "success",
        "count": current_count
    })


# -----------------------------
# Get current count
# -----------------------------
@app.route("/count", methods=["GET"])
def get_count():

    return jsonify({
        "count": current_count
    })


# -----------------------------
# Start server
# -----------------------------
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
