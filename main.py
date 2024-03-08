from bitget.ws.bitget_ws_client import BitgetWsClient, SubscribeReq
from bitget import consts as c
from binance.lib.utils import config_logging
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

def message_handler_bg_future(message):
    print("handle:" + message)
def message_handler_bn_future(_,message):
    pass
WS_URL_v1='wss://ws.bitget.com/mix/v1/stream'
WS_URL_v2='wss://ws.bitget.com/v2/ws/public'
apiKey = ""
secretKey = '''your'''
passphrase = ""

def ws_for_binance_future():
    my_client_bn_future = UMFuturesWebsocketClient(on_message=message_handler_future) 
    my_client_bn_future.agg_trade('1000PEPEUSDT')

if __name__ == '__main__':
    
    client_bg=BitgetWsClient(WS_URL_v1,need_login=False).build()
    clannles=[SubscribeReq("MC","ticker","LINKUSDT")]
    client_bg.subscribe(clannles, message_handler_bg_future)


