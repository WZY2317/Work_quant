from bitget.ws.bitget_ws_client import BitgetWsClient, SubscribeReq
from bitget import consts as c
from binance.lib.utils import config_logging
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from dataManager import dataManager
import bitget.v1.mix.order_api as maxOrderApi
from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException

WS_URL_v1='wss://ws.bitget.com/mix/v1/stream'
WS_URL_v2='wss://ws.bitget.com/v2/ws/public'
apiKey = "bg_16133b342bfcc121556b688e670d4f45"
secretKey = "cab04616e4db4e431a797ffb2d65ab76fb205256cc0c9e230ac75861f68835d7"
passphrase = "asdsa87913"

client_rest=None
lastPricePair=None
fairPricePair=None

def message_handler_bg_future(message):
    print("handlexxxx:" + message)
def handle(message):
    print("handlexxx:" + message)
    global lastPricePair
    lastPricePair=dataManager.get_last_price(message)
    print(lastPricePair)
  
def message_handler_bn_future(_,message):
    print("handle:"+ message)
    global fairPricePair
    fairPricePair=dataManager.get_fair_price(message)

def rest_api():
    try:
        params = {}
        params["productType"] = "USDT-FUTURES"
        global client_rest
        client_rest=BitgetApi(api_key=apiKey,api_secret_key=secretKey,passphrase=passphrase)
        response = client_rest.get("/api/v2/mix/account/accounts", params)
        #response = client_rest.post("/api/v2/mix/order/close-positions", params)
        print(response)
    except BitgetAPIException as e:
        print("error:" + e.message)
    
def trade(symbol:str):
    try:
       
        global client_rest
        if client_rest is None:
            client_rest=BitgetApi(api_key=apiKey,api_secret_key=secretKey,passphrase=passphrase)
       
    except BitgetAPIException as e:
        print("error:" + e.message)
    fairPrice=fairPricePair['fairPrice']
    fairPriceTimestamp=fairPricePair['timeStamp']
    lastPrice=lastPricePair['lastPrice']
    lastPriceTimestamp=lastPricePair['timeStamp']
    priceLimit=0.002*fairPrice#???
    priceDiff=fairPrice-lastPrice
    if abs(priceDiff)>priceLimit:
        targetPrice=fairPrice if fairPriceTimestamp>lastPriceTimestamp else lastPrice
        side="buy" if lastPrice<fairPrice else  "sell"
        try:
            params = {}
            params["symbol"]=symbol
            params["productType"] = "USDT-FUTURES"
            params['marginMode']="isolated"
            params["marginCoin"]="USDT"
            params["size"]="10"
            params["price"]=targetPrice
            params["side"]=priceDiff
            params["orderType"]="limit"
            params["force"]="ioc"
            #这里很多参数实际上放在下单函数的前面比较好,可以减少一下下单时间,这里很多参数可以认为是固定的
            params["presetStopSurplusPrice"]=str(fairPrice)
            params["presetStopLossPrice"]="2%"
            response = client_rest.post("/api/v2/mix/order/place-order", params)
            print(response)
        except BitgetAPIException as e:
            print("error:" + e.message)
            


def ws_for_binance():
    my_client_bn_future = UMFuturesWebsocketClient(on_message=message_handler_bn_future) 
    my_client_bn_future.diff_book_depth('LINKUSDT')

def ws_for_bitget():
    #client_bg=BitgetWsClient(c.CONTRACT_WS_URL,need_login=True).api_key(apiKey).api_secret_key(secretKey).passphrase(passphrase).build()
    client_bg=BitgetWsClient(c.CONTRACT_WS_URL,need_login=False).build()
    clannles=[SubscribeReq("mc","ticker","LINKUSDT")]
    client_bg.subscribe(clannles, handle)
    
if __name__ == '__main__':
    #ws_for_bitget()
    rest_api()


