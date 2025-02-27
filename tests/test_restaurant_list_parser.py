from CTVM_bot.restaurant_list_parser import (
    read_restaurant_list_json,
    write_restaurant_list_json,
)


def test_read_write_restaurant_list_json():
    asd = read_restaurant_list_json()

    write_restaurant_list_json(asd)
