import os
import json
import datetime

fs = open('sample_res.json','r').read()
menu_json_datas = json.loads(fs)
if menu_json_datas.get("status_code","") == 200:
	for menu_json_data in menu_json_datas.get("data",{}).get("items",[]):
		menu_info = dict()
		menu_info["source"] = "foodpanda"
		menu_info["country_code"] = "SG"
		menu_info["restaurant_url"] = menu_json_data.get("web_path","")
		menu_info["menu_url"] = menu_json_data.get("web_path","")
		menu_info["chain"] = menu_json_data.get("chain",{"name":""}).get("name")
		menu_info["name"] = menu_json_data.get("name","")
		menu_info["latitude"] = menu_json_data.get("latitude","")
		menu_info["longitude"] = menu_json_data.get("longitude","")
		menu_info["address"] = menu_json_data.get("address","")
		menu_info["postal_code"] = menu_json_data.get("postal_code","")
		menu_info["city"] = menu_json_data.get("city",{"name":""}).get("name")
		images = list()
		images.append(menu_json_data.get("hero_image",""))
		images.append(menu_json_data.get("hero_listing_image",""))
		menu_info["image_url"] = images
		order_location_list = list()
		
		del_info = dict()
		del_info["delivery_fee"] = menu_json_data.get("minimum_delivery_fee","")
		del_info["delivery_fee"] = menu_json_data.get("minimum_delivery_time","")
		del_info["distance"] = menu_json_data.get("data",{}).get("distance","")
		order_location_list.append(del_info)
		menu_info["order_location"] = order_location_list

		del_time = list()
		del_method = list()
		for schedule in menu_json_data.get("schedules",[]):
			if schedule.get("opening_type","") in del_method:
				pass
			else:
				del_method.append(schedule.get("opening_type",""))
			if schedule.get("opening_type","") == "delivering":
				if schedule.get("weekday") == 1:
					del_time.append("Sunday: "+schedule.get("opening_time")+"-"+schedule.get("closing_time"))
				elif schedule.get("weekday") == 2:
					del_time.append("Monday: "+schedule.get("opening_time")+"-"+schedule.get("closing_time"))
				elif schedule.get("weekday") == 3:
					del_time.append("Tuesday: "+schedule.get("opening_time")+"-"+schedule.get("closing_time"))
				elif schedule.get("weekday") == 4:
					del_time.append("Wednesday: "+schedule.get("opening_time")+"-"+schedule.get("closing_time"))
				elif schedule.get("weekday") == 5:
					del_time.append("Thrusday: "+schedule.get("opening_time")+"-"+schedule.get("closing_time"))
				if schedule.get("weekday") == 6:
					del_time.append("Friday: "+schedule.get("opening_time")+"-"+schedule.get("closing_time"))
				if schedule.get("weekday") == 7:
					del_time.append("Saturday: "+schedule.get("opening_time")+"-"+schedule.get("closing_time"))
		menu_info["opening_hours"] = del_time
		menu_info["fulfillment_methods"] = del_method
		cusine_list = list()
		for cusine in menu_json_data.get("cuisines",[]):
			cusine_list.append(cusine.get("name",""))
		menu_info["cuisine_type"] = cusine_list

		menu_info["rating"] = menu_json_data.get("rating","")
		menu_info["number_of_reviews"] = menu_json_data.get("review_number","")
		menu_info["restaurant_id"] = menu_json_data.get("code","")
		menu_info["website"] = menu_json_data.get("website","")
		menu_info["pickup_enabled"] = menu_json_data.get("is_pickup_enabled","")
		menu_info["transportation_direction"] = menu_json_data.get("accepts_instructions","")
		menu_info["currency"] = "SGD"
		time_converted = datetime.datetime.utcnow()
		menu_info["timestamp"] = time_converted.isoformat("T") + "Z"
		try:
			menu_info["halal"] = menu_json_data.get("food_characteristics",[{"is_halal":""}])[0].get("is_halal")
		except:
			menu_info["halal"] = ""
		print menu_info

