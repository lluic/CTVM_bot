import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    PollHandler,
)

# Stati per la conversazione di aggiunta ristorante
RIST_NAME, RIST_LINK = range(2)

# Dizionario dei ristoranti:
# Ogni ristorante ha il link di Google Maps, la media dei voti e il numero totale dei voti.
ristoranti = {
    "Ristorante A": {
        "link": "https://goo.gl/maps/exampleA",
        "rating": None,
        "total_votes": 0,
    },
    "Ristorante B": {
        "link": "https://goo.gl/maps/exampleB",
        "rating": None,
        "total_votes": 0,
    },
}

# Mapping tra poll_id e ristorante per aggiornare la valutazione
poll_mapping = {}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


### FUNZIONE HELPER PER CONVERTIRE LA VALUTAZIONE IN EMOJI DI STELLE ###
def rating_to_stars(rating):
    """Converte una valutazione in un display a stelle (su scala 1-5)."""
    if rating is None or rating == 0:
        return "Non valutato"
    # Arrotonda al numero intero più vicino
    stars = round(rating)
    # Mostra stelle piene e stelle vuote per completare 5
    return "⭐" * stars + "☆" * (5 - stars)


### COMANDI BASE E MENU INTERATTIVO ###


# /start: mostra un menu interattivo con pulsanti inline
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Lista Ristoranti", callback_data="lista")],
        [InlineKeyboardButton("Aggiungi Ristorante", callback_data="aggiungi")],
        [InlineKeyboardButton("Aiuto", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Benvenuto! Scegli un'opzione dal menu:", reply_markup=reply_markup
    )


# /help: mostra l'elenco dei comandi
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Comandi disponibili:\n"
        "/start - Mostra il menu interattivo\n"
        "/help - Mostra questo messaggio di aiuto\n"
        "/lista - Visualizza la lista dei ristoranti con link di Maps e valutazione\n"
        "/posizione - Seleziona un ristorante per visualizzare la sua posizione\n"
        "/sondaggio - Seleziona un ristorante per avviare un sondaggio (1-5 stelle, non anonimo)\n"
        "/aggiungi_ristorante - Aggiungi un nuovo ristorante (nome e link di Google Maps)\n"
        "/elimina_ristorante - Seleziona un ristorante da eliminare dalla lista"
    )
    await update.message.reply_text(help_text)


# /lista: mostra la lista dei ristoranti, il link e la valutazione in numeri ed emoji
async def lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Lista dei ristoranti disponibili:\n"
    if not ristoranti:
        text += "Nessun ristorante disponibile."
    else:
        for nome, dati in ristoranti.items():
            link = dati.get("link", "Nessun link disponibile")
            rating = dati.get("rating")
            total_votes = dati.get("total_votes", 0)
            text += f"- {nome}\nLink: {link}\n"
            if rating is not None and total_votes > 0:
                stars = rating_to_stars(rating)
                text += (
                    f"Valutazione: {rating:.1f} stelle {stars} ({total_votes} voti)\n\n"
                )
            else:
                text += "Valutazione: non valutato\n\n"
    await update.message.reply_text(text)


### SELEZIONE DEL RISTORANTE CON PULSANTI INLINE ###


