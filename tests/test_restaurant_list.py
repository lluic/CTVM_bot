from CTVM_bot.restaurant_list import RestaurantList


def test_read_write_restaurant_list_json():
    RestaurantList().read_restaurant_list_json()

    RestaurantList().write_restaurant_list_json()
