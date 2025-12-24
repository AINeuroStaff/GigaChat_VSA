"""
Проект: GigaChat_for_VSA
Версия: 4.0
Статус: Подстановка системного промта из .txt файла, выбор модели GigaChat-2 / GigaChat-2-Pro / GigaChat-2-Max
        и разбор JSON-ответа (answer.user).

Модуль: state.py
Разработчик: GEN AI + @AI_NeuroStaff / Dubinin Vladimir

Назначение:
- Управление состоянием сессии Streamlit (st.session_state).
- Централизованная инициализация и модификация внутренних переменных состояния.

Переменные (внутри st.session_state):
- messages: list[dict]
    История сообщений чата в формате словарей:
    {
        "role": "user" | "assistant" | "system",
        "content": str
    }.
- system_prompt: str
    Текущий системный промпт, определяющий поведение агента.
- model_params: dict
    Параметры модели (например: temperature, max_tokens).
- mode: str
    Текущий выбранный режим работы агента (ключ из config.AVAILABLE_MODES).
- is_thinking: bool
    Флаг, показывающий, что сейчас ожидается ответ от модели.
- last_error: str | None
    Текст последней ошибки (если была), для отображения в UI.

Функции:
- init_state() -> None
    Инициализирует все необходимые поля в st.session_state, если они отсутствуют.
    Использует константы из модуля config.py.
- add_message(role: str, content: str, **meta) -> None
    Добавляет сообщение в историю сообщений st.session_state.messages.
    Вызывается из:
        - app.py для добавления пользовательских и ассистентских сообщений.
- clear_chat() -> None
    Очищает историю сообщений и сбрасывает флаг ошибки.
    Вызывается из:
        - app.py при нажатии кнопки "Очистить диалог".
- set_error(error_text: str | None) -> None
    Сохраняет текст ошибки в st.session_state.last_error (или очищает, если None).
    Вызывается из:
        - app.py при обработке ошибок взаимодействия с API GigaChat.
"""

from typing import Optional

import streamlit as st

from config import DEFAULT_SYSTEM_PROMPT, DEFAULT_MODEL_PARAMS, AVAILABLE_MODES


def init_state() -> None:
    """
    Инициализация ключевых полей st.session_state.

    Ветвления внутри функции проверяют, существует ли уже соответствующий ключ
    в состоянии сессии. Если ключ отсутствует (первая загрузка приложения
    или новая сессия пользователя), создаётся значение по умолчанию.

    Это важно, потому что:
    - Streamlit переиспользует состояние между перерисовками страницы;
    - нельзя без проверки перезаписывать значения, которые пользователь
      уже изменил (например, выбранный режим или параметры модели).
    """

    # 1. История сообщений чата
    # Если список сообщений ещё не создан — создаём пустой список.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 2. Режим работы агента
    # Если режим ещё не выбран — берём первый доступный режим из AVAILABLE_MODES.
    if "mode" not in st.session_state:
        default_mode = list(AVAILABLE_MODES.keys())[0]
        st.session_state.mode = default_mode

    # 3. Системный промпт
    # Если системный промпт ещё не задан — используем значение,
    # соответствующее текущему режиму.
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = AVAILABLE_MODES[
            st.session_state.mode
        ]["system_prompt"]

    # 4. Параметры модели
    # Если параметры модели ещё не инициализированы — создаём копию
    # дефолтного словаря, чтобы изменения одного пользователя не влияли
    # на других.
    if "model_params" not in st.session_state:
        st.session_state.model_params = DEFAULT_MODEL_PARAMS.copy()

    # 5. Флаг «модель думает»
    # Если флаг ещё не создан — устанавливаем False (модель сейчас не отвечает).
    if "is_thinking" not in st.session_state:
        st.session_state.is_thinking = False

    # 6. Последняя ошибка
    # Если хранилище ошибки ещё не создано — инициализируем значением None
    # (ошибок пока нет).
    if "last_error" not in st.session_state:
        st.session_state.last_error = None 


def add_message(role: str, content: str, **meta) -> None:
    """
    Добавить сообщение в историю.

    Параметры:
    - role: роль сообщения ("user", "assistant", "system").
    - content: текст сообщения.
    - meta: дополнительные необязательные данные (например, timestamp, debug-инфо),
      могут быть использованы UI-слоем.

    Вызывается из:
    - app.py при добавлении сообщений пользователя и ассистента.
    """
    message: dict = {"role": role, "content": content}
    if meta:
        message.update(meta)
    st.session_state.messages.append(message)


def clear_chat() -> None:
    """
    Очистить историю чата и сбросить последнюю ошибку.

    Вызывается из:
    - app.py по нажатию кнопки "Очистить диалог" в sidebar.
    """
    st.session_state.messages = []
    st.session_state.last_error = None


def set_error(error_text: Optional[str]) -> None:
    """
    Установить или очистить текст ошибки.

    Параметры:
    - error_text: текст ошибки или None для очистки.

    Вызывается из:
    - app.py при обработке исключений и ошибок API.
    """
    st.session_state.last_error = error_text
