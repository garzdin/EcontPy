import client

if __name__ == '__main__':
    c = client.Client(demo=True).login("iasp-dev", "iasp-dev")
    data = c.get_shipments()
    print(data)
