import datetime

from telegram import LabeledPrice, ParseMode
from telegram.ext import PreCheckoutQueryHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.updater import Updater
from telegram.update import Update

from database import get_collection
from utils import print_col


BOT_KEY = "<YOUR_BOT_KEY_HERE>"
STRIPE_TOKEN = "<YOUR_TOKEN_HERE>"
PRICE = 500


def start(update: Update, context: CallbackContext):
    welcome_message = "Welcome to this bot!"
    update.message.reply_text(welcome_message, parse_mode="html")


def donate(update: Update, context: CallbackContext):
    out = context.bot.send_invoice(
        chat_id=update.message.chat_id,
        title="Test donation",
        description="Give money here.",
        payload="test",
        provider_token=STRIPE_TOKEN,
        currency="GBP",
        prices=[LabeledPrice("Give", PRICE)],
        need_name=False,
    )


def pre_checkout_handler(update: Update, context: CallbackContext):
    """https://core.telegram.org/bots/api#answerprecheckoutquery"""
    query = update.pre_checkout_query
    query.answer(ok=True)


def successful_payment_callback(update: Update, context):
    col = get_collection()
    receipt = update.message.successful_payment
    col.insert_one({"telegram_uid": update.message.chat.username, 
                   "donated_amount": receipt.total_amount,
                   "currency": receipt.currency,
                   "datetime": str(datetime.datetime.now())})
    print_col(col)
    update.message.reply_text("Thank you for your purchase!")


def uid(update: Update, context: CallbackContext):
    uid = update.message.chat.username
    update.message.reply_text(f"Your uid is {uid}", parse_mode="html")


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(f"If you need support please contact example@email.com.")


def _add_handlers(updater):
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("give", donate))
    updater.dispatcher.add_handler(PreCheckoutQueryHandler(pre_checkout_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters._SuccessfulPayment, successful_payment_callback))
    updater.dispatcher.add_handler(CommandHandler("uid", uid))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))


if __name__ == "__main__":
    updater = Updater(BOT_KEY, use_context=True)
    _add_handlers(updater)
    print("starting to poll...")
    updater.start_polling()
