import json
class dataManager:
    @staticmethod
    def get_fair_price(message:str):
        res={}
        data=json.loads(message)
        time_stamp=int(data['lastUpdateId'])
        bids1=float(data['bids'][0][0])
        amount_bid1=float(data['bids'][0][1])
        asks1=float(data['asks'][0][0])
        amount_ask1=float(data['asks'][0][1])
        fairPrice=float((bids1+asks1)/2)
        res['fairPrice']=fairPrice
        res['timeStamp']=time_stamp
        return 
    @staticmethod
    def get_last_price(message):
        res={}
        data=json.loads(message)
        lastPrice=float(data['data'][0]['last'])
        timeStamp=int(data['ts'])
        res['lastPrice']=lastPrice
        res['timeStamp']=timeStamp
        return res

        
    