import random
import textwrap

import vk_api as vk
from environs import Env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from misc import get_random_question, get_right_answer
from redis_connection import redis

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


def handle_new_question_request(event, vk_api):
    question_for_user = get_random_question()
    vk_api.messages.send(
        user_id=event.user_id,
        message=question_for_user,
        random_id=random.randint(1, 1000)
    )
    redis.set(str(event.user_id), question_for_user)


def handle_solution_attempt(event, vk_api):
    right_answer = get_right_answer(event.user_id)
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


def give_up(event, vk_api):
    message_text = f'Правильный ответ: {get_right_answer(event.user_id)}'
    vk_api.messages.send(
        user_id=event.user_id,
        message=message_text,
        random_id=random.randint(1, 1000)
    )

    handle_new_question_request(event, vk_api)


def main():
    env = Env()
    env.read_env()
    quiz_vk_token = env('QUIZ_VK_TOKEN')

    vk_session = vk.VkApi(token=quiz_vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Сдаться':
                give_up(event, vk_api)
            elif event.text == 'Новый вопрос':
                handle_new_question_request(event, vk_api)
            elif event.text == 'Привет':
                start(event, vk_api)
            else:
                handle_solution_attempt(event, vk_api)


if __name__ == "__main__":
    main()
