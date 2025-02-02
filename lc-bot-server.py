from flask import Flask
import threading
import os
from LCBot import LCBot

app = Flask(__name__)

@app.route("/")
def home():
    return "Healthy!"

@app.route("/amihealthy")
def health_check():
    return jsonify({"status": "healthy"}), 200

def run_server():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))

if __name__ == "__main__":
    environment = os.getenv('ENVIRONMENT', 'development')
    if environment == 'production':
        threading.Thread(target=run_server).start()

    bot = LCBot()
    bot.run()
