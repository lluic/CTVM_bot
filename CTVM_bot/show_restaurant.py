import validators
from telegram import Update, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from CTVM_bot.restaurant_data_manager import RestaurantDataManager


class ShowRestaurant:
    @staticmethod
    async def show_restaurant(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
        restaurant_name = query.data.split(":")[1]
        if not RestaurantDataManager().has(restaurant_name):
            await query.message.reply_text(text="Errore: ristorante non trovato.")
            return

        restaurant = RestaurantDataManager().get_restaurant(restaurant_name)
        if validators.url(restaurant.link):
            location_button = InlineKeyboardButton(
                "Apri su Maps",
                url=restaurant.link,
            )
        else:
            location_button = InlineKeyboardButton(
                "Aggiungi posizione",
                callback_data=f"edit_location:{restaurant_name}",
            )
        poll_button = InlineKeyboardButton(
            "Apri sondaggio",
            callback_data=f"poll:{restaurant_name}",
        )
        edit_button = InlineKeyboardButton(
            "Modifica",
            callback_data=f"edit_restaurant:{restaurant_name}",
        )
        buttons = [
            [location_button],
            [poll_button],
            [edit_button],
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        await query.message.reply_text(f"{restaurant_name}", reply_markup=keyboard)

    @staticmethod
    async def edit_restaurant(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
        restaurant_name = query.data.split(":")[1]
        if not RestaurantDataManager().has(restaurant_name):
            await query.message.reply_text(text="Errore: ristorante non trovato.")
            return

        buttons = [
            [
                InlineKeyboardButton(
                    "Modifica nome", callback_data=f"edit_name:{restaurant_name}"
                )
            ],
            [
                InlineKeyboardButton(
                    "Modifica posizione",
                    callback_data=f"edit_location:{restaurant_name}",
                )
            ],
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        await query.message.reply_text(
            f"Modifica {restaurant_name}", reply_markup=keyboard
        )
