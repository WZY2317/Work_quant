import csv
import json
import statistics
import pytz
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec
import plotly.graph_objects as go
import plotly.subplots as sp
time_set=set()
class utilManager:
    @staticmethod
    def calulateDonkMidPrice(Va,Vb,Pa,Pb,F_t,P_mid):
        I=(Va-Vb)/(Va+Vb)
        S=(Pa-Pb)/((Pa+Pb)/2)
        s=((S+F_t)/2)
        At=0.6
        ct=0.4
        sitar=At*s+ct
        P_fair=P_mid+sitar*(I*(I*I+1))/2
        return P_fair
    @staticmethod
    def save_to_csv(row,filename:str):
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
           
            if row is None:
                return  # 跳过空行
            if len(row) < 2:
                return  # 跳过字段数量不足的行
            
            writer.writerow(row)  # 将数据写入 CSV 文件
            #print('success')
    @staticmethod
    def save_to_csv_for_bn(row,filename:str):
        with open(filename, 'a') as file:
            writer = csv.writer(file)
            if row is None:
                return  # 跳过空行
            if row[0] not in time_set:
                 time_set.add(row[0])
                 writer.writerow(row) 
    @staticmethod
    def save_to_csv_depth(row,filename:str):
         with open(filename, 'a') as file:
             writer=csv.writer(file)
             if row is None:
                 return 
             writer.writerow(row) 

    @staticmethod
    def transform_for_depth(message:str):
        data=json.loads(message)
        time_stamp=int(data['lastUpdateId'])
        bids1=float(data['bids'][0][0])
        amount_bid1=float(data['bids'][0][1])
        asks1=float(data['asks'][0][0])
        amount_ask1=float(data['asks'][0][1])
        return time_stamp,bids1,amount_bid1,asks1,amount_ask1
    @staticmethod
    def transform(message:str):
        data=json.loads(message)
        
        price=float(data['p'])
        
            #price=float(data['p'])
        timeStamp = int(data['E'])
        # timeStamp_sec = timeStamp / 1000  # 将毫秒级时间戳转换为秒级时间戳
        # dt = datetime.datetime.fromtimestamp(timeStamp_sec)
        # time_str = dt.strftime('%H:%M:%S.%f')[:-3] 
        return timeStamp,price
    @staticmethod
    def transform_for_spot_meme(message:str):
        data=json.loads(message)
        
        price=float(data['p'])*1000
        
            #price=float(data['p'])
        timeStamp = int(data['E'])
        # timeStamp_sec = timeStamp / 1000  # 将毫秒级时间戳转换为秒级时间戳
        # dt = datetime.datetime.fromtimestamp(timeStamp_sec)
        # time_str = dt.strftime('%H:%M:%S.%f')[:-3] 
        return timeStamp,price
    @staticmethod
    def transform_for_bm(message:str):
        data=json.loads(message)
        price=data['data'][0]['last_price']
        price=str(price)
        timeStamp = int(data['data'][0]['ms_t'])
        timeStamp_sec = timeStamp / 1000  # 将毫秒级时间戳转换为秒级时间戳
        dt = datetime.datetime.fromtimestamp(timeStamp_sec)
        time_str = dt.strftime('%H:%M:%S.%f')[:-3] 
        return time_str,price
    def transform_for_bm_new_trade(message:str):
        data=json.loads(message)
        print(data)
        res=data["data"]
        print(res)
        trades=[]
        target_list=[]
        for trade_data in res:
            trades.append(trade_data)
        for item in trades:
            time_stamp_mill = int(item["create_time_mill"])
            price=float(item['deal_price'])
            row=[time_stamp_mill,price]
            target_list.append(row)
        return target_list
            
        
    @staticmethod
    def merge_csv_files(file1, file2, merged_file):
        with open(file1,'r') as f1,open(file2,'r') as f2,open(merged_file,'w') as outfile:
            reader1=csv.reader(f1)
            reader2=csv.reader(f2)
            writer=csv.writer(outfile)
            merged_data=[]
            rows1 = list(reader1)  # 读取文件1的所有行
            rows2 = list(reader2)  # 读取文件2的所有行
            #这里的value1是bitmart的
            for row1 in rows1:
                time1 = row1[0]
                value1 = row1[1]
                time1_dt = datetime.strptime(time1, "%H:%M:%S.%f")
                value_list=[]
                for row2 in rows2:
                    time2 = row2[0]
                    value2 = row2[1]

                    time2_dt = datetime.strptime(time2, "%H:%M:%S.%f")
                    time_diff = time2_dt - time1_dt
                    

                    if abs(time_diff.total_seconds()) <= 0.1:
                        value_list.append(float(value2))
                        # merged_row = [time1, value1, value2,price_diff]
                        # merged_data.append(merged_row)
                if len(value_list)!=0:
                    value_avg_bn=round(statistics.mean(value_list),2)
                price_diff=round(float(value1)-float(value_avg_bn),2)
                merged_row=[time1,value1,value_avg_bn,price_diff]
                merged_data.append(merged_row)
                
            writer.writerows(merged_data)
    @staticmethod
    def merge_csv(file_bn,file_other,merged_file):
        with open(file_bn,'r') as f1,open(file_other,'r') as f2,open(merged_file,'w') as outfile:
            reader1=csv.reader(f1)
            reader2=csv.reader(f2)
            writer=csv.writer(outfile)
            rows1 = list(reader1)  # 读取文件1的所有行
            rows2 = list(reader2)  # 读取文件2的所有行
            merged_row={}
            price_row=[]
            for row1 in rows1:
                time1 = row1[0]
                value1 = row1[1]
                price_row.append(value1)
                merged_row[time1]=price_row
                price_row=[]
            for row2 in rows2:
                time2=row2[0]
                value2=row2[1]
                if time2 in merged_row.keys():
                    price_diff=float(merged_row[time2][0])-float(value2)
                    merged_row[time2].append(value2)
                    merged_row[time2].append(price_diff)

            for key,value in merged_row.items():
                key_row=[key,value[0],value[1],value[2]]
                writer.writerow(key_row)
    @staticmethod
    def generate_csv_for_price_diff(file_bn:str,file_other:str,output_csv:str):
        #这里的逻辑稍微有点复杂,bm的csv每两个作为一组数据,比如time_a,time_b,然后再bncsv
        #里边找到一个交集区间,起始的时间是小的时间的较大者,结束的时间是大的时间的较小者,
        #里边还会有几个时间戳,这几个时间戳,就是要计算价差的
        with open(file_bn,'r') as f1,open(file_other,'r') as f2,open(output_csv,'w') as outfile:
            reader1=csv.reader(f1)
            reader2=csv.reader(f2)
            writer=csv.writer(outfile)
            rows1 = list(reader1)  # 读取文件1的所有行
            rows2 = list(reader2)  # 读取文件2的所有行
            #rows2作为基准
            start_time=max(int(rows1[0][0]),int(rows2[0][0]))
            i=1
            j=1
            next_time=rows2[j][0]
            
            start_index=1 if int(rows2[0])>int(rows2[0]) else 0
            end_index=0
            while j <=len(rows2) and i<=len(rows1):
                while rows1[i]<next_time:
                    i=i+1
                end_time=rows1[j-1]
            
                end_index=i-1
                #这里要把bn的价格填进去
                k=start_index
                sub_row=[]
                for k in range(start_index,end_index):
                    sub_row.append(rows1[k])
                    price_diff=float(rows1[k])-float(rows2[start_index])
                    sub_row.append(str(price_diff))
                start_index=j
                i=i+1
                next_time=rows2[i]
                start_time=rows1[j]
    @staticmethod
    def merge_and_add_price_difference(file_bn: str, file_other: str, output_csv: str):
    # 读取第一个CSV文件
        data_bn = []
        with open(file_bn, 'r') as file_bn:
            reader_bn = csv.reader(file_bn)
            next(reader_bn)  # 跳过标题行（如果有）
            for row in reader_bn:
                row.append("file_bn")  # 添加标识列
                data_bn.append(row)

        # 读取第二个CSV文件
        data_other = []
        with open(file_other, 'r') as file_other:
            reader_other = csv.reader(file_other)
            next(reader_other)  # 跳过标题行（如果有）
            for row in reader_other:
                row.append("file_other")  # 添加标识列
                data_other.append(row)

        # 合并两个数据列表
        dauta_combined = data_bn + data_other

        # 按时间戳对数据进行排序
        sorted_data = sorted(dauta_combined, key=lambda x: x[0])

        # 添加上一行价格列和价差列
        # 添加上一行价格列和价差列
        data_with_previous_price_and_difference = []
        previous_price = None
        for row in sorted_data:
            if previous_price is None:
                previous_price = row[1]
            row.append(previous_price)  # 添加上一行价格列

            if row[-2] in ("file_bn", "file_other"):
                if row[-2] == "file_bn":
                    price_difference = float(row[1]) - float(row[3])
                    price_difference_percent=(price_difference/float(row[1]))*100

                elif row[-2] == "file_other":
                    price_difference = float(row[3]) - float(row[1])
                    price_difference_percent=(price_difference/float(row[3]))*100
                else:
                    price_difference = None
                    price_difference_percent=None

                row.append(price_difference)  # 添加价差列
                row.append(price_difference_percent)

            data_with_previous_price_and_difference.append(row)
            previous_price = row[1]

        # 写入输出CSV文件
        with open(output_csv, 'w', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerows(data_with_previous_price_and_difference)
    @staticmethod
    def plot_price_movement(csv_file0,csv_file1, output_file):
        prices0 = []
        prices1 = []

        with open(csv_file0, 'r') as file0, open(csv_file1, 'r') as file1:
            reader0 = csv.reader(file0)
            next(reader0)  # 跳过标题行

            for row in reader0:
                price = float(row[1])
                prices0.append(price)

            reader1 = csv.reader(file1)
            next(reader1)  # 跳过标题行

            for row in reader1:
                price = float(row[1])
                prices1.append(price)

        fig, ax = plt.subplots(figsize=(16, 8))  # 设置图像尺寸为16x8
        ax.plot(prices0, color='blue', linewidth=1, label='File 0')  # 绘制第一个文件的价格曲线
        ax.plot(prices1, color='red', linewidth=1, label='File 1')  # 绘制第二个文件的价格曲线

        for i in range(len(prices0)):
            if i > 0:
                if prices0[i] > prices0[i-1]:
                    ax.axvline(x=i, color='green', linewidth=1, alpha=0.3)  # 第一个文件的上涨用绿色竖线表示
                elif prices0[i] < prices0[i-1]:
                    ax.axvline(x=i, color='red', linewidth=1, alpha=0.3)  # 第一个文件的下跌用红色竖线表示

        for i in range(len(prices1)):
            if i > 0:
                if prices1[i] > prices1[i-1]:
                    ax.axvline(x=i, color='orange', linewidth=1, alpha=0.3)  # 第二个文件的上涨用橙色竖线表示
                elif prices1[i] < prices1[i-1]:
                    ax.axvline(x=i, color='purple', linewidth=1, alpha=0.3)  # 第二个文件的下跌用紫色竖线表示

        ax.axhline(y=prices0[0], linestyle='--', color='black', linewidth=1)  # 第一个文件的初始价格用虚线表示
        ax.axhline(y=prices1[0], linestyle='--', color='black', linewidth=1)  # 第二个文件的初始价格用虚线表示

        ax.set_xlabel('Time')
        ax.set_ylabel('Price')
        ax.set_title('Price Movement')
        ax.legend()  # 显示图例
        plt.savefig(output_file)  # 保存为PNG文件
        plt.close()
    @staticmethod
    def merge_and_add_price_difference_new(file_bn: str, file_other: str, output_csv: str):
         # 读取第一个CSV文件
        data_bn = []
        with open(file_bn, 'r') as file_bn:
            reader_bn = csv.reader(file_bn)
            next(reader_bn)  # 跳过标题行（如果有）
            for row in reader_bn:
                row.append("file_bn")  # 添加标识列
                data_bn.append(row)

        # 读取第二个CSV文件
        data_other = []
        with open(file_other, 'r') as file_other:
            reader_other = csv.reader(file_other)
            next(reader_other)  # 跳过标题行（如果有）
            for row in reader_other:
                row.append("file_other")  # 添加标识列
                data_other.append(row)

        # 合并两个数据列表
        data_combined = data_bn + data_other

        # 按时间戳对数据进行排序
        sorted_data = sorted(data_combined, key=lambda x: x[0])

        # 添加价差列
        data_with_price_difference = []
        for i, row in enumerate(sorted_data):
            if row[-1] == "file_bn":
                price_difference = 0
                for j in range(i-1, -1, -1):
                    if sorted_data[j][-2] == "file_other":
                        price_difference = float(row[1]) - float(sorted_data[j][1])
                        break
            elif row[-1] == "file_other":
                price_difference = 0
                for j in range(i-1, -1, -1):
                    if sorted_data[j][-2] == "file_bn":
                        price_difference = float(sorted_data[j][1]) - float(row[1])
                        break
            else:
                price_difference = 0

            row.append(price_difference)  # 添加价差列
            data_with_price_difference.append(row)

        # 写入输出CSV文件
        with open(output_csv, 'w', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerows(data_with_price_difference)

class test:
    @staticmethod
    def draw_fair_price_line(source_data):
        times=[]
        fair_prices=[]
        for item in source_data:
            time = item[0]
            fair_price = item[1]
            times.append(time)
            fair_prices.append(fair_price)
        # 创建价格变化的跳动效果图
        fig = go.Figure(data=go.Scatter(x=times, y=fair_prices, mode='lines+markers'))

        # 设置图表布局和样式
        fig.update_layout(
            title='Fair Price Variation',
            xaxis_title='Time',
            yaxis_title='Price',
            showlegend=False
        )

        # 显示图表
        fig.show()
        

    @staticmethod
    def drawKline(input_data,output_file,bn_kind,other_kind):
        pricesbn = []
        pricesbm = []
        pricesdiff = []
        pricesdiffPercent=[]
        times = []
        for item in input_data:
            time=int(item[0])
            pricebn=float(item[1])
            pricebm=float(item[2])
            pricediff=float(item[3])
            pricediffpercent=float(item[4])
            times.append(time)
            pricesbn.append(pricebn)
            pricesbm.append(pricebm)
            pricesdiff.append(pricediff)
            pricesdiffPercent.append(pricediffpercent)
        
        fig = sp.make_subplots(rows=3, cols=1, subplot_titles=('Price_bn and Price_bm', 'Price_diff','Price_diff_percent'))

        fig.add_trace(go.Scatter(x=times, y=pricesbn, mode='lines', name=bn_kind), row=1, col=1)
        fig.add_trace(go.Scatter(x=times, y=pricesbm, mode='lines', name=other_kind), row=1, col=1)
        fig.add_trace(go.Scatter(x=times, y=pricesdiff, mode='lines', name='Price_diff'), row=2, col=1)
        fig.add_trace(go.Scatter(x=times, y=pricesdiffPercent, mode='lines', name='Price_diff_percent'), row=3, col=1)

        min_value_diff = min(pricesdiff)
        max_value_diff = max(pricesdiff)
        min_value_diff_percent=min(pricesdiffPercent)
        max_value_diff_percent=max(pricesdiffPercent)
        range_value_diff = max(abs(min_value_diff), abs(max_value_diff))
        range_value_diff_percent=max(abs(min_value_diff_percent), abs(max_value_diff_percent))
        yaxis_range_diff = [-range_value_diff, range_value_diff]
        yaxis_range_diff_percent= [-range_value_diff_percent, range_value_diff_percent]
        mid_value_diff = 0
        mid_value_diff_percent=0

        fig.update_yaxes(title_text='Price', range=yaxis_range_diff, row=2, col=1)
        fig.update_yaxes(fixedrange=True, row=2, col=1, range=[mid_value_diff - range_value_diff, mid_value_diff + range_value_diff])
        fig.update_yaxes(title_text='Price_percent_base_bn', range=yaxis_range_diff_percent, row=3, col=1)
        fig.update_yaxes(fixedrange=True, row=3, col=1, range=[mid_value_diff_percent - range_value_diff_percent, mid_value_diff_percent + range_value_diff_percent])

        fig.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),  # 调整上、下、左、右的间距值
            xaxis_title='Timestamp',
            title='Price Movement'
        )

        fig.write_image(output_file)
        fig.show()