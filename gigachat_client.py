"""
Проект: GigaChat_for_VSA
Версия: 4.0
Статус: Подстановка системного промта из .txt файла, выбор модели GigaChat-2 / GigaChat-2-Pro / GigaChat-2-Max
        и разбор JSON-ответа (answer.user).

Модуль: gigachat_client.py
Разработчик: GEN AI + @AI_NeuroStaff / Dubinin Vladimir

Назначение:
- Обёртка над GigaChat API (через официальный Python-SDK).
- Использование корневого сертификата НУЦ Минцифры из файла проекта
  для корректной проверки SSL-соединения.
- Предоставление функции generate_reply для получения ответа модели.

Переменные:
- GIGACHAT_CREDENTIALS: str | None
    Ключ авторизации GigaChat (client_id:client_secret или иной формат, см. доку).
    Считывается из переменной окружения или st.secrets.
- GIGACHAT_SCOPE: str | None
    Область доступа (например, "GIGACHAT_API_PERS").
- GIGACHAT_MODEL: str
    Имя модели по умолчанию (например, "GigaChat").
- GIGACHAT_CA_BUNDLE_FILE: str | None
    Путь к файлу с корневым сертификатом НУЦ Минцифры в формате CER.
    Считывается из переменной окружения или st.secrets и передаётся в SDK
    через параметр ca_bundle_file.

Функции:
- _get_settings_from_env() -> dict
    Внутренняя функция. Читает настройки GigaChat (credentials, scope, model,
    ca_bundle_file) из переменных окружения. Используется как запасной вариант.
- _get_settings_from_streamlit() -> dict
    Внутренняя функция. Пытается прочитать те же настройки из st.secrets
    (если Streamlit доступен и secrets настроены).
- _resolve_settings() -> dict
    Объединяет настройки из st.secrets и окружения, st.secrets имеет приоритет.
- _create_client() -> GigaChat
    Внутренняя функция. Создаёт и возвращает клиент GigaChat SDK,
    используя настройки (включая путь к сертификату).
- generate_reply(messages: list[dict], model_params: dict | None, system_prompt: str | None) -> str
    Публичная функция. Формирует запрос к GigaChat и возвращает текст ответа.
    Вызывается из app.py при обработке нового сообщения пользователя.
"""

from typing import List, Dict, Optional
import os
import json

import requests  # Для блока проверки сертификата

try:
    import streamlit as st  # для чтения st.secrets, если запущено в Streamlit
except ImportError:
    st = None  # type: ignore

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from config import DEFAULT_MODEL_PARAMS


def _get_settings_from_env() -> dict:
    """
    Прочитать настройки GigaChat из переменных окружения.

    Ожидаемые переменные:
    - GIGACHAT_CREDENTIALS
    - GIGACHAT_SCOPE
    - GIGACHAT_MODEL
    - GIGACHAT_CA_BUNDLE_FILE

    Возвращает:
    - словарь с ключами: credentials, scope, model, ca_bundle_file.
    """
    return {
        "credentials": os.environ.get("GIGACHAT_CREDENTIALS"),
        "scope": os.environ.get("GIGACHAT_SCOPE"),
        "model": os.environ.get("GIGACHAT_MODEL", "GigaChat-2"),
        "ca_bundle_file": os.environ.get("GIGACHAT_CA_BUNDLE_FILE"),
    }


def _get_settings_from_streamlit() -> dict:
    """
    Прочитать настройки GigaChat из st.secrets, если приложение
    запущено в контексте Streamlit и secrets настроены.

    Ожидаемые ключи в st.secrets["gigachat"]:
    - credentials
    - scope
    - model
    - ca_bundle_file (относительный путь к файлу сертификата в репозитории)

    Возвращает:
    - словарь с теми же ключами, что и _get_settings_from_env().
    """
    if st is None or "gigachat" not in st.secrets:
        return {}

    cfg = st.secrets["gigachat"]
    return {
        "credentials": cfg.get("credentials"),
        "scope": cfg.get("scope"),
        "model": cfg.get("model", "GigaChat-2"),
        "ca_bundle_file": cfg.get("ca_bundle_file"),
    }


