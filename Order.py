class Order:

    def __init__(self, request):
        self.channel_from_url = request.json['channel_from_url']
        self.channel_to_url = request.json['channel_to_url']
        self.ids = request.json['ids']
        self.count = request.json['count']

        words = request.json['words'].split(',')
        self.words = []
        for word in words:
            self.words.append(str.lower(word.strip()))
