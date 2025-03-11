import logging
import os

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    PollHandler,
)

from CTVM_bot.add_restaurant_conversation import (
    AddRestaurant,
    add_restaurant_conv_handler,
)
from CTVM_bot.edit_location_conversation import (
    edit_location_conversation_handler,
)
from CTVM_bot.edit_name_conversation import edit_name_conversation_handler
from CTVM_bot.poll_manager import PollManager
from CTVM_bot.restaurant_data_manager import RestaurantDataManager
from CTVM_bot.shared_buttons import SharedButtons
from CTVM_bot.show_list import ShowList
from CTVM_bot.show_restaurant import ShowRestaurant

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def start(update: Update | CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """Mostra un menu interattivo con pulsanti inline."""
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
        [InlineKeyboardButton("📋  Lista Ristoranti", callback_data="list")],
        [SharedButtons.add_restaurant_button()],
        [InlineKeyboardButton("❔  Aiuto", callback_data="help")],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        "Benvenuto! Scegli un'opzione dal menu:", reply_markup=keyboard
    )


async def help_command(
    update: Update | CallbackQuery, context: ContextTypes.DEFAULT_TYPE
):
    """Mostra l'elenco dei comandi disponibili."""
    help_text = (
        "Comandi disponibili:\n"
        "/start - Mostra il menu interattivo\n"
        "/help - Mostra i comandi disponibili\n"
    )
    await update.message.reply_text(help_text)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "home":
        await start(query, context)
    elif data == "list":
        await ShowList.show_list(query, context)
    elif data == "add_restaurant":
        await AddRestaurant.add_restaurant_start(query, context)
        await ShowRestaurant.show_restaurant(query, context)
    elif data == "help":
        await help_command(query, context)
    elif data.startswith("restaurant:"):
        await ShowRestaurant.show_restaurant(query, context)
    elif data.startswith("edit_restaurant:"):
        await ShowRestaurant.edit_restaurant(query, context)
    elif data.startswith("delete_restaurant:"):
        await ShowRestaurant.delete_restaurant(query, context)
    elif data.startswith("confirm_delete:"):
        await ShowRestaurant.confirm_delete(query, context)
    elif data.startswith("poll:"):
        restaurant_name = data.split(":", 1)[1]
        if RestaurantDataManager().has(restaurant_name):
            question = f"Come valuti {restaurant_name}? (1-5 stelle)"
            options = ["1", "2", "3", "4", "5"]
            poll_message = await query.message.reply_poll(
                question=question, options=options, is_anonymous=False
            )
            PollManager().poll_mapping[poll_message.poll.id] = restaurant_name
            await query.message.reply_text(
                text=f"Sondaggio per {restaurant_name} creato con successo!"
            )
        else:
            await query.message.reply_text(text="Errore: ristorante non trovato.")
    else:
        await query.message.reply_text(text="Azione non riconosciuta.")


def setup_bot():
    # Load environment variables, where token is stored
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(bot_token).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lista", ShowList.show_list))

    # Register conversation handlers
    application.add_handler(add_restaurant_conv_handler)
    application.add_handler(edit_location_conversation_handler)
    application.add_handler(edit_name_conversation_handler)

    # Register button handler
    application.add_handler(CallbackQueryHandler(button_handler))

    # Register poll handlers
    application.add_handler(PollHandler(PollManager().poll_update_handler))

    application.run_polling()
