from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

from CTVM_bot.restaurant_list import RestaurantList


class AddRestaurant:
    # States for the AddRestaurant conversation
    RIST_NAME, RIST_LINK = range(2)

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
                    )
                ],
                AddRestaurant.RIST_LINK: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        AddRestaurant.add_restaurant_link,
                    )
                ],
            },
            fallbacks=[CommandHandler("cancel", AddRestaurant.add_restaurant_cancel)],
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

        # Ask user for restaurant name
        await message.reply_text("Inserisci il nome del ristorante:")
        return AddRestaurant.RIST_NAME  # Move to the next state

    @staticmethod
    async def add_restaurant_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["new_restaurant_name"] = update.message.text
        await update.message.reply_text(
            "Inserisci il link di Google Maps della posizione:"
        )
        return AddRestaurant.RIST_LINK

    @staticmethod
    async def add_restaurant_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
        link = update.message.text
        if "maps.google" in link or "goo.gl" in link or "google.com/maps" in link:
            RestaurantList().add_restaurant(
                name=context.user_data.get("new_restaurant_name"),
                link=link,
                rating=None,
                total_votes=0,
            )
            await update.message.reply_text(f"Ristorante aggiunto con successo!")
        else:
            await update.message.reply_text(
                "Errore: Link non valido. Assicurati che sia un link di Google Maps."
            )
        return ConversationHandler.END

    @staticmethod
    async def add_restaurant_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Aggiunta del ristorante annullata.")
        return ConversationHandler.END
