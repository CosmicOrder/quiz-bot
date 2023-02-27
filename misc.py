from random import choice

from quiz import quiz_from_content
from redis_connection import redis


def get_random_question():
    quiz = quiz_from_content()
    random_question = choice(list(quiz.keys()))
    return random_question


def get_right_answer(update):
    asked_question = redis.get(str(update.message.from_user.id))
    return quiz_from_content().get(asked_question)[:-1]