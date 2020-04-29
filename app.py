from flask import Flask
from flask import request
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello_world():
    return 'send POST on /api/v1/forwards<br>{<br>' \
           '"channel_from_url": "https://t.me/brn_gamedev",<br>' \
           '"channel_to_url": "https://t.me/joinchat/AAAAAFbg-_q73VXqppVYrg",<br>' \
           '"words": "Арт, devtodev, 1110",<br>' \
           '"ids": [1, 2, 3],<br>' \
           '"count": 10<br>' \
           '}<br>'


@app.route('/api/v1/forwards', methods=['POST'])
def forwards():
    print('forwards')
    channel_from_url = request.json['channel_from_url']
    channel_to_url = request.json['channel_to_url']
    words = request.json['words']
    ids = request.json['ids']
    count = request.json['count']
    ws = words.split(',')

    ww = []
    for w in ws:
        ww.append(w.strip())
    with client:
        client.loop.run_until_complete(
            f(channel_from_url, channel_to_url, ww, ids, count))
    return 'Forward!'


api_id = 1358396
api_hash = '194e180caca6b9358e415bde11937e0d'
username = 'vo13crabs'
client = TelegramClient(username, api_id, api_hash)
client.start()


def good_message(message, words, sending_ids):
    for word in words:
        if word in message.message and message.id not in sending_ids:
            print(message.message)
            return True
    return False


async def dump_all_messages(channel_from, channel_to, words, sending_ids, total_count_limit):
    offset_msg = 0  # номер записи, с которой начинается считывание
    limit_msg = 100  # максимальное число записей, передаваемых за один раз
    all_messages = []  # список всех сообщений

    while True:
        history = await client(GetHistoryRequest(
            peer=channel_from,
            offset_id=offset_msg,
            offset_date=None, add_offset=0,
            limit=limit_msg, max_id=0, min_id=0,
            hash=0))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message)
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    messages = all_messages[:total_count_limit]
    for message in messages:
        if good_message(message, words, sending_ids):
            await client.forward_messages(channel_to, message.id, channel_from)


async def f(channel_from_url, channel_to_url, words, sending_ids, total_count_limit):
    channel_from = await client.get_entity(channel_from_url)
    channel_to = await client.get_entity(channel_to_url)
    await dump_all_messages(channel_from, channel_to, words, sending_ids, total_count_limit)


if __name__ == '__main__':
    app.run()