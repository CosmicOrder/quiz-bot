import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, \
    MessageHandler, Filters
from environs import Env

logger = logging.Logger(__file__)


def start(update: Update, context: CallbackContext):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text('Здравствуйте', reply_markup=reply_markup)


def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)


def main():
    env = Env()
    env.read_env()

    quiz_tg_token = env('QUIZ_TG_TOKEN')
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(logging.DEBUG)

    updater = Updater(token=quiz_tg_token)

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
