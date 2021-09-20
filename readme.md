# Тестовое задание на django / drf

Задача: спроектировать и разработать API для системы опросов пользователей.

Функционал для администратора системы:

- аутентификация в системе (регистрация не нужна)
- добавление/изменение/удаление опросов. Атрибуты опроса: название, дата старта, дата окончания, описание. После создания поле "дата старта" у опроса менять нельзя
- добавление/изменение/удаление вопросов в опросе. Атрибуты вопросов: текст вопроса, тип вопроса (ответ текстом, ответ с выбором одного варианта, ответ с выбором нескольких вариантов)

Функционал для пользователей системы:

- получение списка активных опросов
- прохождение опроса: опросы можно проходить анонимно, в качестве идентификатора пользователя в API передаётся числовой ID, по которому сохраняются ответы пользователя на вопросы; один пользователь может участвовать в любом количестве опросов
- получение пройденных пользователем опросов с детализацией по ответам (что выбрано) по ID уникальному пользователя

Использовать следующие технологии: Django 2.2.10, Django REST framework.

Результат выполнения задачи:
- исходный код приложения в github (только на github, публичный репозиторий)
- инструкция по разворачиванию приложения (в docker или локально)
- документация по API

## Установка зависимостей
    python -m pip install -r req.txt
    python manage.py runserver
    python manage.py migrate

Команда 
```python manage.py populate```
заполняет базу начальными данными.

## Описание API
Аутентификация через сессию Django или HTTP Basic Auth.
Каждая точка в корне ./api/ поддерживает GET/POST/PUT/DELETE и возвращает данные в виде JSON формата:
* count - количество объектов
* prev, next - ссылки для постранничного вывода (не реализовано)
* results - JSON с объектами
    
В корне **./dashboard/** расположена панель управления опросами на основе BrowsableApiRenderer.
ID пользователя генерируется на лету в middleware и хранится в сессии. Опросы пользователя со своим ID можно получить по адресу **/api/polls/me/** или **/dashboard/polls/me**.
По адресу **./** форма голосования в опросе.

### Опросы (Poll) - /api/polls/, /dashboard/polls/
Формат объектов в results:
1. id - **read-only** идентификатор объекта.
2. url - ссылка на объект *models.Poll* в панели управления.
3. title - название. По-умолчанию "Untitled".
4. start_at - дата старта в [стандартных форматах Django](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-DATETIME_INPUT_FORMATS). По-умолчанию равна "сейчас".
5. expire_at - дата окончания. По-умолчанию равна "через неделю".
6. description - описание. По-умолчанию "I'm a Poll".
7. questions - **read-only** JSON с объектами *PollQuestion*.

Обновление поля start_at запрещено на уровне валидации поля. Без аутентификации разрешено только чтение.

### Вопросы (PollQuestion) - /api/questions/, /dashboard/questions/
Формат объектов в results:
1. id - **read-only** идентификатор объекта.
2. url - ссылка на объект *PollQuestion* в панели управления.
3. poll - ссылка на родительский объект models.Poll в панели управления.
4. text - текст вопроса. По-умолчанию "What's up?".
5. answers - текстовое поле, содержащее разделенные запятой варианты ответов. Пример - "Sky,Space,ISS".
6. type - текстовое поле типа вопроса со значениями "SA" - вопрос с выбором одного ответа, "TA" - вопрос с текстовым вводом, "MA" - вопрос с выбором нескольких вариантов ответа.
7. type_display - **read-only** поле с полным названием типа. Пример - "Single Answer".
8. answers_display - **read-only** поле, содержащее JSON с отдельными вариантами ответов из поля answers.
7. responses - **read-only** JSON с объектами PollResponse.

Без аутентификации разрешено только чтение.

### Ответы (PollResponse) - /api/responses/
Формат объектов в results:
1. question - ID родительского объекта PollQuestion.
2. text - текстовое поле, содержащее JSON с номерами ответов. Пример - "Sky,Space,ISS" -> [0, 1, 2].
3. user_id - **write-only** текстовое поле, содержащее ID ответившего пользователя.

Аутентификация для создания объектов PollResponse не требуется. Уникальность пары "response.user_id - question.id" проверяется при валидации.
