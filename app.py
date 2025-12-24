"""
Проект: GigaChat_for_VSA
Версия: 4.0
Статус: Подстановка системного промта из .txt файла, выбор модели GigaChat-2 / GigaChat-2-Pro / GigaChat-2-Max
        и разбор JSON-ответа (answer.user).

Модуль: app.py
Разработчик: GEN AI + @AI_NeuroStaff / Dubinin Vladimir

Запуск: streamlit run app.py

Назначение:
- Основное Streamlit-приложение (витрина чата для LLM-агента GigaChat).
- Организация пользовательского интерфейса, логики ввода/вывода
  и интеграции с модулем gigachat_client.py.

Переменные:
- В модуле используются только локальные переменные и состояние st.session_state.
  Ключевые поля st.session_state определены и описаны в модуле state.py.

Функции:
- render_sidebar() -> None
    Отрисовывает боковую панель с настройками:
        - выбор режима (config.AVAILABLE_MODES),
        - параметры модели (temperature, max_tokens),
        - кнопка очистки диалога.
    Обновляет соответствующие значения в st.session_state.
- render_chat() -> None
    Отрисовывает:
        - историю сообщений чата (вызывая ui_components.render_message),
        - поле ввода для нового сообщения пользователя,
        - логику отправки запроса к GigaChat через gigachat_client.generate_reply.
- main() -> None
    Точка входа приложения:
        - инициализирует состояние через state.init_state,
        - настраивает страницу,
        - вызывает render_sidebar и render_chat.

Связи с другими модулями:
- state.py:
    - init_state(), add_message(), clear_chat(), set_error().
- config.py:
    - AVAILABLE_MODES, PROJECT_NAME, PROJECT_VERSION.
- gigachat_client.py:
    - generate_reply().
- ui_components.py:
    - render_message(), render_error().
"""

import streamlit as st

from config import AVAILABLE_MODES, PROJECT_NAME, PROJECT_VERSION
from state import init_state, add_message, clear_chat, set_error
from gigachat_client import generate_reply
from ui_components import render_message, render_error


st.set_page_config(
    page_title=f"{PROJECT_NAME} v{PROJECT_VERSION}",
    layout="wide",
)


def render_sidebar() -> None:
    """Отрисовка боковой панели с настройками режима и модели."""
    st.sidebar.title("Настройки агента")

    # Выбор режима
    current_mode = st.session_state.mode
    mode_names = list(AVAILABLE_MODES.keys())
    mode_index = mode_names.index(current_mode) if current_mode in mode_names else 0

    selected_mode = st.sidebar.selectbox(
        "Режим",
        options=mode_names,
        index=mode_index,
    )

    if selected_mode != st.session_state.mode:
        st.session_state.mode = selected_mode
        st.session_state.system_prompt = AVAILABLE_MODES[selected_mode]["system_prompt"]
        # clear_chat()  # опционально

    # --- ВЫБОР МОДЕЛИ LLM ---
    model_options = ["GigaChat-2", "GigaChat-2-Pro", "GigaChat-2-Max"]
    current_model = getattr(st.session_state, "model_name", "GigaChat-2")
    model_index = model_options.index(current_model) if current_model in model_options else 0

    selected_model = st.sidebar.selectbox(
        "Модель LLM",
        options=model_options,
        index=model_index,
    )
    st.session_state.model_name = selected_model
    # --- КОНЕЦ БЛОКА ВЫБОРА МОДЕЛИ ---

    # Параметры модели
    temperature = st.sidebar.slider(
        "Температура",
        min_value=0.0,
        max_value=1.0,
        step=0.05,
        value=st.session_state.model_params.get("temperature", 0.5),
    )
    max_tokens = st.sidebar.slider(
        "Длина ответа",
        min_value=256,
        max_value=4096,
        step=256,
        value=st.session_state.model_params.get("max_tokens", 1024),
    )
    st.session_state.model_params["temperature"] = temperature
    st.session_state.model_params["max_tokens"] = max_tokens

    # Кнопка очистки диалога
    if st.sidebar.button("Очистить диалог"):
        clear_chat()

    # Инфо-блок
    st.sidebar.markdown(
        f"**Проект:** {PROJECT_NAME}  \n"
        f"**Версия:** {PROJECT_VERSION}"
    )

# --- ПОДВАЛ СТРАНИЦЫ ---
    st.sidebar.markdown(
        """
        <div style="font-size: 12px; color: #666; margin-top: 8px;">
            <div>2025 · © Дубинин Владимир</div>
            <div>ОГРНИП 325180000101289</div>
            <div>г. Старый Оскол</div>
            <div style="margin-top: 6px;">
                Сайт продукта:<br>
                <a href="http://solution-architect.tilda.ws/" target="_blank">
                    VSA — AI-агент в мире кодинга
                </a>
            </div>
            <div style="margin-top: 4px;">
                Обратная связь:<br>
                <a href="https://t.me/AI_Services_VSA" target="_blank">
                    Команда разработки
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_chat() -> None:
    """Отрисовка основной зоны чата: история, ввод, вызов модели."""
    st.title("Sber500 - Международный IT-акселератор")

    # Верхняя плашка
    st.markdown(
        """
        <div style="
            padding: 8px 16px;
            border-radius: 6px;
            background: #152642;
            color: white;
            font-size: 20px;
            margin-bottom: 12px;
        ">
            Виртуальный Ассистент - Solution Architect \ Системный Программный Архитектор 
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Баннер-изображение под плашкой (по желанию)
    # st.image("assets/sber01.png", use_column_width=True)

    st.caption(
        f"Текущий режим: **{st.session_state.mode}** · "
        f"Модель: **{getattr(st.session_state, 'model_name', 'GigaChat-2')}**"
    )

    # Отобразить историю сообщений
    for msg in st.session_state.messages:
        render_message(msg)

    # Показать ошибку, если есть
    if st.session_state.last_error:
        render_error(st.session_state.last_error)

    # Поле ввода сообщения пользователя
    user_input: str | None = st.chat_input("Введите сообщение")


    if user_input:
        # Очистить предыдущую ошибку
        set_error(None)

        # Добавить пользовательское сообщение
        add_message("user", user_input)

        # Отрисовать его сразу
        with st.chat_message("user"):
            st.markdown(user_input)

        # Показать "думающего" ассистента
        st.session_state.is_thinking = True
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("_Агент формирует ответ..._")

            try:
                reply_text = generate_reply(
                    messages=st.session_state.messages,
                    model_params=st.session_state.model_params,
                    system_prompt=st.session_state.system_prompt,
                    model_name=getattr(st.session_state, "model_name", "GigaChat-2"),
                )
            except Exception as exc:  # noqa: BLE001
                error_message = f"Ошибка при обращении к GigaChat: {exc}"
                set_error(error_message)
                placeholder.markdown("_Возникла ошибка при получении ответа._")
                st.session_state.is_thinking = False
                return

            # Обновить вывод с полученным текстом
            placeholder.markdown(reply_text)

        # Добавить ответ ассистента в историю
        add_message("assistant", reply_text)
        st.session_state.is_thinking = False



def main() -> None:
    """Точка входа приложения."""
    init_state()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()
