import json
class dataManager:
    @staticmethod
    def get_fair_price_bn(message:str):
        res={}
        data=json.loads(message)
        time_stamp=int(data['E'])
        size=len(data['a'][0][0])
        bids1=float(data['b'][0][0])
        #amount_bid1=float(data['bids'][0][1])
        asks1=float(data['a'][0][0])
        #amount_ask1=float(data['asks'][0][1])
        fairPrice=float((bids1+asks1)/2)
        res['fairPrice']=fairPrice
        res['timeStamp']=time_stamp
        return res
    @staticmethod
    def get_fair_price_bg(message):
        res={}
        data=json.loads(message)
        print(data)
        asks1=float(data['data'][0]['asks'][0][0])
        bids1=float(data['data'][0]['bids'][0][0])
        fairPrice=(bids1+asks1)/2
        timeStamp=int(data['ts'])
        res['fairPrice']=fairPrice
        res['timeStamp']=timeStamp
        return res

        
    