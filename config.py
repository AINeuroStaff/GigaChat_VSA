"""
Проект: GigaChat_for_VSA
Версия: 4.0
Статус: Подстановка системного промта из .txt файла, выбор модели GigaChat-2 / GigaChat-2-Pro / GigaChat-2-Max
        и разбор JSON-ответа (answer.user).
Подстановка системных промптов из файлов Prompts/*.txt
Модуль: config.py
Разработчик: GEN AI + @AI_NeuroStaff / Dubinin Vladimir

Назначение:
- Хранение глобальных констант и конфигурации проекта.

Переменные:
- PROJECT_NAME: str
    Название проекта.
- PROJECT_VERSION: str
    Текущая версия проекта.
- DEFAULT_SYSTEM_PROMPT: str
    Базовый системный промпт для LLM-агента по умолчанию.
- DEFAULT_MODEL_PARAMS: dict
    Словарь параметров модели (temperature, max_tokens и т.п.).
- AVAILABLE_MODES: dict
    Словарь доступных режимов работы агента, где ключ — имя режима,
    значение — словарь настроек режима (в частности system_prompt).

Функции:
- В этом модуле функций нет. Значения констант импортируются
  из других модулей (app.py, state.py, gigachat_client.py) по мере необходимости.
"""

from pathlib import Path

PROJECT_NAME: str = "GigaChat_for_VSA"
PROJECT_VERSION: str = "4.0"

# Корень проекта = директория, где лежит этот файл
BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "Prompts"


def _read_prompt(filename: str, fallback: str) -> str:
    """
    Читает текст промпта из файла Prompts/filename.
    Если файл отсутствует или не читается — возвращает fallback-текст.
    """
    path = PROMPTS_DIR / filename
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return fallback.strip()


# Базовые тексты по умолчанию (на случай отсутствия файлов)
DEFAULT_ASSISTENT_PROMPT = (
    "Ты умный и лаконичный ассистент. Отвечай чётко и по сути, "
    "используя понятные формулировки и по возможности примеры."
)

DEFAULT_CODER_PROMPT = (
    "Ты опытный разработчик. Объясняй решение кратко, приводя примеры кода "
    "и минимально необходимую теорию."
)

DEFAULT_ANALYST_PROMPT = (
    "Ты бизнес-аналитик. Отвечай структурированно, выделяй ключевые тезисы, "
    "делай короткие выводы и рекомендации."
)

# Чтение промптов из файлов
DEFAULT_SYSTEM_PROMPT: str = _read_prompt("Assistent.txt", DEFAULT_ASSISTENT_PROMPT)
CODER_SYSTEM_PROMPT: str = _read_prompt("Coder.txt", DEFAULT_CODER_PROMPT)
ANALYST_SYSTEM_PROMPT: str = _read_prompt("Analyst.txt", DEFAULT_ANALYST_PROMPT)

DEFAULT_MODEL_PARAMS: dict = {
    "temperature": 0.1,
    "max_tokens": 8192,
}

AVAILABLE_MODES: dict = {
    "Ассистент": {
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
    },
    "Кодер": {
        "system_prompt": CODER_SYSTEM_PROMPT,
    },
    "Аналитик": {
        "system_prompt": ANALYST_SYSTEM_PROMPT,
    },
}