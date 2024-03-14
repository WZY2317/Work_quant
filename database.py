from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
import json
class influxManager(object):
    def __init__(self) -> None:
        self.client = InfluxDBClient('54.95.141.35', 8086,'admin','admin') # 初始化
        self.data_dict={}
    def create_database(self,name):
        self.client.create_database(name)
    def write_row(self, database_name: str, res: dict):
        try:
            self.client.switch_database(database=database_name)
            data = []
            for key, value in res.items():
               data = [
                    {
                        "measurement": "timedelay",
                        "tags": {},
                        "time": key,  # 开仓时间的时间戳
                        "fields": {
                            "value":value # 延迟时间的值（单位为毫秒）
                        }
                    }
                ]
            self.client.write_points(data)
        except InfluxDBClientError as e:
            print(f"InfluxDBClientError: {e}")
        except InfluxDBServerError as e:
            print(f"InfluxDBServerError: {e}")
    def write_row_for_arr(self, database_name: str, row):
        try:
            self.client.switch_database(database=database_name)
            data = []
            opening_time = row[0]
            return_time = row[1]
            delay_time = row[2]
            bn_time = row[3]
            bn_price = row[4]
            bg_time = row[5]
            bg_price = row[6]

            data.append({
                "measurement": "timedelay",
                "tags": {
                    "opening_time": opening_time,
                    "return_time": return_time,
                    "bn_time": bn_time,
                    "bg_time": bg_time
                },
                "fields": {
                    "delay_time": delay_time,
                    "bn_price": bn_price,
                    "bg_price": bg_price
                }
            })

            self.client.write_points(data)
        except InfluxDBClientError as e:
            print(f"InfluxDBClientError: {e}")
        except InfluxDBServerError as e:
            print(f"InfluxDBServerError: {e}")
    def write_row_for_profit(self, database_name: str, row):
        try:
            self.client.switch_database(database=database_name)
            data=[]
            
            timestamp = row[0]  # 数组的第一个元素是时间戳
            asset_value = row[1]  # 数组的第二个元素是资产价值

            data.append({
                "measurement": "asset",
                "tags": {},
                "fields": {
                    "timestamp": timestamp,
                    "asset_value": asset_value
                }
            })
            self.client.write_points(data)
        except InfluxDBClientError as e:
            print(f"InfluxDBClientError: {e}")
        except InfluxDBServerError as e:
            print(f"InfluxDBServerError: {e}")

    def test(self):
        pass

im=influxManager()
im.client.create_database('dbForcrypto')   
im.client.switch_database('dbForcrypto')

# 生成数据并写入
data = [
    {
        "measurement": "temperature",
        "tags": {
            "location": "room1",
        },
        "fields": {
            "value": 25.5,
        }
    },
    {
        "measurement": "humidity",
        "tags": {
            "location": "room1",
        },
        "fields": {
            "value": 50.2,
        }
    }
]

im.client.write_points(data)