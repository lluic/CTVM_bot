from telegram import Update, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from CTVM_bot.restaurant_data_manager import RestaurantDataManager
from CTVM_bot.shared_buttons import SharedButtons

# Define states
ASK_NAME = 1


class AddRestaurant:
    @staticmethod
    async def add_restaurant_start(
        update: Update | CallbackQuery, context: ContextTypes.DEFAULT_TYPE
    ):
        """Starts the restaurant addition conversation."""
        # Handle both command and button press (callback_query)
        if update.message:
            message = update.message  # Command
        elif update.callback_query:
            query = update.callback_query
            await query.answer()  # Acknowledge button press
            message = query.message  # Message containing the inline keyboard
        else:
            return  # Failsafe: shouldn't happen

        buttons = [[SharedButtons.back_to_home_button("Annulla")]]

        await message.reply_text(
            "Inserisci il nome del ristorante:",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

        return ASK_NAME

    @staticmethod
    async def add_restaurant_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles user input for the restaurant name."""
        restaurant_name = update.message.text
        restaurant_name = restaurant_name.replace(":", ";")

        if RestaurantDataManager().has(restaurant_name):
            await update.message.reply_text(
                "Errore: esiste già un ristorante con questo nome."
            )
            return ASK_NAME

        RestaurantDataManager().add_restaurant(
            name=restaurant_name,
            link="Nessun link",
            rating=None,
            total_votes=0,
        )

        buttons = [
            [
                SharedButtons.back_to_restaurant_button(
                    restaurant_name, "👉🏼  Vai al ristorante"
                ),
            ],
            [SharedButtons.back_to_home_button()],
        ]
        await update.message.reply_text(
            "Ristorante aggiunto con successo!",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return ConversationHandler.END


# Define conversation handler
add_restaurant_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            AddRestaurant.add_restaurant_start, pattern="add_restaurant"
        )
    ],
    states={
        ASK_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, AddRestaurant.add_restaurant_name
            )
        ],
    },
    fallbacks=[],
)
