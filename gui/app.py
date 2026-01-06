"""
Main Flet application setup and layout.
"""

import flet as ft
import threading

from core.llm import preload_models
from core.tts import tts
from gui.handlers import ChatHandlers


def main(page: ft.Page):
    """Main application entry point."""
    
    # --- Page Configuration ---
    page.title = "Pocket AI"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window.width = 480
    page.window.height = 800
    page.bgcolor = "#1a1c1e"
    
    page.fonts = {
        "Roboto Mono": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf"
    }

    # --- UI Components ---
    chat_list = ft.ListView(
        expand=True,
        spacing=15,
        auto_scroll=True,
        padding=10
    )

    status_text = ft.Text("Initializing...", size=12, color=ft.Colors.GREY_500)
    
    user_input = ft.TextField(
        hint_text="Ask something...",
        border_radius=25,
        filled=True,
        bgcolor="#2b2d31",
        border_color=ft.Colors.TRANSPARENT,
        expand=True,
        autofocus=True,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=10),
    )

    send_button = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED, 
        icon_color=ft.Colors.BLUE_200,
        bgcolor="#2b2d31",
        tooltip="Send"
    )
    
    stop_button = ft.IconButton(
        icon=ft.Icons.STOP_CIRCLE_OUTLINED,
        icon_color=ft.Colors.RED_400,
        bgcolor="#2b2d31",
        visible=False,
        tooltip="Stop Generation"
    )

    # --- Initialize Handlers ---
    handlers = ChatHandlers(
        page=page,
        chat_list=chat_list,
        status_text=status_text,
        user_input=user_input,
        send_button=send_button,
        stop_button=stop_button
    )
    
    # Wire up events
    user_input.on_submit = handlers.send_message
    send_button.on_click = handlers.send_message
    stop_button.on_click = handlers.stop_generation

    # --- Layout ---
    app_bar = ft.Row([
        ft.Text("Pocket AI", size=20, weight=ft.FontWeight.BOLD),
        ft.Container(expand=True),
        ft.IconButton(ft.Icons.CLEAN_HANDS_ROUNDED, tooltip="Clear Chat", on_click=handlers.clear_chat, icon_color=ft.Colors.GREY_500),
        ft.Text("Voice", size=12, color=ft.Colors.GREY_400),
        ft.Switch(value=True, on_change=handlers.toggle_tts, scale=0.8)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    input_bar = ft.Container(
        content=ft.Row([
            user_input,
            stop_button,
            send_button
        ]),
        padding=ft.Padding.only(top=10)
    )

    page.add(
        ft.Column([
            app_bar,
            status_text,
            ft.Divider(color=ft.Colors.GREY_800),
            chat_list,
            input_bar
        ], expand=True)
    )

    # --- Initial Preload ---
    def preload_background():
        status_text.value = "Warming up models..."
        page.update()
        preload_models()
        if tts.toggle(True):
            status_text.value = "Ready | TTS Active"
        else:
            status_text.value = "Ready | TTS Failed"
        page.update()

    threading.Thread(target=preload_background, daemon=True).start()
