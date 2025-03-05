import validators
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

from CTVM_bot.restaurant_data_manager import RestaurantDataManager


class EditLocation:
    # States for the AddRestaurant conversation
    LOCATION = range(1)

    @staticmethod
    def conversation_handler():
        return ConversationHandler(
            entry_points=[
                CommandHandler("edit_location", EditLocation.edit_location_start),
                CallbackQueryHandler(
                    EditLocation.edit_location_start, pattern=f"^edit_location:.*"
                ),
            ],
            states={
                EditLocation.LOCATION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        EditLocation.edit_location_link,
                    ),
                    CallbackQueryHandler(
                        EditLocation.edit_location_cancel, pattern=f"^cancel_link$"
                    ),
                ],
            },
            fallbacks=[],
        )

    @staticmethod
    async def edit_location_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        restaurant_name = update.callback_query.data.split(":")[1]
        if not RestaurantDataManager().has(restaurant_name):
            await update.message.reply_text(text="Errore: ristorante non trovato.")
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
            [InlineKeyboardButton("Annulla", callback_data="cancel_link")],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        # Ask user for restaurant name
        await message.reply_text(
            "Inserisci il link di Google Maps del ristorante:", reply_markup=keyboard
        )
        return EditLocation.LOCATION  # Move to the next state

    @staticmethod
    async def edit_location_link(
        update: Update | CallbackQuery, context: ContextTypes.DEFAULT_TYPE
    ):
        link = update.message.text
        if (
            not "maps.google" in link
            and not "goo.gl" in link
            and not "google.com/maps" in link
        ) or not validators.url(link):
            buttons = [
                [InlineKeyboardButton("Annulla", callback_data="cancel_link")],
            ]
            keyboard = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(
                "Errore: Link non valido. Assicurati che sia un link di Google Maps.",
                reply_markup=keyboard,
            )
            return EditLocation.LOCATION

        RestaurantDataManager().update_location(
            context.user_data["restaurant_name"], link
        )

        await update.message.reply_text(f"Posizione aggiornata con successo!")
        return ConversationHandler.END

    @staticmethod
    async def edit_location_cancel(
        update: Update | CallbackQuery, context: ContextTypes.DEFAULT_TYPE
    ):
        # Handle both command and button press (callback_query)
        if update.message:
            message = update.message  # Command
        elif update.callback_query:
            query = update.callback_query
            await query.answer()  # Acknowledge button press
            message = query.message  # Message containing the inline keyboard
        else:
            return  # Failsafe: shouldn't happen

        await message.reply_text("Aggiornamento della posizione annullato.")
        return ConversationHandler.END
