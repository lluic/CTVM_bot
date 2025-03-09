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
from CTVM_bot.shared_buttons import SharedButtons


class EditName:
    # States for the conversation
    NAME = range(1)

    @staticmethod
    def conversation_handler():
        return ConversationHandler(
            entry_points=[
                CommandHandler("edit_name", EditName.edit_name_start),
                CallbackQueryHandler(
                    EditName.edit_name_start, pattern=f"^edit_name:.*"
                ),
            ],
            states={
                EditName.NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        EditName.edit_name,
                    ),
                    CallbackQueryHandler(
                        EditName.edit_name_cancel, pattern=f"^cancel_edit_name$"
                    ),
                ],
            },
            fallbacks=[],
        )

    @staticmethod
    async def edit_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            [InlineKeyboardButton("Annulla", callback_data="cancel_edit_name")],
        ]

        await message.reply_text(
            "Inserisci il nuovo nome del ristorante:",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return EditName.NAME

    @staticmethod
    async def edit_name(
        update: Update | CallbackQuery, context: ContextTypes.DEFAULT_TYPE
    ):
        name = update.message.text
        buttons = [
            [InlineKeyboardButton("Annulla", callback_data="cancel_edit_name")],
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        if RestaurantDataManager().has(name):
            await update.message.reply_text(
                "Esiste già un ristorante con questo nome. Inserisci un nome diverso.",
                reply_markup=keyboard,
            )
            return EditName.NAME

        if name == "":
            await update.message.reply_text(
                "Errore: Nome non valido. Riprova.",
                reply_markup=keyboard,
            )
            return EditName.NAME

        RestaurantDataManager().update_name(context.user_data["restaurant_name"], name)

        back_button = SharedButtons.back_to_restaurant_button(
            context.user_data["restaurant_name"]
        )
        await update.message.reply_text(
            f"Nome aggiornato con successo!",
            reply_markup=InlineKeyboardMarkup([[back_button]]),
        )
        return ConversationHandler.END

    @staticmethod
    async def edit_name_cancel(
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

        back_button = SharedButtons.back_to_restaurant_button(
            context.user_data["restaurant_name"]
        )
        await message.reply_text(
            "Aggiornamento del nome annullato.",
            reply_markup=InlineKeyboardMarkup([[back_button]]),
        )
        return ConversationHandler.END
