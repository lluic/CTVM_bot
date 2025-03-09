from telegram import Update, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from CTVM_bot.restaurant_data_manager import RestaurantDataManager
from CTVM_bot.shared_buttons import SharedButtons
from CTVM_bot.utils import rating_to_stars


class ShowList:
    @staticmethod
    async def show_list(
        update: Update | CallbackQuery, context: ContextTypes.DEFAULT_TYPE
    ):
        """Mostra la lista dei ristoranti e la loro valutazione."""
        restaurants = RestaurantDataManager().restaurants
        if not restaurants:
            await update.message.reply_text("Errore: Nessun ristorante disponibile.")
            return

        buttons = []
        for r in restaurants:
            button_string = r.name
            if r.rating is not None and r.total_votes > 0:
                stars = rating_to_stars(r.rating)
                button_string += f"  {stars} ({r.rating:.1f})"
            buttons.append(
                [
                    InlineKeyboardButton(
                        button_string, callback_data=f"restaurant:{r.name}"
                    )
                ]
            )

        buttons.append([SharedButtons.back_to_home_button()])

        await update.message.reply_text(
            "Seleziona un ristorante per visualizzarlo o modificarlo:",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
