import time

import requests
from telethon.tl.functions.messages import GetHistoryRequest

from Order import Order


def forward(client, request):
    order = Order(request)
    with client:
        client.loop.run_until_complete(forward_order(client, order))
    return 'Forward!'


async def forward_order(client, order):
    channel_from = get_channel_by_url(order.channel_from_url, client)
    channel_to = get_channel_by_url(order.channel_to_url, client)
    await forward_all_messages(client, order, channel_from, channel_to)


def get_channel_by_url(url, client):
    # todo кэш
    return await client.get_entity(url)


def is_good_message(message, words, sending_ids):
    for word in words:
        if (word in str.lower(message.message)) and (message.id not in sending_ids):
            return True
    return False


async def forward_all_messages(client, order, channel_from, channel_to):
    offset_msg = 0
    limit_msg = 10

    history = await client(
        GetHistoryRequest(
            peer=channel_from,
            offset_id=offset_msg,
            offset_date=None,
            add_offset=0,
            limit=limit_msg,
            max_id=0,
            min_id=0,
            hash=0
        )
    )

    messages = history.messages
    forward_messages = []

    for message in messages:
        if is_good_message(message, order.words, order.sending_ids):
            forward_messages.append({
                "channel_from": order.channel_from_url,
                "channel_to": order.channel_to_url,
                "id": message.id
            })
            time.sleep(10)
            await client.forward_messages(channel_to, message.id, channel_from)

    try:
        m = {"messages": forward_messages}
        requests.post("http://9f7aadf2.ngrok.io/api/message",
                      json=m,
                      headers={"Secret": "88ec724d-5822-44df-a747-9b282492d63f"})
    except Exception as e:
        pass
