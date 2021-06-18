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

logHandler = handlers.TimedRotatingFileHandler('foodpanda_sg_spidering.log', when='H', interval=1, backupCount=10)
logHandler.setLevel(logging.INFO)
## Here we set our logHandler's formatter
logHandler.setFormatter(formatter)

log.addHandler(logHandler)

url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost/%2f')
params = pika.URLParameters(url)
params.socket_timeout = 5

connection = pika.BlockingConnection(params) # Connect to CloudAMQP
channel = connection.channel() # start a channel
channel.queue_declare(queue='urls') # Declare a queue
# send a message

urls_dup = set()

def request_module(latitude_val,longitude_val,offset):

    url = "https://disco.deliveryhero.io/listing/api/v1/pandora/vendors?latitude="+latitude_val+"&longitude="+longitude_val+"&language_id=1&include=characteristics&dynamic_pricing=0&configuration=Variant2&country=sg&customer_id=&customer_hash=&budgets=&cuisine=&sort=&food_characteristic=&use_free_delivery_label=false&vertical=restaurants&limit=300&offset="+str(offset)+"&customer_type=regular"
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

    response = requests.request("GET", url, headers=headers)
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y-%H:%M:%S")
    fs = open(latitude_val+'_'+longitude_val+'_'+str(offset)+'_'+str(dt_string)+'.json','w')
    fs.write(response.content.decode("utf-8"))
    fs.close()
    return response.content.decode("utf-8")

def spider_urls(zone_val):
    if len(zone_val) > 1:
        latitude_val = zone_val[0]
        longitude_val = zone_val[1]
        get_links = 1
        offset = 0
        count = 0
        count_final = 0
        while get_links == 1:
            json_resp = request_module(latitude_val,longitude_val,offset)
            json_resp = json.loads(json_resp)
            if json_resp.get("status_code","") == 200:

                for loop_data in json_resp.get("data",{}).get("items",[]):
                    restaurant_listing_data = dict()
                    restaurant_listing_data["input_latitude"] = latitude_val
                    restaurant_listing_data["input_longitude"] = longitude_val
                    restaurant_listing_data["listing_id"] = loop_data.get("id","")
                    restaurant_listing_data["listing_city"] = loop_data.get("city",{})
                    restaurant_listing_data["listing_cuisines"] = loop_data.get("cuisines","")
                    restaurant_listing_data["listing_food_characteristics"] = loop_data.get("food_characteristics","")
                    restaurant_listing_data["listing_latitude"] = loop_data.get("latitude","")
                    restaurant_listing_data["listing_longitude"] = loop_data.get("longitude","")
                    restaurant_listing_data["listing_minimum_delivery_fee"] = loop_data.get("minimum_delivery_fee","")
                    restaurant_listing_data["listing_minimum_delivery_time"] = loop_data.get("minimum_delivery_time","")
                    restaurant_listing_data["listing_minimum_order_amount"] = loop_data.get("minimum_order_amount","")
                    restaurant_listing_data["listing_minimum_pickup_time"] = loop_data.get("minimum_pickup_time","")
                    restaurant_listing_data["listing_name"] = loop_data.get("name","")
                    restaurant_listing_data["listing_post_code"] = loop_data.get("post_code","")
                    restaurant_listing_data["listing_rating"] = loop_data.get("rating","")
                    restaurant_listing_data["listing_review_number"] = loop_data.get("review_number","")
                    restaurant_listing_data["listing_url"] = loop_data.get("redirection_url","")
                    restaurant_listing_data["listing_score"] = loop_data.get("score","")
                    restaurant_listing_data["listing_service_fee_percentage_amount"] = loop_data.get("service_fee_percentage_amount","")
                    restaurant_listing_data["listing_service_tax_percentage_amount"] = loop_data.get("service_tax_percentage_amount","")
                    restaurant_listing_data["listing_special_days"] = loop_data.get("special_days",[])
                    restaurant_listing_data["listing_web_path"] = loop_data.get("web_path","")
                    restaurant_listing_data["listing_website"] = loop_data.get("website","")
                    restaurant_listing_data["listing_has_online_payment"] = loop_data.get("has_online_payment","")
                    restaurant_listing_data["listing_discounts_info"] = loop_data.get("discounts","")
                    url_crawled = loop_data.get("redirection_url","")
                    res_zipcode = loop_data.get("post_code","")
                    for k,v in loop_data.items():
                        if k.startswith("is_"):
                            restaurant_listing_data["listing_"+k] = v

                    file_write = open('foodpanda_my_final_json_data.json','a')
                    file_write.write(json.dumps(restaurant_listing_data)+"\n")
                    file_write.close()
                    if url_crawled+"_"+res_zipcode in urls_dup:
                        pass
                    else:
                        urls_dup.add(url_crawled+"_"+res_zipcode)
                        channel.basic_publish(exchange='', routing_key='urls', body=url_crawled)
                    log.info("url "+url_crawled+" sent to urls queue")

                try:
                    count_final = json_resp.get("data",{}).get("available_count","")
                    count = count + json_resp.get("data",{}).get("returned_count","")
                    if count >= count_final:
                        get_links = 0
                        log.info("All availble results are fetched for "+latitude_val+","+longitude_val)
                    else:
                        get_links = 1
                        offset = offset + 300
                        log.info("getting offset "+str(offset)+" for "+latitude_val+","+longitude_val)
                except Exception as e:
                    log.error("Some error doing pagination "+e+" for "+latitude_val+","+longitude_val)
            else:
                get_links = 0
                log.error("No data for "+latitude_val+","+longitude_val)


                    



    else:
        log.error("Latitude and longitude both required to get valid link please provide both")


zones = []
file_open = open("sg_zipcodes.txt","r")
for line in file_open:
    zones.append(line.strip().split(","))
for zone in zones:
    spider_urls(zone)

connection.close()


