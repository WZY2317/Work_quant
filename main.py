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
from rest import restfulManager
from database import influxManager
import time
import threading
import asyncio
import logging
import json
fairPricebnPairbg=None
fairPricebnPairbn=None

WS_URL_v1='wss://ws.bitget.com/mix/v1/stream'
WS_URL_v2='wss://ws.bitget.com/v2/ws/public'
apiKey = "bg_16133b342bfcc121556b688e670d4f45"
secretKey = "cab04616e4db4e431a797ffb2d65ab76fb205256cc0c9e230ac75861f68835d7"
passphrase = "asdsa87913"

client_rest=None
data_lock = threading.Lock()
data_updated = threading.Condition(data_lock)

global stagePost
stagePost=influxManager()
# fairPricebnPairbg=None
# fairPricebnPairbn=None
class Messagedistribution():
    def __init__(self) -> None:
        # self.fairPricebnPairbg=fairPricebnPairbg
        # self.fairPricebnPairbn=fairPricebnPairbn
        self.priceDiff=0
        # self.dq1=containerBn
        # self.dq2=containerBg

    def handle(self,ws,message):
        #print("handlexxx:" + message)
        global fairPricebnPairbg
        with data_lock:
            fairPricebnPairbg=dataManager.get_fair_price_bg(message)
            data_updated.notify()#通知等待的线程有更新
        #self.dq1.append(self.fairPricebnPairbg)
        #print('BG',self.fairPricebnPairbg)
  
    def message_handler_bn_future(self,_,message):
        global fairPricebnPairbn
        #print("handle:"+ message)
        with data_lock:
            fairPricebnPairbn=dataManager.get_fair_price_bn(message)
            data_updated.notify()
        #self.dq2.append(self.fairPricebnPairbn)
        #print('BN',self.fairPricebnPairbn)

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
         self.params["productType"] = "umcbl"
         self.params['marginMode']="isolated"
         self.params["marginCoin"]="USDT"
         self.params["size"]="3"#下单数量暂且定位十美金
         self.params["price"]=None
         self.params["side"]=None
         self.params["orderType"]="limit"
         self.params["force"]="ioc"
         self.params["presetStopSurplusPrice"]=None
        
         self.dq1=containerBn
         self.dq2=containerBg
    def trading(self):
        time.sleep(1)
        global fairPricebnPairbn,fairPricebnPairbg
        # priceLimit=0
        # priceDiff=0
        global client_rest
        if client_rest is None:
            client_rest=BitgetApi(api_key=apiKey,api_secret_key=secretKey,passphrase=passphrase)
        while True:
                 with data_lock:
            # 等待有新数据到达
                    data_updated.wait()
                    start_time = time.time()*1000
                    arr=[]
                    databn={}
                    databg={}
                    fairPricebn=fairPricebnPairbn['fairPrice']
                    fairPricebnTimestampbn=fairPricebnPairbn['timeStamp']
                    fairPircebg=fairPricebnPairbg['fairPrice']
                    fairPircebgTimestampbg=fairPricebnPairbg['timeStamp']
                    priceLimit=0.002*fairPricebn#???
                    priceDiff=fairPricebn-fairPircebg
                    res={}
                    if abs(priceDiff)>priceLimit:
                        targetPrice=fairPircebg 
                        #哪个交易所的价格慢,开仓价格就是哪个交易所
                        side="buy" if fairPircebg<fairPricebn else  "sell"
                        self.params["price"]=round(targetPrice,3)
                        self.params["side"]=side
                        self.params["presetStopSurplusPrice"]=str(round(fairPricebn,3))
                        #self.params["presetStopLossPrice"]="10%"
                        order_timeStamp=int(time.time() * 1000)
                        #stagePost.insert('下单时间',str(order_timeStamp))
                        end_time = time.time()
                        execution_time = end_time - start_time
                        #print('xxxxxxxxxx',execution_time)
                        result=client_rest.post("/api/v2/mix/order/place-order", self.params)#等待下单完成
                        res_timeStamp=result['requestTime']
                        
                        timedelay=int(res_timeStamp)-order_timeStamp
                        res[order_timeStamp]=(timedelay)
                        databn[fairPricebnTimestampbn]=fairPricebn
                        databg[fairPircebgTimestampbg]=fairPircebg
                        arr.append(order_timeStamp)
                        arr.append(res_timeStamp)
                        arr.append(timedelay)
                        arr.append(fairPricebnTimestampbn)
                        arr.append(fairPricebn)
                        arr.append(fairPircebgTimestampbg)
                        arr.append(fairPircebg)
                        #stagePost.insert('返回时间',str(res_timeStamp))
                        print("下单成功")
                        # stagePost.write_row('mydb',res)
                        # stagePost.write_row('resTimeForbn',databn)
                        # stagePost.write_row('resTimeForbg',databg)
                        stagePost.write_row_for_arr('logdb',arr)
                        #time.sleep(2)


                #print("error:" + e.message)
def profit_record():
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

def listen_order():
    while True:
        pass

# def run_loop_inside_thread(loop):
#     loop.run_forever()

def mmm():
    dequeBn=deque(maxlen=1)
    dequeBg=deque(maxlen=1)  
    MD=Messagedistribution()
    OM=OrderManager('LINKUSDT',dequeBn,dequeBg)
    thread_bn=threading.Thread(target=MD.ws_for_binance)
    thread_bg=threading.Thread(target=MD.ws_for_bitget_p)
    thread_value=threading.Thread(target=profit_record)
    #hread_trade=threading.Thread(target=loop.run_until_complete(OM.trading()))
    #thread_trade=threading.Thread(target=run_loop_inside_thread,args=(loop,)).start()
    #loop.call_soon_threadsafe(OM.trading)
    thread_trade=threading.Thread(target=OM.trading)

    threads=[
            thread_bn,
            thread_bg,
            thread_value,
            thread_trade
            ]
    for thread in threads:
        thread.start()
    # 等待线程结束
# #rest_api()
if __name__ == '__main__':
    #mmm()
    restM=restfulManager()
    #restM.get_account_message()
    restM.close_position
    
    #restM.get_current_plan()
    #restM.get_single_position()
    #restM.close_position()
    #restM.cancel_all_order()
#1:663.1418
   


