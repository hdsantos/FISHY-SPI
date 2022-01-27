# Producer example
import os
from threading import Event
from format_cef._cef.base import datetime_sanitiser
import pandas as pd
import psycopg2
from pandas.io.json import json_normalize
import json
import requests
from format_cef import format_cef
import maya
import time


#Open Conection with BD
conn = psycopg2.connect(database="keycloak", user="keycloak", password="password", host="127.0.0.1", port="25432")

# DF - Get all the information from the dictionary in the BD
df_dict = pd.read_sql_query("SELECT * FROM  {}".format('"dictionary_csv"'),con=conn)

# DF Queue
df_queue = pd.read_sql_query("SELECT DISTINCT queue FROM  {}".format('"dictionary_csv"'),con=conn) #Name of each row
lqueue = df_queue.values.tolist()
# Get the Queues names to create with Rabbit later
list_queue = [item for sublist in lqueue for item in sublist]

conn.close() #Close database connection

#In our case, this step was necessary because the imported json comes with some flaws.
#Read json file as text as json comes invalidly from azure storage explorer
with open('/home/alan/Documents/Code/FISHY-SPI/producer/PT1H.json') as f:
  rawdata = [line.rstrip('\n') for line in f] #Break json into a string list

#Creating Dataframe
log_list = []
for log in rawdata:#Scan rawdata and transform string into dictionary
    log_list.append(json.loads(log))
df_log = pd.DataFrame.from_records(log_list)#Collect everything that was made into a dictionary and assemble a DF
df_log = df_log[['metricName','time','count','total','minimum','maximum','average']] #Add filters to collect the necessary information in the DF

## Compare the DF of Logs (json) with the database (Postgres) where the taxonomy classification is
df_result = pd.merge(df_log, df_dict, how='left', on=['metricName','metricName'])
df_result.to_csv('teste_merge.csv')
#print(df_result)


#API Gateway authentication and configuration process.

#Environment variables
host = os.environ["HOST_IP"]
keycloak_kong_client_secret = os.environ["CLIENT_SECRET"]
keycloak_realm = os.environ["REALM"]

#Create Queues
def createQueues(queues):
    headers = {"content-type:application/json"}
    for queue in queues:
        r_createqueue=requests.put("http://localhost:8080/api/queues/%2f/{}".format(queue), auth=('guest', 'guest'))
        
createQueues(list_queue)


#1. Creating services - OIDC

def createservice_oidc():
    r_verify=requests.get("http://localhost:8000/mock")
    #print(r_verify)
    if r_verify.status_code == 404:
        print("Creating services")
        r=requests.post("http://localhost:8001/services", {"name":"mock-service", "url":"http://mockbin.org/request"})
        #print(r)
        r_data=json.loads(r.content)
        r_id=r_data["id"]
        #print(r_id)
        #print("Create Route...")
        r_route = requests.post(r"http://localhost:8001/services/{}/routes".format(r_id),{"paths[]":"/mock"})
        print(r_route)
        #print("Enabling OIDC plugin with client parameters")
        r_oidc=requests.post("http://localhost:8001/plugins", {"name":"oidc", "config.client_id":"kong","config.client_secret":keycloak_kong_client_secret, "config.bearer_only":"yes", "config.realm": keycloak_realm,
        "config.introspection_endpoint": "http://{}:8180/auth/realms/{}/protocol/openid-connect/token/introspect".format(host,keycloak_realm),
        "config.discovery":"http://{}:8180/auth/realms/{}/.well-known/openid-configuration".format(host,keycloak_realm)})
        #print(r_oidc.status_code)
    else:
        print("Error or service already started")
         
createservice_oidc()

#Creatinng services - AMQP
def createservice_amqp(queues):
    for queue in queues:
        r=requests.post("http://localhost:8001/services", {"name":"{}".format(queue), "url":"amqp://rabbitmq:5672"})
        #print(r.status_code)
        if r.status_code not in [401, 404, 409]:
            print("Creating services - AMQP")
            #print(r)
            r_data=json.loads(r.content)
            r_id=r_data["id"]
            #print(r_id)
            #print("Create Route...")
            r_route = requests.post(r"http://localhost:8001/services/{}/routes".format(r_id, queue),{"paths[]":"/{}".format(queue)})
            #print(r_route)
            print("Enabling OIDC plugin with client parameters")
            r_amqp=requests.post("http://localhost:8001/services/{}/plugins/".format(queue), {"name":"amqp", "config.routingkey":"{}".format(queue)})
            #print(r_amqp.status_code)
        else:
            print("Error or service already started")

createservice_amqp(list_queue)

#2. Request Token - Keycloak

def get_token(cliend_id, client_secret):
    
    r_login = requests.post("http://{}:8180/auth/realms/experimental/protocol/openid-connect/token".format(host), {"Content-Type":"application/x-www-form-urlencoded", "grant_type":"client_credentials",
    "client_id":"FISHY-prod-ex", "client_secret":"xzONWxH6RQ2s2MNlvVNLMTkvtjBJ391e"})
    print(r_login.status_code)
    if r_login.status_code == 401:
        print("Access denied")
    else:
        r_login_data = json.loads(r_login.content)
        r_introspct = r_login_data["access_token"]
        return(r_introspct) 
        print(r_introspct)
token = get_token("FISHY-prod-ex", "xzONWxH6RQ2s2MNlvVNLMTkvtjBJ391e")
print(token)
    
#Check the queue with the queues already registered in the dictionary, and then send the metrics to the correct queues in RabbitMQ
def send_msg(host, token, data, queue):
    if token == None:
        print("Token not found")
    else:
        headers = {"Accept":"application/json", "Authorization":"Bearer {}".format(token)}
        for ind in data.index:
            if data['queue'][ind]== queue:  
                args = ("Azure","IoTHub","1.0",str(data['metricName'][ind]),str(data['metric'][ind]),4,)
                msg = format_cef(*args, extensions={'destinationProcessId':int(data['count'][ind]), 'destinationUserPrivileges':'count','deviceCustomFloatingPoint2': float(data['total'][ind]),'deviceCustomFloatingPoint2Label':'total','deviceCustomFloatingPoint1':float(data['minimum'][ind]),
                'deviceCustomFloatingPoint1Label': 'minimum', 'deviceCustomFloatingPoint3':float(data['maximum'][ind]), 'deviceCustomFloatingPoint3Label':'maximum', 'deviceCustomFloatingPoint4':float(data['maximum'][ind]),'deviceCustomFloatingPoint4Label': 'average',
                'deviceCustomDate1':maya.parse(data['time'][ind],"%Y-%m-%d %H:%M:%S").datetime(), 'deviceCustomDate1Label':'time'})
                #inicio = time.time()
                r_msg = requests.post("http://{}:8000/{}".format(host, queue), data=msg, headers=headers) 
                #fim = time.time()
                #print(fim-inicio)
                # print(r_msg.content)
                # print(r_msg.status_code)
                # print('{} Send'.format(msg))
    print('All messages  -- {} Send'.format(queue))
    

#Scrolls through the list of queues
for queue in list_queue:
    inicio = time.time()
    send_msg(host, token, df_result, queue)
    #df_result.to_csv('cef_test.csv')
    fim = time.time()
    print(fim-inicio)#Time between sending the message and receiving it by rabbitmq
