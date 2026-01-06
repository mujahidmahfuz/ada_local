"""
ThinkingExpander component - Gemini-style collapsible thinking UI.
"""

import flet as ft


class ThinkingExpander(ft.ExpansionTile):
    """Gemini-style collapsible thinking UI."""
    
    def __init__(self):
        super().__init__(
            title=ft.Text("Thinking Process", size=12, color=ft.Colors.GREY_400),
            leading=ft.ProgressRing(width=16, height=16, stroke_width=2),
            bgcolor=ft.Colors.TRANSPARENT,
            collapsed_bgcolor=ft.Colors.TRANSPARENT,
            maintain_state=True,
            shape=ft.RoundedRectangleBorder(radius=8),
            collapsed_shape=ft.RoundedRectangleBorder(radius=8),
            tile_padding=ft.Padding(0, 0, 0, 0),
        )
        
        self.log_view = ft.Column(
            controls=[], 
            spacing=2,
        )
        
        self.controls = [
            ft.Container(
                content=self.log_view,
                padding=10,
                bgcolor="#202020",
                border_radius=8,
                margin=ft.Margin.only(bottom=10)
            )
        ]
        
    def add_text(self, text):
        """Add text to the thinking log."""
        if not self.log_view.controls:
            self.log_view.controls.append(
                ft.Text("", font_family="Roboto Mono", size=11, color="#a0a0a0", selectable=True)
            )
        
        self.log_view.controls[-1].value += text
        try:
            self.update()
        except RuntimeError:
            # Control not yet added to page, skip update
            pass
        
    def complete(self):
        """Mark thinking as complete."""
        self.leading = ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=16, color=ft.Colors.GREEN_400)
        self.title.value = "Thinking Finished"
        self.title.color = ft.Colors.GREEN_400
        try:
            self.update()
        except RuntimeError:
            # Control not yet added to page, skip update
            pass
