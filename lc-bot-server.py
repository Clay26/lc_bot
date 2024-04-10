from flask import Flask
import threading
import os
from LCBot import LCBot

app = Flask(__name__)

@app.route("/")
def home():
    return "Healthy!"

def run_server():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))

if __name__ == "__main__":
    threading.Thread(target=run_server).start()
    bot = LCBot()
    bot.run()
