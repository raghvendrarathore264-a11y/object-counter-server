from flask import Flask, request, jsonify

app = Flask(__name__)

count = 0

@app.route("/")
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Object Counter</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 80px;
            }}

            h1 {{
                font-size: 32px;
            }}

            .count {{
                font-size: 80px;
                font-weight: bold;
            }}
        </style>
    </head>

    <body>

        <h1>📦 Object Counter</h1>

        <div class="count">{count}</div>

        <p>Objects Detected</p>

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
