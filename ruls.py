import logging
import time

import requests
from telethon.tl.functions.messages import GetHistoryRequest

from Order import Order

logging.basicConfig(
    filename='logs.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s | %(message)s',
    datefmt='%d.%m.%Y %I:%M:%S %p')


def start():
    print("Hello, i'm aggnews from 3CRABS")
    logging.info("Hello, i'm aggnews from 3CRABS")


def forward(client, request):
    order = Order(request)
    logging.info(f'Пришел запрос на from:{order.channel_from_url} to:{order.channel_to_url} words:{order.words}')
    with client:
        client.loop.run_until_complete(forward_order(client, order))
    return 'Forward!'


channels_cache = {}


async def forward_order(client, order):
    logging.info(f'Запрос {order.channel_from_url}')
    if order.channel_from_url in channels_cache:
        channel_from = channels_cache[order.channel_from_url]
    else:
        channel_from = await client.get_entity(order.channel_from_url)
        channels_cache[order.channel_from_url] = channel_from
        logging.info(f'{order.channel_from_url} добавлена в кэш')

    logging.info(f'Запрос {order.channel_to_url}')
    if order.channel_to_url in channels_cache:
        channel_to = channels_cache[order.channel_to_url]
    else:
        channel_to = await client.get_entity(order.channel_to_url)
        channels_cache[order.channel_to_url] = channel_to
        logging.info(f'{order.channel_to_url} добавлена в кэш')

    await forward_all_messages(client, order, channel_from, channel_to)


def is_good_message(message, words, sending_ids):
    for word in words:
        if (word in str.lower(message.message)) and (message.id not in sending_ids):
            return True
    return False


async def forward_all_messages(client, order, channel_from, channel_to):
    offset_msg = 0
    limit_msg = 10

    history = await client(GetHistoryRequest(
        peer=channel_from,
        offset_id=offset_msg,
        offset_date=None,
        add_offset=0,
        limit=limit_msg,
        max_id=0,
        min_id=0,
        hash=0))

    messages = history.messages
    logging.info(f'Получено {len(messages)} сообщений')

    forward_messages = []
    for message in messages:
        if is_good_message(message, order.words, order.ids):
            forward_messages.append({
                "channel_from": order.channel_from_url,
                "channel_to": order.channel_to_url,
                "id": message.id
            })
            time.sleep(10)
            try:
                await client.forward_messages(channel_to, message.id, channel_from)
                logging.info(f'Пересылка from:{channel_from} to:{channel_to} id:{message.id} прошла успешно')
            except Exception as e:
                logging.error(f'Переслать from:{channel_from} to:{channel_to} id:{message.id} не удалось\ne:{e}')

    url = 'http://localhost:3000/api/message'
    try:
        if forward_messages:
            m = {"messages": forward_messages}
            requests.post(
                url,
                json=m,
                headers={"Secret": "88ec724d-5822-44df-a747-9b282492d63f"})
            logging.info(f'Отправка {m} на {url} прошла успешно')
        else:
            logging.info(f'Отправлять нечего')
    except Exception as e:
        logging.error(f'{url} не отвечает e:{e}')
        exit(1)
