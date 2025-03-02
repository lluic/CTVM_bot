import json
from pathlib import Path


class Restaurant:
    def __init__(self, name: str, link: str, rating: float | None, total_votes: int):
        self.name = name
        self.link = link
        self.rating = rating
        self.total_votes = total_votes


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

        self.json_db_path = Path("CTVM_bot/data/restaurants_db.json")
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
        self.restaurants.append(
            Restaurant(
                name=name,
                link=link,
                rating=rating,
                total_votes=total_votes,
            )
        )
        self.write_restaurant_list_json()

    def remove_restaurant(self, name: str):
        self.restaurants = [r for r in self.restaurants if r.name != name]
        self.write_restaurant_list_json()

    def has(self, name: str) -> bool:
        return any(r.name == name for r in self.restaurants)

    def get_restaurant(self, name: str) -> Restaurant | None:
        return next((r for r in self.restaurants if r.name == name), None)

    def update_rating_and_votes(self, name: str, rating: float, total_votes: int):
        for r in self.restaurants:
            if r.name == name:
                r.rating = rating
                r.total_votes = total_votes
                break
        self.write_restaurant_list_json()

    def read_restaurant_list_json(self):
        self.restaurants = []
        with open(self.json_db_path, "r") as f:
            restaurants_dict = json.load(f)
        for item in restaurants_dict:
            restaurant = Restaurant(
                name=item["name"],
                link=item["link"],
                rating=item["rating"],
                total_votes=item["total_votes"],
            )
            self.restaurants.append(restaurant)

    def write_restaurant_list_json(self):
        restaurants_dict = []
        for restaurant in self.restaurants:
            restaurant_dict = {
                "name": restaurant.name,
                "link": restaurant.link,
                "rating": restaurant.rating,
                "total_votes": restaurant.total_votes,
            }
            restaurants_dict.append(restaurant_dict)
        with open(self.json_db_path, "w") as f:
            json.dump(restaurants_dict, f)
