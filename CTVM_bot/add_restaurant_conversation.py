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


class AddRestaurant:
    # States for the AddRestaurant conversation
    RIST_NAME = range(1)

    @staticmethod
    def conversation_handler():
        return ConversationHandler(
            entry_points=[
                CommandHandler(
                    "aggiungi_ristorante", AddRestaurant.add_restaurant_start
                ),
                CallbackQueryHandler(
                    AddRestaurant.add_restaurant_start, pattern="^add$"
                ),
            ],
            states={
                AddRestaurant.RIST_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        AddRestaurant.add_restaurant_name,
                    ),
                    CallbackQueryHandler(
                        AddRestaurant.add_restaurant_cancel, pattern=f"^cancel_add$"
                    ),
                ],
            },
            fallbacks=[],
        )

    @staticmethod
    async def add_restaurant_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Starts the restaurant addition conversation, handling both commands and button presses."""

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
            [InlineKeyboardButton("Annulla", callback_data=f"cancel_add")],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        # Ask user for restaurant name
        await message.reply_text(
            "Inserisci il nome del ristorante:", reply_markup=keyboard
        )
        # await message.reply_text("Inserisci il nome del ristorante:")
        return AddRestaurant.RIST_NAME  # Move to the next state

    @staticmethod
    async def add_restaurant_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if RestaurantDataManager().has(update.message.text):
            await update.message.reply_text(
                "Errore: Esiste già un ristorante con questo nome."
            )
            return ConversationHandler.END

        # context.user_data["new_restaurant_name"] = update.message.text
        RestaurantDataManager().add_restaurant(
            name=update.message.text,
            link="Nessun link",
            rating=None,
            total_votes=0,
        )
        buttons = [
            [
                InlineKeyboardButton(
                    "Aggiungi posizione",
                    callback_data=f"edit_location:{update.message.text}",
                ),
            ]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "Ristorante aggiunto con successo!",
            reply_markup=keyboard,
        )
        # await update.message.reply_text("Ristorante aggiunto con successo!")
        return ConversationHandler.END

    @staticmethod
    async def add_restaurant_cancel(
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

        await message.reply_text("Aggiunta ristorante annullata.")
        return ConversationHandler.END
