import websocket
import zlib
import time
from util import utilManager
import json


class sample_socket_client(object):

    def __init__(self, url, params, on_message):
        self.ws = None
        self.url = url
        self.params = params
        self.on_message = on_message
        self.connection()

    def connection(self):
        self.ws = websocket.WebSocketApp(url=self.url,
                                         on_message=self.on_message,
                                         on_open=self.on_open,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever(ping_interval=10,
                            ping_timeout=1,
                            ping_payload='ping')

    def on_error(self, ws, error):
        print("{}on_error:{}".format(ws, error))

    def on_close(self, ws, close_status_code, close_msg):
        self.connection()


    def on_open(self, ws):
        ws.send(self.params)
    def stop_connection(self):
        if self.ws:
            self.ws.close()


# decompress data
def inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated.decode('UTF-8')


# on message
def on_message(ws, message):
    if type(message) == bytes:
        response = inflate(message)
    else:
        response = message
    print("Received message: " + response)

def on_message_to_csv(ws, message):
    if type(message) == bytes:
        response = inflate(message)
    else:
        response = message
        res_list=utilManager.transform_for_bm_new_trade(response)
        filename='databm_for_future.csv'
        for item in res_list:
            utilManager.save_to_csv(item,filename)


        
    print("Received message: " + response)
    

if __name__ == '__main__':
    official_link = 'wss://ws-manager-compress.bitmart.com/api?protocol=1.1'
    private_link = 'ws://bitmart-aws-ws.bitmart.com/api?protocol=1.1'
    option = '{"action":"subscribe","args":["futures/klineBin1m:BTCUSDT"]}'
    option = '{"action":"subscribe","args":["futures/depth20:BTCUSDT"]}'
    sample_socket_client(private_link, option, on_message)
