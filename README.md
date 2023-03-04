# Квиз боты 

Данные [ВК](https://vk.ru/club219094613) и [телеграмм](https://t.me/intellectual_quiz_bot) боты представляют собой площадки для проведения викторин. 


## Как установить

Скачайте код.

Создайте виртуальное окружение:

```
python3 -m venv venv
```

Активируйте виртуальное окружение:

- для Windows:
    ```
    venv\Scripts\activate 
    ```
- для Linux:
    ```
    source venv/bin/activate 
    ```

Установите зависимости командой:

```
pip install -r requirements.txt
```

## Переменные окружения

Часть настроек проекта берётся из переменных окружения. Чтобы их определить,
создайте файл `.env` в корне проекта и запишите туда данные в таком
формате: `ПЕРЕМЕННАЯ=значение`.

Доступны следующие переменные:

- `QUIZ_TG_TOKEN` – токен, который необходим для управления телеграм-ботом викторины через API
- `QUIZ_VK_TOKEN` – токен, который необходим для управления ВК-ботом викторины через API
- `PATH_TO_QUIZ` – путь до текстового файла с вопросами и ответами для викторины
- `HOST` – адрес базы данных вида: `redis-13965.f18.us-east-4-9.wc1.cloud.redislabs.com`
- `PORT` – порт по которому будет произведено соединения с базой данных
- `REDIS_USERNAME` – имя пользователя базы данных
- `REDIS_PASSWD` – пароль базы данных


## Запуск

Чтобы запустить телеграмм-бота, введите в терминале:

```
python tg_bot.py 
```

Чтобы запустить вк-бота, введите в терминале:

```
python vk_bot.py 
```

В результате, если вы всё сделали правильно, боты будет задавать вопросы, 
на которые вы должны будете отвечать.

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для
веб-разработчиков [dvmn.org](https://dvmn.org/).