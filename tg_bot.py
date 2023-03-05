import functools
import logging
import textwrap
from random import choice

from redis import Redis
from environs import Env
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CallbackContext, ConversationHandler, \
    CommandHandler, MessageHandler, Filters

from quiz import make_quiz_from_content

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


def handle_new_question_request(update, context, quiz, redis):
    question_for_user = choice(list(quiz.keys()))
    update.message.reply_text(question_for_user)
    redis.set(str(update.message.from_user.id), question_for_user)
    return SOLUTION_ATTEMPT


def handle_solution_attempt(update, context, quiz, redis):
    asked_question = redis.get(str(update.message.from_user.id))
    right_answer = quiz.get(asked_question)[:-1]
    if update.message.text.capitalize() == right_answer.capitalize():
        update.message.reply_text(textwrap.dedent('''
        Правильно! Поздравляю!
        Для следующего вопроса нажми "Новый вопрос"
        '''))
        return CHOOSING
    else:
        update.message.reply_text('Неправильно... Попробуешь ещё раз?')


def give_up(update, context, quiz, redis):
    asked_question = redis.get(str(update.message.from_user.id))
    right_answer = quiz.get(asked_question)[:-1]
    update.message.reply_text(f'Правильный ответ: {right_answer}')

    question_for_user = choice(list(quiz.keys()))
    update.message.reply_text(question_for_user)
    redis.set(str(update.message.from_user.id), question_for_user)
    return SOLUTION_ATTEMPT


def cancel(update, context):
    return -1


def main():
    env = Env()
    env.read_env()

    quiz_tg_token = env('QUIZ_TG_TOKEN')
    path_to_quiz = env('PATH_TO_QUIZ')
    host = env('HOST')
    port = env('PORT')
    username = env('REDIS_USERNAME')
    password = env('REDIS_PASSWD')

    redis = Redis(
        host=host,
        port=port,
        username=username,
        password=password,
        decode_responses=True,
    )

    quiz = make_quiz_from_content(path_to_quiz)

    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(logging.DEBUG)

    updater = Updater(token=quiz_tg_token)

    dispatcher = updater.dispatcher

    handle_new_question_request_partial = functools.partial(
        handle_new_question_request,
        redis=redis,
        quiz=quiz,
    )
    handle_solution_attempt_partial = functools.partial(
        handle_solution_attempt,
        redis=redis,
        quiz=quiz,
    )
    give_up_partial = functools.partial(
        give_up,
        redis=redis,
        quiz=quiz,
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^Новый вопрос$'),
                                      handle_new_question_request_partial),
                       ],
            SOLUTION_ATTEMPT: [MessageHandler(Filters.regex('^Сдаться$'),
                                              give_up_partial),
                               MessageHandler(
                                   Filters.text & (~Filters.command),
                                   handle_solution_attempt_partial),
                               ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
