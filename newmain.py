from bitget.ws.bitget_ws_client import BitgetWsClient, SubscribeReq, BaseWsReq
from bitget import consts as c
from binance.lib.utils import config_logging
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from dataManager import dataManager
import bitget.v1.mix.order_api as maxOrderApi
from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException
from ws_bitget import sample_socket_client
from collections import deque
from rest import restfulManager
from database import influxManager
import time
import threading
import asyncio
import logging
import json

fairPricebnPairbn = None
fairPricebnPairbg = None

WS_URL_v1 = 'wss://ws.bitget.com/mix/v1/stream'
WS_URL_v2 = 'wss://ws.bitget.com/v2/ws/public'
apiKey = "bg_16133b342bfcc121556b688e670d4f45"
secretKey = "cab04616e4db4e431a797ffb2d65ab76fb205256cc0c9e230ac75861f68835d7"
passphrase = "asdsa87913"

client_rest = None
data_lock = threading.Lock()
data_updated = threading.Condition(data_lock)
cond_bn = threading.Condition(data_lock)
cond_bg = threading.Condition(data_lock)

stagePost = influxManager()

class Messagedistribution():
    def message_handler_bn_future(self, _, message):
        global fairPricebnPairbn
        with cond_bn:
            #print('cccc',message)
            fairPricebnPairbn = dataManager.get_fair_price_bn(message)
            cond_bn.notify_all()
                 
    def handle(self, ws, message):
        global fairPricebnPairbg
        with cond_bg:
            #print('xxxxx',message)
            fairPricebnPairbg = dataManager.get_fair_price_bg(message)
            cond_bg.notify_all()

    def ws_for_binance(self):
        my_client_bn_future = UMFuturesWebsocketClient(on_message=self.message_handler_bn_future)
        my_client_bn_future.diff_book_depth('SOLUSDT')

    def ws_for_bitget_p(self):
        param = '{"op":"subscribe","args":[{"instType":"mc","channel":"books5","instId":"SOLUSDT"}]}'
        sample_socket_client(WS_URL_v1, params=param, on_message=self.handle)

class OrderManager():
    def __init__(self, symbol: str) -> None:
        self.params = {
            "symbol": symbol,
            # "productType": "umcbl",
            'marginMode': "isolated",
            "marginCoin": "USDT",
            "size": "0.2",  # 下单数量暂且定位十美金
            "price": None,
            "side": None,
            "orderType": "limit",
            "timeInForceValue": "ioc",
            "presetStopSurplusPrice": None
        }

    def trading(self):
        global client_rest
        global fairPricebnPairbn
        global fairPricebnPairbg
        if client_rest is None:
            client_rest = BitgetApi(api_key=apiKey, api_secret_key=secretKey, passphrase=passphrase)
        while True:
            start_time = time.time() * 1000
            arr = []
            databn = {}
            databg = {}

            # 等待 Binance 行情数据
            with cond_bn:
                cond_bn.wait_for(lambda: fairPricebnPairbn is not None)
                fairPricebnPair = fairPricebnPairbn
                fairPricebnPairbn = None
                fairPricebn = fairPricebnPair['fairPrice']
                fairPricebnTimestampbn = fairPricebnPair['timeStamp']

            # 等待 Bitget 行情数据
            with cond_bg:
                cond_bg.wait_for(lambda: fairPricebnPairbg is not None)
                fairPricebnPairbg_copy = fairPricebnPairbg
                fairPricebnPairbg = None
                fairPircebg = fairPricebnPairbg_copy['fairPrice']
                fairPircebgTimestampbg = fairPricebnPairbg_copy['timeStamp']

            priceLimit = 0.002 * fairPricebn
            priceDiff = fairPricebn - fairPircebg
            res = {}
            if abs(priceDiff) > priceLimit:
                targetPrice = fairPircebg
                side = "open_long" if fairPircebg < fairPricebn else "open_short"
                self.params["price"] = round(targetPrice, 3)
                self.params["side"] = side
                self.params["presetTakeProfitPrice"] = str(round(fairPricebn, 3))
                order_timeStamp = int(time.time() * 1000)
                end_time = time.time()
                execution_time = end_time - start_time
                result = client_rest.post("/api/mix/v1/order/placeOrder", self.params)
                res_timeStamp = result['requestTime']
                timedelay = int(res_timeStamp) - order_timeStamp
                res[order_timeStamp] = (timedelay)
                databn[fairPricebnTimestampbn] = fairPricebn
                databg[fairPircebgTimestampbg] = fairPircebg
                arr.append(order_timeStamp)
                arr.append(res_timeStamp)
                arr.append(timedelay)
                arr.append(fairPricebnTimestampbn)
                arr.append(fairPricebn)
                arr.append(fairPircebgTimestampbg)
                arr.append(fairPircebg)
                
                stagePost.write_row_for_arr('logdb', arr)
                print("下单成功")
                time.sleep(5)

async def profit_record():
    restM = restfulManager()
    while True:
        res = restM.get_account_message()
        data = json.loads(json.dumps(res))
        arr = []
        requestTime = data['requestTime']
        equity = data['data'][0]['accountEquity']
        arr.append(requestTime)
        arr.append(equity)
        stagePost.write_row_for_profit('assetdb', arr)
        time.sleep(20)

def mmm():
    MD = Messagedistribution()

    thread_bn = threading.Thread(target=MD.ws_for_binance)
    thread_bg = threading.Thread(target=MD.ws_for_bitget_p)
    thread_value = threading.Thread(target=profit_record)
    thread_trade = threading.Thread(target=OrderManager('SOLUSDT_UMCBL').trading)

    threads = [thread_bn, thread_bg, thread_value, thread_trade]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    #restM=restfulManager()
    #restM.get_all_position()
    #restM.get_account_message()
    #restM.close_position()
    #print(r)
    #restM.get_single_position()
    mmm()
    #restM.set_position_mode()