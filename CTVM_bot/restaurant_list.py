import json
from pathlib import Path


class RestaurantList:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RestaurantList, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.json_db_path = Path("CTVM_bot/data/restaurant_list.json")
        self.restaurants = []
        self.read_restaurant_list_json()
        self._initialized = True

    def add_restaurant(
        self,
        name: str,
        link: str,
        rating: float | None,
        total_votes: int,
    ):
        self.restaurants = {
            "name": name,
            "link": link,
            "rating": rating,
            "total_votes": total_votes,
        }
        self.write_restaurant_list_json()

    def remove_restaurant(self, name: str):
        self.restaurants = [r for r in self.restaurants if r["name"] != name]
        self.write_restaurant_list_json()

    def has(self, name: str) -> bool:
        return any(r.name == name for r in self.restaurants)

    def update_rating_and_votes(self, name: str, rating: float, total_votes: int):
        for r in self.restaurants:
            if r.name == name:
                r.rating = rating
                r.total_votes = total_votes
                break
        self.write_restaurant_list_json()

    def read_restaurant_list_json(self):
        with open(self.json_db_path, "r") as f:
            self.restaurants = json.load(f)

    def write_restaurant_list_json(self):
        with open(self.json_db_path, "w") as f:
            json.dump(self.restaurants, f)
