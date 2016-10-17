from xmltodict import parse

class Response(object):
    def __init__(self, data):
        self.data = data

    def parse(self):
        return parse(self.data)
