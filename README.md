# Телеграм-бот для Модерации Чата

![GitHub Stars](https://img.shields.io/github/stars/your_username/your_repo.svg?style=flat&label=Stars&maxAge=2592000)

Данный телеграм-бот представляет собой инструмент для модерации чата, который позволяет управлять пользователями с помощью опросов. Бот создает опросы для бана, мута, смены тайтла пользователя и создания инвайта на одного пользователя. Модераторы чата могут принимать решения на основе результатов опросов и выполнять соответствующие действия.

## Функциональность

- Бан пользователя по решению большинства.
- Мут пользователя по решению большинства.
- Изменение тайтла пользователя по решению большинства.
- Создание инвайта на одного пользователя по решению большинства.

## Как использовать

1. Установите все зависимости, указанные в `requirements.txt`.

2. В файле `config.py` укажите токен вашего телеграм-бота и ID группы.

3. Запустите бота с помощью команды `python bot.py`.

4. Бот будет автоматически реагировать на команды модераторов чата.

## Команды бота

- `/ban` - Отправляется в ответ на сообщение пользователя. Создает опрос для бана пользователя.
- `/mute 10` - Отправляется в ответ на сообщение пользователя. Создает опрос для мута пользователя на указанное количество минут.
- `/role new_title` - Отправляется в ответ на сообщение пользователя. Создает опрос для изменения тайтла пользователя на новый `new_title`.
- `/invite` - Создает опрос для создания инвайта на одного пользователя.

## Как это работает

1. Когда пользователь чата отправляет команду для бана, мута, смены тайтла или создания инвайта, бот создает опрос с вариантами ответа "Да" и "Нет".

2. Другие пользователи видят опрос и могут проголосовать.

3. По истечении 10 минут бот анализирует результаты опроса и принимает решение на основе большинства голосов.

4. Если большинство пользователей проголосовало "Да", бот выполняет соответствующее действие.

5. Результаты опроса и решение бота отправляются в чат для уведомления всех участников.

## Автор

Александр Вяткин - [https://t.me/leavemealonefuckingscripts](https://github.com/Greavis)

## Лицензия

Этот проект лицензирован под лицензией [MIT](https://opensource.org/licenses/MIT).
