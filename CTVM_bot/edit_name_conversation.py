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
NAME = 1


class EditName:
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
        return NAME

    @staticmethod
    async def edit_name(
        update: Update | CallbackQuery, context: ContextTypes.DEFAULT_TYPE
    ):
        name = update.message.text
        cancel_button = InlineKeyboardButton(
            "Annulla", callback_data="cancel_edit_name"
        )

        if RestaurantDataManager().has(name):
            await update.message.reply_text(
                "Esiste già un ristorante con questo nome. Inserisci un nome diverso.",
                reply_markup=InlineKeyboardMarkup([[cancel_button]]),
            )
            return NAME

        if name == "":
            await update.message.reply_text(
                "Errore: Nome non valido. Riprova.",
                reply_markup=InlineKeyboardMarkup([[cancel_button]]),
            )
            return NAME

        RestaurantDataManager().update_name(context.user_data["restaurant_name"], name)

        back_button = SharedButtons.back_to_restaurant_button(name)
        await update.message.reply_text(
            f"Nome aggiornato con successo!",
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
        await query.message.reply_text(
            "Modifica annullata",
            reply_markup=InlineKeyboardMarkup([[back_button]]),
        )
        return ConversationHandler.END


# Define conversation handler
edit_name_conversation_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(EditName.edit_name_start, pattern="edit_name"),
    ],
    states={
        NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                EditName.edit_name,
            ),
        ],
    },
    fallbacks=[CallbackQueryHandler(EditName.cancel, pattern="^cancel_edit_name$")],
)
