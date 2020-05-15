import json

from flask import Flask, request
from telethon.sync import TelegramClient

import ruls

with open('config.json', 'r') as file:
    data = file.read()
config = json.loads(data)

api_id = config['api_id']
api_hash = config['api_hash']
username = config['username']

client = TelegramClient(username, api_id, api_hash)
client.start()

app = Flask(__name__)


@app.route('/', methods=['POST'])
def forwards():
    return ruls.forward(client, request)


if __name__ == '__main__':
    app.run()
