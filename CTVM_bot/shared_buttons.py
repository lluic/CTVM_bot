from telegram import InlineKeyboardButton


class SharedButtons:
    @staticmethod
    def back_to_home_button(text: str = "🏠  Home"):
        return InlineKeyboardButton(text, callback_data="home")

    @staticmethod
    def back_to_list_button(text: str = "⬅️  Torna alla lista"):
        return InlineKeyboardButton(text, callback_data="list")

    @staticmethod
    def back_to_restaurant_button(
        restaurant_name: str,
        text: str = "⬅️  Torna al ristorante",
    ):
        return InlineKeyboardButton(
            text,
            callback_data=f"restaurant:{restaurant_name}",
        )

    @staticmethod
    def add_restaurant_button(text: str = "➕  Aggiungi ristorante"):
        return InlineKeyboardButton(text, callback_data="add_restaurant")
