"""
Test settings for the project.
"""

# Import only what we need
from .settings import BASE_DIR

# Используем SQLite для тестов (быстрее)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

# Отключаем кэширование для тестов
CACHE_ENABLED = False

# Используем консольный бэкенд для email в тестах
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Ускоряем тесты
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Отключаем логирование для тестов
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
    },
}

# Настройки для тестирования
TEST_RUNNER = "django.test.runner.DiscoverRunner"
