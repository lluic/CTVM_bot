import json
from pathlib import Path

restaurant_list_json_path = Path("CTVM_bot/data/restaurant_list.json")


def read_restaurant_list_json():
    with open(restaurant_list_json_path, "r") as f:
        restaurant_list_dict = json.load(f)
    return restaurant_list_dict


def write_restaurant_list_json(restaurants: dict):
    with open(restaurant_list_json_path, "w") as f:
        json.dump(restaurants, f)
