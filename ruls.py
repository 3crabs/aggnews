def forward(client, request):
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


def good_message(message, words, sending_ids):
    for word in words:
        if (word in message.message) and (message.id not in sending_ids):
            return True
    return False


async def dump_all_messages(channel_from_url, channel_from, channel_to_url, channel_to, words, sending_ids,
                            total_count_limit):
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
    misha_messages = []

    for message in messages:
        if good_message(message, words, sending_ids):
            misha_messages.append({"channel_from": channel_from_url, "channel_to": channel_to_url, "id": message.id})
            await client.forward_messages(channel_to, message.id, channel_from)

    try:
        m = {"messages": misha_messages}
        requests.post("http://9f7aadf2.ngrok.io/api/message",
                      json=m,
                      headers={"Secret": "88ec724d-5822-44df-a747-9b282492d63f"})
    except Exception as e:
        pass


async def f(channel_from_url, channel_to_url, words, sending_ids, total_count_limit):
    channel_from = await client.get_entity(channel_from_url)
    channel_to = await client.get_entity(channel_to_url)
    await dump_all_messages(channel_from_url, channel_from, channel_to_url, channel_to, words, sending_ids,
                            total_count_limit)
