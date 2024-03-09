from bitget.ws.bitget_ws_client import BitgetWsClient, SubscribeReq,BaseWsReq
from bitget import consts as c
from binance.lib.utils import config_logging
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from dataManager import dataManager
import bitget.v1.mix.order_api as maxOrderApi
from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException
from ws_bitget import sample_socket_client
from queue import Queue
from collections import deque
import time
import threading
import asyncio
import logging
#from core import statusupdate, bilidynamic

WS_URL_v1='wss://ws.bitget.com/mix/v1/stream'
WS_URL_v2='wss://ws.bitget.com/v2/ws/public'
apiKey = "bg_16133b342bfcc121556b688e670d4f45"
secretKey = "cab04616e4db4e431a797ffb2d65ab76fb205256cc0c9e230ac75861f68835d7"
passphrase = "asdsa87913"

client_rest=None
# fairPricebnPairbg=None
# fairPricebnPairbn=None
class Messagedistribution():
    def __init__(self,containerBn,containerBg) -> None:
        self.fairPricebnPairbg=None
        self.fairPricebnPairbn=None
        self.priceDiff=0
        self.dq1=containerBn
        self.dq2=containerBg

    def handle(self,ws,message):
        print("handlexxx:" + message)
        self.fairPricebnPairbg=dataManager.get_fair_price_bg(message)
        self.dq1.append(self.fairPricebnPairbg)
        print('BG',self.fairPricebnPairbg)
  
    def message_handler_bn_future(self,_,message):
        print("handle:"+ message)
        self.fairPricebnPairbn=dataManager.get_fair_price_bn(message)
        self.dq2.append(self.fairPricebnPairbn)
        print('BN',self.fairPricebnPairbn)

    def ws_for_binance(self):
        my_client_bn_future = UMFuturesWebsocketClient(on_message=self.message_handler_bn_future) 
        my_client_bn_future.diff_book_depth('LINKUSDT')

    def ws_for_bitget_p(self):
        param='{"op":"subscribe","args":[{"instType":"mc","channel":"books5","instId":"LINKUSDT"}]}'
        client_bg=sample_socket_client(WS_URL_v1,params=param,on_message=self.handle)
    
    #上面两个线程给第三个线程传递消息
        
    

class OrderManager():
    def __init__(self,symbol:str,containerBn:deque,containerBg:deque) -> None:
         self.params = {}
         self.params["symbol"]=symbol
         self.params["productType"] = "USDT-FUTURES"
         self.params['marginMode']="isolated"
         self.params["marginCoin"]="USDT"
         self.params["size"]="3"#下单数量暂且定位十美金
         self.params["price"]=None
         self.params["side"]=None
         self.params["orderType"]="limit"
         self.params["force"]="ioc"
        #这里很多参数实际上放在下单函数的前
        #面比较好,可以减少一下下单时间,这里很多参数可以认为是固定的
         self.params["presetStopSurplusPrice"]=None
         self.dq1=containerBn
         self.dq2=containerBg
    def trading(self):
        time.sleep(2)
        # priceLimit=0
        # priceDiff=0
        while True:
            logging.info('正在监听')
            try:
                global client_rest
                if client_rest is None:
                    client_rest=BitgetApi(api_key=apiKey,api_secret_key=secretKey,passphrase=passphrase)
            except BitgetAPIException as e:
                print("error:" + e.message)
            
            
            fairPricebn=self.dq1[0]['fairPrice']
            fairPricebnTimestampbn=self.dq1[0]['timeStamp']
            fairPircebg=self.dq2[0]['fairPrice']
            fairPircebgTimestampbg=self.dq2[0]['timeStamp']
            priceLimit=0.002*fairPricebn#???
            priceDiff=fairPricebn-fairPircebg
               
            if abs(priceDiff)>priceLimit:
                targetPrice=fairPricebn if fairPricebnTimestampbn>fairPircebgTimestampbg else fairPircebg
                side="buy" if fairPircebg<fairPricebn else  "sell"
                self.params["price"]=round(targetPrice,3)
                self.params["side"]=side
                #self.params["presetStopSurplusPrice"]=str(round(fairPricebn,3))
                #params["presetStopLossPrice"]="2%"
                print(self.params)
                client_rest.post("/api/v2/mix/order/place-order", self.params)#等待下单完成
                print("下单成功")
                #print("error:" + e.message)
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
        

# def ws_for_bitget():
#     #client_bg=BitgetWsClient(c.CONTRACT_WS_URL,need_login=True).api_key(apiKey).api_secret_key(secretKey).passphrase(passphrase).build()
#     client_bg=BitgetWsClient(c.CONTRACT_WS_URL,need_login=False).build()
# #     clannles=[BaseWsReq(op="subscribe",args=[
# #     {
# #       "instType":"mc",
# #       "channel":"books5",
# #       "instId":"BTCUSDT"
# #     }
# #   ])]
#     client_bg.send_message(op="subscribe",args=[
#     {
#       "instType":"mc",
#       "channel":"books5",
#       "instId":"LINKUSDT"
#     }
#   ])

def run_loop_inside_thread(loop):
    loop.run_forever()

rest_api()
# if __name__ == '__main__':
#     #ws_for_bitget()
#     loop = asyncio.get_event_loop()
#     global dequeBn
#     global dequeBg
#     dequeBn=deque(maxlen=1)
#     dequeBg=deque(maxlen=1)  
#     MD=Messagedistribution(dequeBn,dequeBg)
#     OM=OrderManager('LINKUSDT',dequeBn,dequeBg)
#     thread_bn=threading.Thread(target=MD.ws_for_binance)
#     thread_bg=threading.Thread(target=MD.ws_for_bitget_p)
#     #hread_trade=threading.Thread(target=loop.run_until_complete(OM.trading()))
#     #thread_trade=threading.Thread(target=run_loop_inside_thread,args=(loop,)).start()
#     #loop.call_soon_threadsafe(OM.trading)
#     thread_trade=threading.Thread(target=OM.trading)

#     threads=[
#             thread_bn,
#             thread_bg,
#             thread_trade
#             ]
#     start=time.time()
#     for thread in threads:
#         thread.start()
#     # 等待线程结束
#     for thread in threads:
#         thread.join()

   



