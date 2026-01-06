"""
MessageBubble component - Styled chat message bubble.
"""

import flet as ft


class MessageBubble(ft.Container):
    """A styled message bubble for User or AI."""
    
    def __init__(self, role, text="", is_thinking=False):
        super().__init__()
        self.role = role
        self.is_thinking = is_thinking
        
        # Style Config
        is_user = role == "user"
        bg_color = "#005c4b" if is_user else "#363636"
        align = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        border_radius = ft.BorderRadius.only(
            top_left=15, top_right=15, 
            bottom_left=15 if is_user else 0,
            bottom_right=0 if is_user else 15
        )
        
        # Content
        if is_thinking:
            self.content = ft.Text(text, color=ft.Colors.GREY_400, italic=True, font_family="Roboto Mono", size=12)
            bg_color = "#2a2a2a"
        else:
            self.content = ft.Markdown(
                text, 
                selectable=True, 
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                code_theme="atom-one-dark",
                on_tap_link=lambda e: self.page.launch_url(e.data) if self.page else None
            )

        self.bgcolor = bg_color
        self.padding = 15
        self.border_radius = border_radius
        self.expand = False
        self.width = None 
        
        # Layout Helper
        self.row_wrap = ft.Row([self], alignment=align, vertical_alignment=ft.CrossAxisAlignment.START)
