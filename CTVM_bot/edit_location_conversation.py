import validators
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

from CTVM_bot.restaurant_data_manager import RestaurantDataManager
from CTVM_bot.shared_buttons import SharedButtons

# Define states
LOCATION = 1


class EditLocation:
    @staticmethod
    async def edit_location_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        restaurant_name = update.callback_query.data.split(":")[1]
        if not RestaurantDataManager().has(restaurant_name):
            await update.message.edit_text(text="Errore: ristorante non trovato.")
            return
        context.user_data["restaurant_name"] = restaurant_name

        # Handle both command and button press (callback_query)
        if update.message:
            message = update.message  # Command
        elif update.callback_query:
            query = update.callback_query
            await query.answer()  # Acknowledge button press
            message = query.message  # Message containing the inline keyboard
        else:
            return  # Failsafe: shouldn't happen

        buttons = [
            [InlineKeyboardButton("Annulla", callback_data="cancel_edit_location")],
        ]

        await message.edit_text(
            "Inserisci il link di Google Maps del ristorante:",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return LOCATION

    @staticmethod
    async def edit_location_link(
        update: Update | CallbackQuery, context: ContextTypes.DEFAULT_TYPE
    ):
        restaurant_name = context.user_data["restaurant_name"]
        link = update.message.text
        if (
            not "maps.google" in link
            and not "goo.gl" in link
            and not "google.com/maps" in link
        ) or not validators.url(link):
            back_button = InlineKeyboardButton(
                "Annulla", callback_data="cancel_edit_location"
            )
            await update.message.chat.send_message(
                "Errore: Link non valido. Assicurati che sia un link di Google Maps.",
                reply_markup=InlineKeyboardMarkup([[back_button]]),
            )
            return LOCATION

        RestaurantDataManager().update_location(restaurant_name, link)

        back_button = SharedButtons.back_to_restaurant_button(restaurant_name)
        await update.message.chat.send_message(
            f"Posizione aggiornata con successo!",
            reply_markup=InlineKeyboardMarkup([[back_button]]),
        )
        return ConversationHandler.END

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        back_button = SharedButtons.back_to_restaurant_button(
            context.user_data["restaurant_name"]
        )
        await query.message.edit_text(
            "Modifica annullata",
            reply_markup=InlineKeyboardMarkup([[back_button]]),
        )

        return ConversationHandler.END


# Define conversation handler
edit_location_conversation_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(EditLocation.edit_location_start, pattern="edit_location"),
    ],
    states={
        LOCATION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                EditLocation.edit_location_link,
            ),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(EditLocation.cancel, pattern="^cancel_edit_location$")
    ],
)
