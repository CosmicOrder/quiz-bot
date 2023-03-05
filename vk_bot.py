import random
import textwrap

import vk_api as vk
from environs import Env
from redis import Redis
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from quiz import make_quiz_from_content

keyboard = VkKeyboard()

keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)

keyboard.add_line()  # Переход на вторую строку
keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

keyboard.add_line()
keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)


def start(event, vk_api):
    text = 'Привет! Я бот для викторин'
    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def handle_new_question_request(event, vk_api, quiz, redis):
    question_for_user = random.choice(list(quiz.keys()))
    vk_api.messages.send(
        user_id=event.user_id,
        message=question_for_user,
        random_id=random.randint(1, 1000)
    )
    redis.set(str(event.user_id), question_for_user)


def handle_solution_attempt(event, vk_api, quiz, redis):
    asked_question = redis.get(str(event.user_id))
    right_answer = quiz.get(asked_question)[:-1]
    if event.text.capitalize() == right_answer.capitalize():
        message_text = (textwrap.dedent('''
         Правильно! Поздравляю!
         Для следующего вопроса нажми "Новый вопрос"
         '''))
        vk_api.messages.send(
            user_id=event.user_id,
            message=message_text,
            random_id=random.randint(1, 1000)
        )
    else:
        message_text = 'Неправильно... Попробуешь ещё раз?'
        vk_api.messages.send(
            user_id=event.user_id,
            message=message_text,
            random_id=random.randint(1, 1000)
        )


def give_up(event, vk_api, quiz, redis):
    asked_question = redis.get(str(event.user_id))
    right_answer = quiz.get(asked_question)[:-1]
    message_text = f'Правильный ответ: {right_answer}'
    vk_api.messages.send(
        user_id=event.user_id,
        message=message_text,
        random_id=random.randint(1, 1000)
    )

    handle_new_question_request(event, vk_api, quiz, redis)


def main():
    env = Env()
    env.read_env()
    quiz_vk_token = env('QUIZ_VK_TOKEN')
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

    vk_session = vk.VkApi(token=quiz_vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Сдаться':
                give_up(event, vk_api, quiz, redis)
            elif event.text == 'Новый вопрос':
                handle_new_question_request(event, vk_api, quiz, redis)
            elif event.text == 'Привет':
                start(event, vk_api)
            else:
                handle_solution_attempt(event, vk_api, quiz, redis)


if __name__ == "__main__":
    main()
