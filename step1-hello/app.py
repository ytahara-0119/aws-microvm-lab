import logging
from flask import Flask, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def hello():
    app.logger.info("Hello endpoint called")
    return jsonify(message="Hello MicroVM!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