# /posizione: mostra un inline keyboard per selezionare il ristorante di cui visualizzare il link
async def choose_posizione(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ristoranti:
        await update.message.reply_text("Errore: Nessun ristorante disponibile.")
        return
    keyboard = [
        [InlineKeyboardButton(r, callback_data=f"posizione:{r}")] for r in ristoranti
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Seleziona un ristorante per visualizzare la posizione:",
        reply_markup=reply_markup,
    )


# /sondaggio: mostra un inline keyboard per selezionare il ristorante da valutare
async def choose_sondaggio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ristoranti:
        await update.message.reply_text("Errore: Nessun ristorante disponibile.")
        return
    keyboard = [
        [InlineKeyboardButton(r, callback_data=f"sondaggio:{r}")] for r in ristoranti
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Seleziona un ristorante per avviare il sondaggio:", reply_markup=reply_markup
    )


# /elimina_ristorante: mostra un inline keyboard per selezionare il ristorante da eliminare
async def choose_elimina(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ristoranti:
        await update.message.reply_text("Errore: Nessun ristorante disponibile.")
        return
    keyboard = [
        [InlineKeyboardButton(r, callback_data=f"elimina:{r}")] for r in ristoranti
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Seleziona un ristorante da eliminare:", reply_markup=reply_markup
    )


### GESTIONE DEI CALLBACK DEI PULSANTI INLINE ###


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "lista":
        # Mostra la lista con link e valutazione in emoji
        text = "Lista dei ristoranti disponibili:\n"
        if not ristoranti:
            text += "Nessun ristorante disponibile."
        else:
            for nome, dati in ristoranti.items():
                link = dati.get("link", "Nessun link disponibile")
                rating = dati.get("rating")
                total_votes = dati.get("total_votes", 0)
                text += f"- {nome}\nLink: {link}\n"
                if rating is not None and total_votes > 0:
                    stars = rating_to_stars(rating)
                    text += f"Valutazione: {rating:.1f} stelle {stars} ({total_votes} voti)\n\n"
                else:
                    text += "Valutazione: non valutato\n\n"
        await query.edit_message_text(text=text)
    elif data == "aggiungi":
        await query.edit_message_text(
            text="Per aggiungere un ristorante, usa il comando /aggiungi_ristorante."
        )
    elif data == "help":
        help_text = (
            "Comandi disponibili:\n"
            "/start - Mostra il menu interattivo\n"
            "/help - Mostra questo messaggio di aiuto\n"
            "/lista - Visualizza la lista dei ristoranti\n"
            "/posizione - Seleziona un ristorante per visualizzare la posizione\n"
            "/sondaggio - Seleziona un ristorante per avviare il sondaggio (1-5 stelle, non anonimo)\n"
            "/aggiungi_ristorante - Aggiungi un nuovo ristorante\n"
            "/elimina_ristorante - Seleziona un ristorante da eliminare"
        )
        await query.edit_message_text(text=help_text)
    elif data.startswith("posizione:"):
        restaurant = data.split(":", 1)[1]
        if restaurant in ristoranti:
            link = ristoranti[restaurant]["link"]
            keyboard = [[InlineKeyboardButton("Apri su Google Maps", url=link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"Posizione per {restaurant}:", reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(text="Errore: ristorante non trovato.")
    elif data.startswith("sondaggio:"):
        restaurant = data.split(":", 1)[1]
        if restaurant in ristoranti:
            question = f"Come valuti {restaurant}? (1-5 stelle)"
            options = ["1", "2", "3", "4", "5"]
            poll_message = await query.message.reply_poll(
                question=question, options=options, is_anonymous=False
            )
            poll_mapping[poll_message.poll.id] = restaurant
            await query.edit_message_text(
                text=f"Sondaggio per {restaurant} creato con successo!"
            )
        else:
            await query.edit_message_text(text="Errore: ristorante non trovato.")
    elif data.startswith("elimina:"):
        restaurant = data.split(":", 1)[1]
        if restaurant in ristoranti:
            del ristoranti[restaurant]
            await query.edit_message_text(
                text=f"Ristorante '{restaurant}' eliminato con successo."
            )
        else:
            await query.edit_message_text(text="Errore: ristorante non trovato.")
    else:
        await query.edit_message_text(text="Azione non riconosciuta.")


### AGGIUNTA DI UN NUOVO RISTORANTE (CONVERSAZIONE) ###


async def aggiungi_ristorante_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Inserisci il nome del ristorante:")
    return RIST_NAME


async def aggiungi_ristorante_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ristorante_nome"] = update.message.text
    await update.message.reply_text("Inserisci il link di Google Maps della posizione:")
    return RIST_LINK


async def aggiungi_ristorante_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    if "maps.google" in link or "goo.gl" in link or "google.com/maps" in link:
        nome = context.user_data.get("ristorante_nome")
        ristoranti[nome] = {"link": link, "rating": None, "total_votes": 0}
        await update.message.reply_text(f"Ristorante '{nome}' aggiunto con successo!")
    else:
        await update.message.reply_text(
            "Errore: Link non valido. Assicurati che sia un link di Google Maps."
        )
    return ConversationHandler.END


async def aggiungi_ristorante_cancel(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text("Aggiunta del ristorante annullata.")
    return ConversationHandler.END


### AGGIORNAMENTO DELLA VALUTAZIONE (Poll Handler) ###


async def poll_update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll = update.poll
    if poll.id in poll_mapping:
        restaurant = poll_mapping[poll.id]
        total_votes = sum(option.voter_count for option in poll.options)
        if total_votes > 0:
            rating_sum = sum(
                (i + 1) * option.voter_count for i, option in enumerate(poll.options)
            )
            average = rating_sum / total_votes
        else:
            average = 0
        ristoranti[restaurant]["rating"] = average
        ristoranti[restaurant]["total_votes"] = total_votes
        logger.info(
            f"Updated rating for {restaurant}: {average:.1f} from {total_votes} votes"
        )


### SETUP DELL'APPLICAZIONE ###


def main():
    application = (
        Application.builder()
        .token("7360553682:AAHEVY2tjiv6bO4yGoJO7X5mrlCDNwAeZJ8")
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("aggiungi_ristorante", aggiungi_ristorante_start)],
        states={
            RIST_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, aggiungi_ristorante_nome
                )
            ],
            RIST_LINK: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, aggiungi_ristorante_link
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", aggiungi_ristorante_cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lista", lista))
    application.add_handler(CommandHandler("posizione", choose_posizione))
    application.add_handler(CommandHandler("sondaggio", choose_sondaggio))
    application.add_handler(CommandHandler("elimina_ristorante", choose_elimina))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(PollHandler(poll_update_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
