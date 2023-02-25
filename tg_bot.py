import logging
import textwrap
from random import choice

from environs import Env
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, \
    MessageHandler, Filters

from quiz import quiz_from_content
from redis_connection import redis

logger = logging.Logger(__file__)


def start(update: Update, context: CallbackContext):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    text = 'Привет! Я бот для викторин'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup)


def get_random_question():
    quiz = quiz_from_content()
    random_question = choice(list(quiz.keys()))
    return random_question


def processing_messages(update: Update, context: CallbackContext):
    asked_question = redis.get(str(update.message.from_user.id))
    right_answer = quiz_from_content().get(asked_question)[:-1]
    print(right_answer)
    if update.message.text == 'Новый вопрос':
        question_for_user = get_random_question()
        update.message.reply_text(question_for_user)
        redis.set(str(update.message.from_user.id), question_for_user)
    elif update.message.text.capitalize() == right_answer.capitalize():
        update.message.reply_text(textwrap.dedent('''
        Правильно! Поздравляю!
        Для следующего вопроса нажми "Новый вопрос"
        '''))
    else:
        update.message.reply_text('Неправильно... Попробуешь ещё раз?')


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
