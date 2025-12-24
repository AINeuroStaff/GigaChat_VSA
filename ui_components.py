"""
Проект: GigaChat_for_VSA
Версия: 4.0
Статус: Подстановка системного промта из .txt файла, выбор модели GigaChat-2 / GigaChat-2-Pro / GigaChat-2-Max
        и разбор JSON-ответа (answer.user).

Модуль: ui_components.py
Разработчик: GEN AI + @AI_NeuroStaff / Dubinin Vladimir

Назначение:
- Вспомогательные функции для рендеринга элементов пользовательского интерфейса
  в Streamlit (сообщения чата, ошибки, описания).

Переменные:
- В этом модуле глобальных изменяемых переменных не используется.

Функции:
- render_message(msg: dict) -> None
    Отрисовывает одно сообщение чата в зависимости от роли ("user"/"assistant"/"system").
    Вызывается из:
        - app.py при рендеринге истории диалога.
- render_error(error_text: str) -> None
    Показывает в интерфейсе текст ошибки (например, ошибку API).
    Вызывается из:
        - app.py при наличии st.session_state.last_error.
"""

import streamlit as st


def render_message(msg: dict) -> None:
    """
    Отрисовать одно сообщение чата в интерфейсе Streamlit.

    Параметры:
    - msg: словарь с ключами:
        - "role": "user" | "assistant" | "system"
        - "content": str
        - любые дополнительные поля (игнорируются в базовой версии)

    Поведение:
    - Для "user" выводится чат-бабл пользователя.
    - Для "assistant" выводится чат-бабл ассистента, текст форматируется как markdown.
    - Для "system" по умолчанию не отображается (можно включить в debug-режиме).
    """
    role = msg.get("role", "user")
    content = msg.get("content", "")

    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)
    elif role == "assistant":
        with st.chat_message("assistant"):
            st.markdown(content)
    elif role == "system":
        # По желанию: можно выводить как отдельный блок или пропускать
        # with st.chat_message("assistant"):
        #     st.caption(f"System: {content}")
        pass
    else:
        # Непредвиденная роль — отображаем как обычное сообщение
        with st.chat_message("assistant"):
            st.markdown(content)


def render_error(error_text: str) -> None:
    """
    Отрисовать сообщение об ошибке в интерфейсе.

    Параметры:
    - error_text: человеко-читаемое описание ошибки.

    Вызывается из:
    - app.py при наличии ошибки в состоянии.
    """
    if not error_text:
        return
    st.error(f"Ошибка: {error_text}")
