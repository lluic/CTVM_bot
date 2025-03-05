from CTVM_bot.restaurant_data_manager import RestaurantDataManager


def test_restaurant_list_json():
    RestaurantDataManager().read_restaurant_list_json()
    RestaurantDataManager().add_restaurant(
        name="Restaurant TEST",
        link="https://maps.app.goo.gl/NFxxWXBf2Y1ztfCC7",
        rating=4.5,
        total_votes=10,
    )

    assert RestaurantDataManager().has("Restaurant TEST")
    assert (
        RestaurantDataManager().get_restaurant("Restaurant TEST").name
        == "Restaurant TEST"
    )
    assert (
        RestaurantDataManager().get_restaurant("Restaurant TEST").link
        == "https://maps.app.goo.gl/NFxxWXBf2Y1ztfCC7"
    )
    assert RestaurantDataManager().get_restaurant("Restaurant TEST").rating == 4.5
    assert RestaurantDataManager().get_restaurant("Restaurant TEST").total_votes == 10

    RestaurantDataManager().update_rating_and_votes(
        name="Restaurant TEST", rating=3.5, total_votes=2
    )

    assert RestaurantDataManager().get_restaurant("Restaurant TEST").rating == 3.5
    assert RestaurantDataManager().get_restaurant("Restaurant TEST").total_votes == 2

    RestaurantDataManager().remove_restaurant(name="Restaurant TEST")
    RestaurantDataManager().write_restaurant_list_json()
