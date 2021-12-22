# Producer example

from threading import Event
from format_cef._cef.base import datetime_sanitiser
import pandas as pd
import psycopg2
from pandas.io.json import json_normalize
import json
import pika
import requests
from format_cef import format_cef
import maya


#Open Conection with BD
conn = psycopg2.connect(database="postgres", user="db-admin", password="admin", host="127.0.0.1", port="5432")

#DF - Get all the information from the dictionary in the BD
df_dict = pd.read_sql_query("SELECT * FROM  {}".format('"Dictionary"'),con=conn)

#DF Queue
df_queue = pd.read_sql_query("SELECT DISTINCT queue FROM  {}".format('"Dictionary"'),con=conn) #Name of each row
lqueue = df_queue.values.tolist()  
list_queue = [item for sublist in lqueue for item in sublist]

conn.close() #Close database connection

#In our case, this step was necessary because the imported json comes with some flaws.
#Read json file as text as json comes invalidly from azure storage explorer
with open('/home/alan/Documents/Code/Metrics-simulator/publish/PT1H.json') as f:
  rawdata = [line.rstrip('\n') for line in f] #Break json into a string list


log_list = []
for log in rawdata:#Scan raw data and transform string into dictionary
    log_list.append(json.loads(log))
df_log = pd.DataFrame.from_records(log_list)#Collect everything that was made into a dictionary and assemble a DF
df_log = df_log[['metricName','time','count','total','minimum','maximum','average']] #Add filters to collect the necessary information in the DF

## Compare the DF of Logs (json) with the database (Postgres) where the taxonomy classification is
df_result = pd.merge(df_log, df_dict, how='left', on=['metricName','metricName'])


df_result.to_csv('teste_merge.csv')
#print(df_result)


#AUTHENTICATION PROCEDURE


#Open connection with RabbitMQ
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/',credentials))
channel = connection.channel()

#Scroll through the list with the queue names, and create the queues in RabbitMQ
for queue in list_queue:
    channel.queue_declare(queue=str(queue), exclusive=False)

    

#Check the queue with the queues already registered in the dictionary, and then send the metrics to the correct queues in RabbitMQ
def send_msg(data, queue):
    for ind in data.index:
        if data['queue'][ind]== queue:  
            args = ("Azure","IoTHub","1.0",str(data['metricName'][ind]),str(data['metric'][ind]),4,)
            msg = format_cef(*args, extensions={'destinationProcessId':int(data['count'][ind]), 'destinationUserPrivileges':'count','deviceCustomFloatingPoint2': float(data['total'][ind]),'deviceCustomFloatingPoint2Label':'total','deviceCustomFloatingPoint1':float(data['minimum'][ind]),
            'deviceCustomFloatingPoint1Label': 'minimum', 'deviceCustomFloatingPoint3':float(data['maximum'][ind]), 'deviceCustomFloatingPoint3Label':'maximum', 'deviceCustomFloatingPoint4':float(data['maximum'][ind]),'deviceCustomFloatingPoint4Label': 'average',
            'deviceCustomDate1':maya.parse(data['time'][ind],"%Y-%m-%d %H:%M:%S").datetime(), 'deviceCustomDate1Label':'time'})
            channel.basic_publish(exchange='',
                        routing_key=queue,
                        body= msg)
            print('{} Send'.format(msg))
    print('All messages  -- {} Send'.format(queue))
    

#Scrolls through the list of queues
for queue in list_queue:
    send_msg(df_result, queue)
    #df_result.to_csv('cef_test.csv')





