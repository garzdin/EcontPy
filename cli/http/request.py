import requests
from response import Response

class Request(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def send(self, data):
        data = requests.post(self.endpoint, files={'file': data}).text.encode('utf-8')
        return Response(data).parse()
