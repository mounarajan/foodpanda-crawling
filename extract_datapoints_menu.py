import os
import json
import datetime

fs = open('sample_menu_data.json','r').read()
menu_json_data = json.loads(fs)
if menu_json_data.get("status_code","") == 200:
	if menu_json_data.get("status_code","") == 200:
		menu_info = dict()
		menu_info["source"] = "foodpanda"
		menu_info["country_code"] = "SG"
		menu_info["restaurant_id"] = menu_json_data.get("data",[]).get("code","")
		time_converted = datetime.datetime.utcnow()
		menu_info["timestamp"] = time_converted.isoformat("T") + "Z"
		items_list = list()
		c = 0
		for menu_info1 in menu_json_data.get("data",[]).get("menus",[]):
			for menu in menu_info1.get("menu_categories"):
				for menu_products in menu.get("products"):
					c = c + 1
					item_dict = dict()
					item_dict["item_name"] = menu_products.get("name")
					item_dict["item_id"] = menu_products.get("code")
					item_dict["description"] = menu_products.get("description")
					images = list()
					for img in menu_products.get("images",[]):
						img.get("image_url","")
					if len(images) >= 1:
						item_dict["image_url"] = images[0]
					item_dict["price_unit"] = "SGD"
					item_dict["price"] = menu_products.get("product_variations")[0].get("price","")
					if menu_products.get("is_sold_out",False) is False:

						item_dict["available"] = True
					else:
						item_dict["available"] = False
					sss
					item_dict["alcohol"] = menu_products.get("is_alcoholic_item","")
					items_list.append(item_dict)
		menu_info["items"] = items_list

		
		print menu_info

