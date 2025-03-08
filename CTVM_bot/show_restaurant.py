import validators
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from CTVM_bot.restaurant_data_manager import RestaurantDataManager
from CTVM_bot.shared_buttons import SharedButtons


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
                "🌍  Apri su Maps",
                url=restaurant.link,
            )
        else:
            location_button = InlineKeyboardButton(
                "🌐  Aggiungi posizione",
                callback_data=f"edit_location:{restaurant_name}",
            )
        poll_button = InlineKeyboardButton(
            "📝  Avvia sondaggio",
            callback_data=f"poll:{restaurant_name}",
        )
        edit_button = InlineKeyboardButton(
            "✏️  Modifica",
            callback_data=f"edit_restaurant:{restaurant_name}",
        )
        delete_button = InlineKeyboardButton(
            "⚠️  Elimina  ⚠️",
            callback_data=f"delete_restaurant:{restaurant_name}",
        )
        back_to_list_button = InlineKeyboardButton(
            "⬅️  Torna alla lista",
            callback_data=f"list",
        )
        buttons = [
            [location_button],
            [poll_button],
            [edit_button],
            [delete_button],
            [back_to_list_button],
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        await query.message.reply_text(f"🍽️  {restaurant_name}", reply_markup=keyboard)

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
            [SharedButtons.back_to_restaurant_button(restaurant_name)],
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        await query.message.reply_text(
            f"Modifica {restaurant_name}", reply_markup=keyboard
        )

    @staticmethod
    async def delete_restaurant(
        query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE
    ):
        restaurant_name = query.data.split(":")[1]
        if not RestaurantDataManager().has(restaurant_name):
            await query.message.reply_text(text="Errore: ristorante non trovato.")
            return

        buttons = [
            [
                InlineKeyboardButton(
                    "Elimina", callback_data=f"confirm_delete:{restaurant_name}"
                )
            ],
            [
                InlineKeyboardButton(
                    "Annulla",
                    callback_data=f"cancel_delete",
                )
            ],
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        await query.message.reply_text(
            f"Sicuro di voler eliminare {restaurant_name}?!", reply_markup=keyboard
        )

    @staticmethod
    async def confirm_delete(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
        await query.answer()
        restaurant_name = query.data.split(":")[1]
        if not RestaurantDataManager().has(restaurant_name):
            await query.message.reply_text(text="Errore: ristorante non trovato.")
            return

        RestaurantDataManager().remove_restaurant(restaurant_name)
        await query.message.reply_text(text="Ristorante eliminato con successo.")

    @staticmethod
    async def cancel_delete(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
        await query.message.reply_text(text="Operazione annullata.")
