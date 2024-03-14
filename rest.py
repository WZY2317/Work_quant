
from typing import Any
from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException
apiKey = "bg_16133b342bfcc121556b688e670d4f45"
secretKey = "cab04616e4db4e431a797ffb2d65ab76fb205256cc0c9e230ac75861f68835d7"
passphrase = "asdsa87913"
class restfulManager:
    def __init__(self) -> None:
        self.client_rest=BitgetApi(api_key=apiKey,api_secret_key=secretKey,passphrase=passphrase)


    def close_position(self):
        try:
            params = {}
            params["productType"] = "USDT-FUTURES"
            #response = client_rest.get("/api/v2/mix/account/accounts", params)
            response = self.client_rest.post("/api/v2/mix/order/close-positions", params)
            print(response)
        except BitgetAPIException as e:
            print("error:" + e.message)
    def set_leverage(self):
        try:
            params = {}
            params["symbol"]="LINKUSDT"
            params["productType"] = "USDT-FUTURES"
            params["marginCoin"]="USDT"
            params["leverage"]="10"
            response = self.client_rest.post("/api/v2/mix/account/set-leverage", params)
            #response = client_rest.post("/api/v2/mix/order/close-positions", params)
            print(response)
        except BitgetAPIException as e:
            print("error:" + e.message)
    def get_account_message(self):
        try:
            params = {}
            params["productType"] = "USDT-FUTURES"
            response = self.client_rest.get("/api/v2/mix/account/accounts", params)
            return response
        except BitgetAPIException as e:
            print("error:" + e.message)
    def get_margin_current(self):
        try:
            params = {}
            #params["productType"] = "umcbl"
            # params["marginCoin"]="USDT"
            params["symbol"]="LINKUSDT_UMCBL"
            response = self.client_rest.get("/api/mix/v1/order/current", params)
            print(response)
        except BitgetAPIException as e:
            print("error:" + e.message)
    def get_single_position(self):
        try:
            params = {}
            #params["productType"] = "umcbl"
            params["marginCoin"]="USDT"
            params["symbol"]="SOLUSDT_UMCBL"
            response = self.client_rest.get("/api/mix/v1/position/singlePosition-v2", params)
            print(response)
        except BitgetAPIException as e:
            print("error:" + e.message)
    
    def get_all_position(self):
        try:
            params = {}
            params["productType"] = "umcbl"
            params["marginCoin"]="USDT"
            #params["symbol"]="LINKUSDT_UMCBL"
            response = self.client_rest.get("/api/mix/v1/position/allPosition-v2", params)
            print(response)
        except BitgetAPIException as e:
            print("error:" + e.message)
    def get_current_plan(self):
        try:
            params = {}
            params["productType"] = "umcbl"
            
            params["marginCoin"]="USDT"
            #params["isPlan"]="plan"
            response = self.client_rest.get("/api/mix/v1/order/marginCoinCurrent", params)
            print(response)
        except BitgetAPIException as e:
            print("error:" + e.message)
    def get_history_plan(self):
        try:
            params = {}
            #params["productType"] = "umcbl"
            
            # params["symbol"]="LINKUSDT_UMCBL"
            # params["isPlan"]="plan"
            params['startTime']='1710144002000'
            params['endTime']='1710145394538'
            response = self.client_rest.get("/api/mix/v1/plan/historyPlan", params)
            print(response)
        except BitgetAPIException as e:
            print("error:" + e.message)
    def cancel_all_order(self):
        try:
            params = {}
            params["productType"] = "umcbl"
            params["marginCoin"]="USDT"
            response = self.client_rest.post("/api/mix/v1/order/cancel-all-orders", params)
            print(response)
        except BitgetAPIException as e:
            print("error:" + e.message)
    def set_position_mode(self):
        try:
            params = {}

            params["productType"] = "umcbl"
            #params["marginCoin"]="USDT"


            params["holdMode"]="double_hold"
            response = self.client_rest.post("/api/mix/v1/account/setPositionMode", params)
            print(response)
        except BitgetAPIException as e:
            print("error:" + e.message)
