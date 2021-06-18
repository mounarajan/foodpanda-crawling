import requests
import json
import logging
import logging.handlers as handlers
import time
import pika
import os
from datetime import datetime
log = logging.getLogger('foodpanda_sg')
log.setLevel(logging.INFO)

## Here we define our formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logHandler = handlers.TimedRotatingFileHandler('foodpanda_sg_menu.log', when='H', interval=1, backupCount=10)
logHandler.setLevel(logging.INFO)
## Here we set our logHandler's formatter
logHandler.setFormatter(formatter)

log.addHandler(logHandler)

def request_module(url):
	rest_id = url.split("/")[-2]
	#https://sg.fd-api.com/api/v5/vendors/zuac?include=menus&language_id=1&dynamic_pricing=0&opening_type=delivery&latitude=1.304532&longitude=103.860341
	api_url = "https://sg.fd-api.com/api/v5/vendors/"+rest_id+"?include=menus&language_id=1&dynamic_pricing=0&opening_type=delivery"
	log.info("Getting response for url "+url)
	headers = {
	  'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
	  'Accept': 'application/json, text/plain, */*',
	  'Accept-Language': 'en-US,en;q=0.5',
	  'X-FP-API-KEY': 'volo',
	  'dps-session-id': 'eyJzZXNzaW9uX2lkIjoiN2NhZTViNTI3OTQ1ZGZkNjNjMzZlYTM2Mzk3Y2U5NDgiLCJwZXJzZXVzX2lkIjoiMTYyMzMxMDE5MC45Nzk4MTkyNjc1LlFGVEwwYjZWMDQiLCJ0aW1lc3RhbXAiOjE2MjMzOTcxMzl9',
	  'x-disco-client-id': 'web',
	  'Origin': 'https://www.foodpanda.sg',
	  'Referer': 'https://www.foodpanda.sg/',
	  'Connection': 'keep-alive',
	  'TE': 'Trailers'
	}

	response = requests.request("GET", api_url, headers=headers)
	now = datetime.now()
	dt_string = now.strftime("%d-%m-%Y-%H:%M:%S")
	fs = open(str(rest_id)+'_'+str(dt_string)+'.json','w')
	fs.write(response.content.decode("utf-8"))
	fs.close()
	#return response.content.decode("utf-8")

def menu_info_extraction(msg):
	log.info("url processing "+msg)
  

	request_module(str(msg))
	log.info("url processing completed "+msg)
  

# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672/%2f')
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel() # start a channel
channel.queue_declare(queue='urls') # Declare a queue

# create a function which is called on incoming messages
def callback(ch, method, properties, body):
	menu_info_extraction(body)

# set up subscription on the queue
channel.basic_consume('urls',
  callback,
  auto_ack=True)

# start consuming (blocks)
channel.start_consuming()
connection.close()