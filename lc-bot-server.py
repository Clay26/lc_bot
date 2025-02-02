from flask import Flask, jsonify
from LCBot import LCBot
import threading
import os

app = Flask(__name__)

def get_version():
    try:
        with open("VERSION", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"

VERSION = get_version()

@app.route("/")
def home():
    return "Healthy!"

@app.route("/amihealthy")
def health_check():
    return jsonify({"status": "healthy", "version": VERSION}), 200

def run_server():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))

if __name__ == "__main__":
    environment = os.getenv('ENVIRONMENT', 'development')
    if environment == 'production':
        threading.Thread(target=run_server).start()

    # Run bot
    bot = LCBot()
    bot.run()
