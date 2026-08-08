from flask import Flask, request, jsonify
import os

app = Flask(__name__)

count = 0


@app.route("/")
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="refresh" content="5">

        <title>Object Counter</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 80px;
                background: #f5f5f5;
            }}

            h1 {{
                font-size: 32px;
            }}

            .count {{
                font-size: 90px;
                font-weight: bold;
                margin: 30px;
            }}

            .status {{
                font-size: 20px;
            }}
        </style>
    </head>

    <body>

        <h1>📦 Object Counter</h1>

        <div class="count">{count}</div>

        <p class="status">Objects Detected</p>

    </body>
    </html>
    """


@app.route("/update", methods=["POST"])
def update():
    global count

    data = request.get_json()

    if data and "count" in data:
        count = data["count"]

    return jsonify({
        "status": "success",
        "count": count
    })


@app.route("/count", methods=["GET"])
def get_count():
    return jsonify({
        "count": count
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
