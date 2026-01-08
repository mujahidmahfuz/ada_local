from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor, QFont

class NewsCard(QFrame):
    """
    A card widget representing a single news story.
    """
    def __init__(self, article, parent=None):
        super().__init__(parent)
        self.article = article
        self.url = article.get('url')
        
        self.setObjectName("newsCard")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedHeight(160)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Image placeholder (Left side) - simple colored block or icon for now
        # In a real app we'd load the image asynchronously
        self.image_area = QLabel()
        self.image_area.setFixedSize(80, 80)
        self.image_area.setAlignment(Qt.AlignCenter)
        self.image_area.setStyleSheet(f"""
            background-color: {self._get_category_color(article.get('category'))};
            border-radius: 12px;
            font-size: 24px;
            color: rgba(255,255,255,0.8);
        """)
        self.image_area.setText(self._get_category_icon(article.get('category')))
        layout.addWidget(self.image_area)
        
        # Content (Right side)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)
        
        # Category & Time
        meta_layout = QHBoxLayout()
        category = QLabel(article.get('category', 'News').upper())
        category.setStyleSheet(f"color: {self._get_category_color(article.get('category'))}; font-weight: bold; font-size: 11px; letter-spacing: 1px;")
        meta_layout.addWidget(category)
        
        date = QLabel(f"• {article.get('date', 'Just now')}")
        date.setStyleSheet("color: #6e6e6e; font-size: 11px;")
        meta_layout.addWidget(date)
        meta_layout.addStretch()
        content_layout.addLayout(meta_layout)
        
        # Headline
        headline = QLabel(article.get('title', 'No Title'))
        headline.setWordWrap(True)
        headline.setStyleSheet("color: #e8eaed; font-size: 15px; font-weight: 600;")
        # headline.setFont(QFont("Segoe UI", 11, QFont.Bold))
        content_layout.addWidget(headline)
        
        # Source
        source = QLabel(article.get('source', 'Unknown Source'))
        source.setStyleSheet("color: #9e9e9e; font-size: 12px; font-style: italic;")
        content_layout.addWidget(source)
        
        content_layout.addStretch()
        layout.addLayout(content_layout)
        
        # Styling
        self.setStyleSheet("""
            QFrame#newsCard {
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
            }
            QFrame#newsCard:hover {
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(79, 142, 247, 0.3);
            }
        """)

    def _get_category_color(self, category):
        """Return color based on category."""
        cat = str(category).lower()
        if "tech" in cat: return "#4F8EF7" # Blue
        if "market" in cat or "finance" in cat: return "#4cd964" # Green
        if "science" in cat: return "#bd93f9" # Purple
        if "culture" in cat: return "#ff2d55" # Red/Pink
        return "#ffcc00" # Yellow default (Top Stories)

    def _get_category_icon(self, category):
        cat = str(category).lower()
        if "tech" in cat: return "💻"
        if "market" in cat: return "📈"
        if "science" in cat: return "🧬"
        if "culture" in cat: return "🎭" 
        return "📰"
    
    def mousePressEvent(self, event):
        """Open URL on click."""
        import webbrowser
        if self.url:
            webbrowser.open(self.url)
