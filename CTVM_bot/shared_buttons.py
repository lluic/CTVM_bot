from telegram import InlineKeyboardButton


class SharedButtons:
    @staticmethod
    def back_to_home_button():
        button = InlineKeyboardButton("🏠  Home", callback_data="home")
        return button

    @staticmethod
    def back_to_restaurant_button(restaurant_name: str):
        return InlineKeyboardButton(
            "⬅️  Torna al ristorante", callback_data=f"restaurant:{restaurant_name}"
        )
