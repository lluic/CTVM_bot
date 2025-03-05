import logging
import os

import validators
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    PollHandler,
)

from CTVM_bot.add_restaurant_conversation import AddRestaurant
from CTVM_bot.edit_location_conversation import EditLocation
from CTVM_bot.poll_manager import PollManager
from CTVM_bot.restaurant_data_manager import RestaurantDataManager
from CTVM_bot.show_list import ShowList
from CTVM_bot.show_restaurant import ShowRestaurant

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


### COMANDI BASE E MENU INTERATTIVO ###
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra un menu interattivo con pulsanti inline."""
    buttons = [
        [InlineKeyboardButton("Lista Ristoranti", callback_data="list")],
        [InlineKeyboardButton("Aggiungi Ristorante", callback_data="add")],
        [InlineKeyboardButton("Aiuto", callback_data="help")],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
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
        "/lista - Visualizza la lista dei ristoranti\n"
        # "/posizione - Visualizza o modifica la posizione dei ristoranti\n"
        # "/sondaggio - Apri un sondaggio su un ristorante (1-5 stelle, non anonimo)\n"
        "/aggiungi_ristorante - Aggiungi un nuovo ristorante (nome e link di Google Maps)\n"
        # "/elimina_ristorante - Seleziona un ristorante da eliminare dalla lista"
    )
    await update.message.reply_text(help_text)


### SELEZIONE DEL RISTORANTE CON PULSANTI INLINE ###
# async def choose_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Mostra un inline keyboard per selezionare il ristorante di cui visualizzare il link"""
#     restaurants = RestaurantDataManager().restaurants
#     if not restaurants:
#         await update.message.reply_text("Errore: Nessun ristorante disponibile.")
#         return
#     buttons = [
#         [InlineKeyboardButton(r.name, callback_data=f"location:{r.name}")]
#         for r in restaurants
#     ]
#     keyboard = InlineKeyboardMarkup(buttons)
#     await update.message.reply_text(
#         "Seleziona un ristorante per visualizzare o modificare la posizione:",
#         reply_markup=keyboard,
#     )


# async def choose_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Mostra un inline keyboard per selezionare il ristorante da valutare."""
#     restaurants = RestaurantDataManager().restaurants
#     if not restaurants:
#         await update.message.reply_text("Errore: Nessun ristorante disponibile.")
#         return
#     buttons = [
#         [InlineKeyboardButton(r.name, callback_data=f"poll:{r.name}")]
#         for r in restaurants
#     ]
#     keyboard = InlineKeyboardMarkup(buttons)
#     await update.message.reply_text(
#         "Seleziona un ristorante per avviare il sondaggio:", reply_markup=keyboard
#     )


# async def choose_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Mostra un inline keyboard per selezionare il ristorante da eliminare."""
#     restaurants = RestaurantDataManager().restaurants
#     if not restaurants:
#         await update.message.reply_text("Errore: Nessun ristorante disponibile.")
#         return
#     buttons = [
#         [InlineKeyboardButton(r.name, callback_data=f"delete:{r.name}")]
#         for r in restaurants
#     ]
#     keyboard = InlineKeyboardMarkup(buttons)
#     await update.message.reply_text(
#         "Seleziona un ristorante da eliminare:", reply_markup=keyboard
#     )


### GESTIONE DEI CALLBACK DEI PULSANTI INLINE ###
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "list":
        await ShowList.show_list(query, context)
    elif data == "help":
        await help_command(query, context)
    elif data.startswith("restaurant:"):
        await ShowRestaurant.show_restaurant(query, context)
    elif data.startswith("edit_restaurant:"):
        await ShowRestaurant.edit_restaurant(query, context)
    # elif data.startswith("location:"):
    #     # TODO: ?- if possible, the button opens a map popup on telegram -?
    #     restaurant_name = data.split(":", 1)[1]
    #     if RestaurantDataManager().has(restaurant_name):
    #         link = RestaurantDataManager().get_restaurant(restaurant_name).link
    #
    #         maps_button = None
    #         link_valid = False
    #         location_button_text = "Aggiungi posizione"
    #         if validators.url(link):
    #             maps_button = InlineKeyboardButton("Apri su Google Maps", url=link)
    #             location_button_text = "Modifica posizione"
    #             link_valid = True
    #
    #         edit_location_button = InlineKeyboardButton(
    #             location_button_text, callback_data=f"edit_location:{restaurant_name}"
    #         )
    #         buttons = [[edit_location_button]]
    #         if link_valid:
    #             buttons.insert(0, [maps_button])
    #         keyboard = InlineKeyboardMarkup(buttons)
    #
    #         await query.message.reply_text(
    #             text=f"Posizione per {restaurant_name}:", reply_markup=keyboard
    #         )
    #     else:
    #         await query.message.reply_text(text="Errore: ristorante non trovato.")
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
    # elif data.startswith("delete:"):
    #     restaurant_name = data.split(":", 1)[1]
    #     if RestaurantDataManager().has(restaurant_name):
    #         RestaurantDataManager().remove_restaurant(restaurant_name)
    #         await query.message.reply_text(
    #             text=f"Ristorante '{restaurant_name}' eliminato con successo."
    #         )
    #     else:
    #         await query.message.reply_text(text="Errore: ristorante non trovato.")
    else:
        await query.message.reply_text(text="Azione non riconosciuta.")


# SETUP
def setup_bot():
    # Load environment variables, where token is stored
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lista", ShowList.show_list))
    # application.add_handler(CommandHandler("posizione", choose_location))
    # application.add_handler(CommandHandler("sondaggio", choose_poll))
    # application.add_handler(CommandHandler("elimina_ristorante", choose_delete))
    application.add_handler(AddRestaurant.conversation_handler())
    application.add_handler(EditLocation.conversation_handler())
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(PollHandler(PollManager().poll_update_handler))

    application.run_polling()
