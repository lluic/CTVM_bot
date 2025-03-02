from CTVM_bot.restaurant_list import RestaurantList


def test_restaurant_list_json():
    RestaurantList().read_restaurant_list_json()
    RestaurantList().add_restaurant(
        name="Restaurant TEST",
        link="https://maps.app.goo.gl/NFxxWXBf2Y1ztfCC7",
        rating=4.5,
        total_votes=10,
    )

    assert RestaurantList().has("Restaurant TEST")
    assert RestaurantList().get_restaurant("Restaurant TEST").name == "Restaurant TEST"
    assert (
        RestaurantList().get_restaurant("Restaurant TEST").link
        == "https://maps.app.goo.gl/NFxxWXBf2Y1ztfCC7"
    )
    assert RestaurantList().get_restaurant("Restaurant TEST").rating == 4.5
    assert RestaurantList().get_restaurant("Restaurant TEST").total_votes == 10

    RestaurantList().update_rating_and_votes(
        name="Restaurant TEST", rating=3.5, total_votes=2
    )

    assert RestaurantList().get_restaurant("Restaurant TEST").rating == 3.5
    assert RestaurantList().get_restaurant("Restaurant TEST").total_votes == 2

    RestaurantList().remove_restaurant(name="Restaurant TEST")
    RestaurantList().write_restaurant_list_json()
