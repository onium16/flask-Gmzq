import os
from flask import Flask, Response
from bot import start_repost_bot
import threading

app = Flask(__name__)

BOT_TOKEN = os.environ.get('TOKEN') 

@app.route("/")
def hello():
    # return Response('<h1>Hello, this is Telegram Bot!</h1>', mimetype='text/html')
    return f'{BOT_TOKEN}'

@app.route("/start_bot", methods=["GET"])
def start_bot():
    # Running a bot in a separate thread
    bot_thread = threading.Thread(target=start_repost_bot)
    print('Start checking')
    bot_thread.start()

    return Response('<h1>Bot started successfully!</h1>', mimetype='text/html')

if __name__ == "__main__":
    app.run()