def _resolve_settings() -> dict:
    """
    Объединить настройки из st.secrets и переменных окружения.

    Приоритет:
    1) st.secrets["gigachat"]
    2) переменные окружения

    Возвращает:
    - словарь с полями credentials, scope, model, ca_bundle_file.
    """
    settings = _get_settings_from_env()

    if st is not None:
        secrets_settings = _get_settings_from_streamlit()
        for key, value in secrets_settings.items():
            if value is not None:
                settings[key] = value

    return settings


def _create_client() -> GigaChat:
    """
    Создать клиент GigaChat SDK с учётом сертификата НУЦ Минцифры.

    - Берёт настройки через _resolve_settings().
    - Параметр ca_bundle_file указывает на файл сертификата в проекте.
    """
    settings = _resolve_settings()

    credentials = settings.get("credentials")
    scope = settings.get("scope")
    model = settings.get("model", "GigaChat-2")
    ca_bundle_file = settings.get("ca_bundle_file")

    if not credentials or not scope:
        raise RuntimeError(
            "Не заданы параметры GigaChat (credentials/scope). "
            "Укажите их в st.secrets['gigachat'] или в переменных окружения."
        )

    # --- БЛОК ПРОВЕРКИ СЕРТИФИКАТА ---
    test_url = "https://gigachat.devices.sberbank.ru"
    try:
        requests.get(test_url, timeout=5, verify=ca_bundle_file)
    except requests.exceptions.SSLError as ssl_err:
        raise RuntimeError(
            f"Ошибка проверки SSL-сертификата GigaChat. "
            f"Проверь ca_bundle_file='{ca_bundle_file}': {ssl_err}"
        ) from ssl_err
    except Exception:
        # другие ошибки здесь не критичны для SSL-проверки
        pass
    # --- КОНЕЦ БЛОКА ПРОВЕРКИ СЕРТИФИКАТА ---

    client = GigaChat(
        credentials=credentials,
        scope=scope,
        model=model,
        ca_bundle_file=ca_bundle_file,
        verify_ssl_certs=True,
    )

    return client


def generate_reply(
    messages: List[Dict[str, str]],
    model_params: Optional[Dict[str, float]] = None,
    system_prompt: Optional[str] = None,
    model_name: Optional[str] = None,
) -> str:
    """
    Сгенерировать ответ от GigaChat.

    - messages: [{"role": "user"|"assistant"|"system", "content": "..."}]
    - model_params: temperature, max_tokens и т.п.
    - system_prompt: дополнительный системный промпт.
    - model_name: имя модели ("GigaChat-2", "GigaChat-2-Pro", "GigaChat-2-Max").
      Если не указано, берётся модель из настроек (_resolve_settings()).

    Возвращает:
    - reply_text: строка, которая пойдёт в UI (answer.user, если пришёл JSON).
    """
    if model_params is None:
        model_params = DEFAULT_MODEL_PARAMS.copy()

    settings = _resolve_settings()
    effective_model_name = model_name or settings.get("model", "GigaChat-2")

    # Формируем список Messages в формате SDK
    sdk_messages: List[Messages] = []

    if system_prompt:
        sdk_messages.append(
            Messages(
                role=MessagesRole.SYSTEM,
                content=system_prompt,
            )
        )

    for m in messages:
        role_str = m.get("role", "user")
        if role_str == "user":
            role = MessagesRole.USER
        elif role_str == "assistant":
            role = MessagesRole.ASSISTANT
        elif role_str == "system":
            role = MessagesRole.SYSTEM
        else:
            role = MessagesRole.USER

        sdk_messages.append(
            Messages(
                role=role,
                content=m.get("content", ""),
            )
        )

    payload = Chat(
        messages=sdk_messages,
        temperature=model_params.get("temperature", 0.5),
        max_tokens=model_params.get("max_tokens", 1024),
        model=effective_model_name,
    )

    client = _create_client()
    response = client.chat(payload)

    # Оригинальный текст от модели
    raw_content = response.choices[0].message.content

    # Ожидаемый формат:
    # {
    #   "answer": {
    #     "reasoning": "длинный текст...",
    #     "user": "длинный текст..."
    #   }
    # }
    try:
        data = json.loads(raw_content)
        reply_text = (
            data.get("answer", {}).get("user")
            or raw_content  # fallback, если структура не совпала
        )
    except (json.JSONDecodeError, TypeError):
        reply_text = raw_content

    return reply_text