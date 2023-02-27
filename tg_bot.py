import logging
import textwrap

from environs import Env
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CallbackContext, ConversationHandler, \
    CommandHandler, MessageHandler, Filters

from misc import get_random_question, get_right_answer
from redis_connection import redis

logger = logging.Logger(__file__)

CHOOSING, SOLUTION_ATTEMPT = range(2)


def start(update: Update, context: CallbackContext):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    text = 'Привет! Я бот для викторин'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup)
    return CHOOSING


def handle_new_question_request(update: Update, context: CallbackContext):
    question_for_user = get_random_question()
    update.message.reply_text(question_for_user)
    redis.set(str(update.message.from_user.id), question_for_user)
    return SOLUTION_ATTEMPT


def handle_solution_attempt(update: Update, context: CallbackContext):
    right_answer = get_right_answer(update)
    if update.message.text.capitalize() == right_answer.capitalize():
        update.message.reply_text(textwrap.dedent('''
        Правильно! Поздравляю!
        Для следующего вопроса нажми "Новый вопрос"
        '''))
        return CHOOSING
    else:
        update.message.reply_text('Неправильно... Попробуешь ещё раз?')


def give_up(update: Update, context: CallbackContext):
    update.message.reply_text(get_right_answer(update))

    question_for_user = get_random_question()
    update.message.reply_text(question_for_user)
    redis.set(str(update.message.from_user.id), question_for_user)
    return SOLUTION_ATTEMPT


def cancel(update: Update, context: CallbackContext):
    return -1


def main():
    env = Env()
    env.read_env()

    quiz_tg_token = env('QUIZ_TG_TOKEN')
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(logging.DEBUG)

    updater = Updater(token=quiz_tg_token)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^Новый вопрос$'),
                                      handle_new_question_request),
                       ],
            SOLUTION_ATTEMPT: [MessageHandler(Filters.regex('^Сдаться$'),
                                              give_up),
                               MessageHandler(Filters.text & (~Filters.command),
                                              handle_solution_attempt),
                               ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
