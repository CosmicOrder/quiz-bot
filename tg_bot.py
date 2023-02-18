import logging
from random import choice

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, \
    MessageHandler, Filters
from environs import Env

from quiz import quiz_from_content

logger = logging.Logger(__file__)


def start(update: Update, context: CallbackContext):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    text = 'Привет! Я бот для викторин'
    update.message.reply_text(text, reply_markup=reply_markup)


def get_random_question():
    quiz = quiz_from_content()
    random_question = choice(list(quiz.keys()))
    return random_question


def processing_messages(update: Update, context: CallbackContext):
    if update.message.text == 'Новый вопрос':
        update.message.reply_text(get_random_question())


def main():
    env = Env()
    env.read_env()

    quiz_tg_token = env('QUIZ_TG_TOKEN')
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(logging.DEBUG)

    updater = Updater(token=quiz_tg_token)

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(
        Filters.text & (~Filters.command),
        processing_messages)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(message_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
