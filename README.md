# FastAPI + SQLAlchemy + Alembic + TaskIQ Project

Проект на FastAPI с использованием SQLAlchemy для работы с PostgreSQL, Alembic для миграций и TaskIQ с Redis в качестве брокера задач.

## Структура проекта

```
Backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Точка входа FastAPI приложения
│   ├── config.py            # Конфигурация приложения
│   ├── database.py          # Настройка SQLAlchemy
│   ├── api/                 # API роутеры
│   │   ├── users.py
│   │   └── tasks.py
│   ├── models/              # SQLAlchemy модели
│   │   └── user.py
│   └── tasks/               # TaskIQ задачи
│       ├── __init__.py
│       └── example_tasks.py
├── alembic/                 # Миграции Alembic
│   ├── env.py
│   └── script.py.mako
├── alembic.ini              # Конфигурация Alembic
├── docker-compose.dev.yaml  # Docker Compose для разработки (Postgres + Redis)
├── worker.py                # Воркер для TaskIQ
├── requirements.txt
└── README.md
```

## Установка

### Создание виртуального окружения

Рекомендуется использовать виртуальное окружение для изоляции зависимостей проекта.

#### Linux/macOS:

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Проверка, что виртуальное окружение активно (в начале строки должно быть (venv))
which python  # Должен показать путь к Python в venv
```

#### Windows:

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
venv\Scripts\activate

# Или в PowerShell:
venv\Scripts\Activate.ps1
```

#### Деактивация виртуального окружения:

```bash
deactivate
```

**Важно:** 
- Виртуальное окружение должно быть активировано перед установкой зависимостей и запуском приложения
- При каждом новом открытии терминала нужно активировать venv заново
- Директория `venv/` уже добавлена в `.gitignore` и не будет попадать в репозиторий

### Установка зависимостей

После активации виртуального окружения установите зависимости:

```bash
# Обновление pip до последней версии (рекомендуется)
pip install --upgrade pip

# Установка зависимостей проекта
pip install -r requirements.txt
```

### Настройка переменных окружения

Создайте файл `.env` в корне проекта и настройте переменные окружения:
```env
# Используйте postgresql+asyncpg:// для асинхронной работы с БД
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
APP_NAME=FastAPI TaskIQ App
DEBUG=True
```

**Важно:** URL базы данных должен использовать префикс `postgresql+asyncpg://` для асинхронной работы. Alembic автоматически преобразует его в синхронную версию для миграций.

### Запуск PostgreSQL и Redis через Docker Compose

Для удобства разработки можно использовать Docker Compose для запуска PostgreSQL и Redis:

```bash
# Запуск сервисов
docker-compose -f docker-compose.dev.yaml up -d

# Проверка статуса
docker-compose -f docker-compose.dev.yaml ps

# Остановка сервисов
docker-compose -f docker-compose.dev.yaml down

# Остановка с удалением volumes (удалит все данные!)
docker-compose -f docker-compose.dev.yaml down -v
```

После запуска Docker Compose используйте следующие настройки в `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/wink_db
REDIS_URL=redis://localhost:6379/0
```

**Параметры по умолчанию:**
- PostgreSQL: `postgres:postgres@localhost:5432/wink_db`
- Redis: `localhost:6379`

**Проверка готовности сервисов:**
```bash
# Проверка статуса контейнеров
docker-compose -f docker-compose.dev.yaml ps

# Просмотр логов
docker-compose -f docker-compose.dev.yaml logs postgres
docker-compose -f docker-compose.dev.yaml logs redis
```

Убедитесь, что оба сервиса показывают статус "healthy" перед запуском приложения.

### Локальная установка PostgreSQL и Redis

Если вы предпочитаете устанавливать сервисы локально, убедитесь, что PostgreSQL и Redis запущены и доступны по указанным в `.env` адресам.

## Запуск

**Перед запуском убедитесь, что виртуальное окружение активировано!**

### Запуск FastAPI приложения

```bash
# Убедитесь, что venv активирован (в начале строки должно быть (venv))
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: http://localhost:8000

Документация API: http://localhost:8000/docs

### Запуск воркера TaskIQ

В отдельном терминале (также с активированным venv):

```bash
# Активируйте venv в новом терминале
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Запустите воркер
taskiq worker app.tasks.broker
```

## Миграции Alembic

### Создание миграции

```bash
alembic revision --autogenerate -m "Initial migration"
```

### Применение миграций

```bash
alembic upgrade head
```

### Откат миграции

```bash
alembic downgrade -1
```

## Использование

### API Endpoints

- `GET /` - Главная страница
- `GET /health` - Проверка здоровья приложения
- `GET /users/` - Список пользователей
- `GET /users/{user_id}` - Получить пользователя
- `POST /users/` - Создать пользователя
- `POST /tasks/example` - Запустить пример задачи
- `POST /tasks/notify` - Запустить задачу уведомления

### Пример использования TaskIQ

В коде можно запускать задачи асинхронно:

```python
from app.tasks.example_tasks import example_task

# Запуск задачи
task = await example_task.kiq("Hello, World!")
```

## Технологии

- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** (async) - асинхронный ORM для работы с базой данных
- **asyncpg** - асинхронный драйвер для PostgreSQL
- **Alembic** - инструмент для миграций базы данных
- **TaskIQ** - асинхронная очередь задач
- **PostgreSQL** - реляционная база данных
- **Redis** - брокер сообщений для TaskIQ

## Особенности

- **Асинхронная работа с БД**: Проект использует асинхронный SQLAlchemy для максимальной производительности
- Все API endpoints работают асинхронно
- Миграции Alembic используют синхронный доступ (автоматическое преобразование URL)
- **Docker Compose для разработки**: Готовый docker-compose.dev.yaml для быстрого запуска PostgreSQL и Redis

