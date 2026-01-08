from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor

class TimerComponent(QWidget):
    """Flow State Timer Component."""
    
    def __init__(self):
        super().__init__()
        self.duration = 25 * 60  # 25 minutes default
        self.remaining = self.duration
        self.is_running = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.timer.setInterval(1000)
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 25, 20, 25)
        layout.setSpacing(25)
        
        # --- Timer Card ---
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 35, 200);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 30)
        card_layout.setSpacing(20)
        
        # Header Row (Title + Edit Button)
        header_layout = QHBoxLayout()
        lbl = QLabel("TIMER")
        lbl.setStyleSheet("color: #e8eaed; font-size: 14px; font-weight: bold; letter-spacing: 1px; background: transparent; border: none;")
        header_layout.addWidget(lbl)
        
        header_layout.addStretch()
        
        self.edit_btn = QPushButton("✎")
        self.edit_btn.setToolTip("Edit Duration")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.setFixedSize(30, 30)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                color: #9e9e9e;
                border-radius: 15px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }
        """)
        self.edit_btn.clicked.connect(self._edit_duration)
        header_layout.addWidget(self.edit_btn)
        
        card_layout.addLayout(header_layout)
        
        # Timer Display
        self.time_display = QLabel("25:00")
        self.time_display.setAlignment(Qt.AlignCenter)
        self.time_display.setStyleSheet("""
            color: #bd93f9; 
            font-size: 56px; 
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            background: transparent;
            border: none;
        """)
        card_layout.addWidget(self.time_display)
        
        # Controls (Start/Pause + Reset)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Start Button
        self.start_btn = QPushButton("START")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setFixedHeight(50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #bd93f9, stop:1 #4F8EF7);
                color: white;
                border-radius: 25px;
                font-weight: bold;
                font-size: 16px;
                border: none;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a87df0, stop:1 #3d7be5);
            }
            QPushButton:pressed {
                background: #333;
            }
        """)
        self.start_btn.clicked.connect(self._toggle_timer)
        controls_layout.addWidget(self.start_btn, 1) # Stretch 1
        
        # Reset Button
        self.reset_btn = QPushButton("↺")
        self.reset_btn.setToolTip("Reset Timer")
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.setFixedSize(50, 50)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                color: #e8eaed;
                border-radius: 25px;
                font-size: 20px;
                border: none;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                color: #4F8EF7;
            }
        """)
        self.reset_btn.clicked.connect(self._reset_timer)
        controls_layout.addWidget(self.reset_btn)
        
        card_layout.addLayout(controls_layout)
        
        layout.addWidget(card)
        layout.addStretch()

    def _toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.start_btn.setText("RESUME")
            self.is_running = False
        else:
            self.timer.start()
            self.start_btn.setText("PAUSE")
            self.is_running = True
            
    def _reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.start_btn.setText("START")
        self.remaining = self.duration
        self._update_display()

    def _edit_duration(self):
        from PySide6.QtWidgets import QInputDialog
        minutes, ok = QInputDialog.getInt(
            self, "Set Timer", "Duration (minutes):", 
            value=self.duration // 60, minValue=1, maxValue=180
        )
        if ok:
            self.duration = minutes * 60
            self._reset_timer()

    def _update_timer(self):
        if self.remaining > 0:
            self.remaining -= 1
            self._update_display()
        else:
            self.timer.stop()
            self.is_running = False
            self.start_btn.setText("START")
            self.remaining = self.duration
            self._update_display()
            # Could play sound here

    def _update_display(self):
        m, s = divmod(self.remaining, 60)
        self.time_display.setText(f"{m:02d}:{s:02d}")
