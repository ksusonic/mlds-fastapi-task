import logging
import os
import httpx

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

API_HOST = os.getenv("API_HOST") or "localhost"
print("Using API_HOST: %s", API_HOST)

# Stages
START_ROUTES, END_ROUTES = range(2)
MAIN_MENU = "menu"

# Callback data
GET_ALL, POST, GET_DOG, POST_DOG, GET_DOG_BY_PK, PATCH_DOG = range(6)
MENU_KEYBOARD = [[row] for row in [
    InlineKeyboardButton("GET [/]", callback_data=str(GET_ALL)),
    InlineKeyboardButton("POST [/post]", callback_data=str(POST)),
    InlineKeyboardButton("GET [/dog],", callback_data=str(GET_DOG)),
    InlineKeyboardButton("POST [/dog]", callback_data=str(POST_DOG)),
    InlineKeyboardButton("GET [/dog/{pk}]", callback_data=str(GET_DOG_BY_PK)),
    InlineKeyboardButton("PATCH [/dog/{pk}]", callback_data=str(PATCH_DOG)),
]]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = MENU_KEYBOARD
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать в ветиринарную клинику!\nВыберите действие:",
        reply_markup=reply_markup
    )
    return START_ROUTES


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = MENU_KEYBOARD
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Start handler, Choose a route", reply_markup=reply_markup)
    return START_ROUTES


async def get(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    r = httpx.get(f"http://{API_HOST}:8000/")
    r.raise_for_status()
    await query.from_user.send_message(f"Ответ GET [/]: {r.json()}")
    return START_ROUTES


async def post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    r = httpx.post(f"http://{API_HOST}:8000/post")
    r.raise_for_status()
    await query.from_user.send_message(f"Ответ POST [/post]: {r.json()}")
    return START_ROUTES


async def get_dog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    r = httpx.get(f"http://{API_HOST}:8000/dog")
    r.raise_for_status()
    await query.from_user.send_message(f"Ответ GET [/dog]: {r.json()}")
    return START_ROUTES


async def post_dog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    r = httpx.post(f"http://{API_HOST}:8000/dog", json={"name": "Bob", "pk": 0, "kind": "terrier"})
    r.raise_for_status()
    await query.from_user.send_message(f"Ответ POST [/dog]: {r.json()}")
    return START_ROUTES


async def get_dog_by_pk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    r = httpx.get(f"http://{API_HOST}:8000/dog/1")
    r.raise_for_status()
    await query.from_user.send_message(f"Ответ GET [/dog/1]: {r.json()}")
    return START_ROUTES


async def patch_dog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    r = httpx.patch(f"http://{API_HOST}:8000/dog/4", json={"name": "Bob", "pk": 4, "kind": "terrier"})
    r.raise_for_status()
    await query.from_user.send_message(f"Ответ PATCH [/dog/4]: {r.json()}")
    return START_ROUTES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(get, pattern="^" + str(GET_ALL) + "$"),
                CallbackQueryHandler(post, pattern="^" + str(POST) + "$"),
                CallbackQueryHandler(get_dog, pattern="^" + str(GET_DOG) + "$"),
                CallbackQueryHandler(post_dog, pattern="^" + str(POST_DOG) + "$"),
                CallbackQueryHandler(get_dog_by_pk, pattern="^" + str(GET_DOG_BY_PK) + "$"),
                CallbackQueryHandler(patch_dog, pattern="^" + str(PATCH_DOG) + "$")
            ],
            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern="^" + str(MAIN_MENU) + "$")
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
