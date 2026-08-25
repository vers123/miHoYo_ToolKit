"""GUI 主题与字体加载模块"""

import os
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import QApplication
from core.config_manager import config_manager

FONT_DIR = os.path.join(config_manager.get_project_root(), "resources", "font")

GAME_TITLE_FONTS = {
    "genshin":  "Genshin Impact/Teyvat-Black/ttf/TeyvatBlack-Regular.ttf",
    "starrail": "Star Rail/Star-Rail-Neue/ttf/StarRailNeue-Sans-Regular.ttf",
    "zzz":      "ZenlessZoneZero/ZZZ-System/ttf/ZZZSystem-Regular.ttf",
}

GAME_BODY_FONTS = {
    "zzz_body": "ZenlessZoneZero/ZZZ-A/ttf/ZZZA-Regular.ttf",
}

GAME_THEME_COLORS = {
    "genshin":  "#D4A03C",
    "zzz":      "#FF6B35",
    "starrail": "#4FC3F7",
}

LIGHT_QSS = """
QMainWindow {
    background: #f8f9fa;
}
QWidget {
    color: #1f2937;
    font-family: "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
    font-size: 14px;
}
QListWidget {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 6px;
    font-size: 15px;
}
QListWidget::item {
    padding: 10px 16px;
    border-radius: 4px;
    margin: 2px 0;
}
QListWidget::item:selected {
    background: #2563eb;
    color: #ffffff;
}
QListWidget::item:hover:!selected {
    background: #f0f1f3;
}
QStackedWidget {
    background: #f8f9fa;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 14px;
    min-width: 80px;
}
QPushButton:hover {
    background: #f0f1f3;
    border-color: #9ca3af;
}
QPushButton:pressed {
    background: #e5e7eb;
}
QPushButton:disabled {
    color: #9ca3af;
    background: #f3f4f6;
}
QPushButton#primaryBtn {
    background: #2563eb;
    color: #ffffff;
    border: none;
}
QPushButton#primaryBtn:hover {
    background: #1d4ed8;
}
QPushButton#dangerBtn {
    background: #ffffff;
    color: #dc2626;
    border: 1px solid #fca5a5;
}
QPushButton#dangerBtn:hover {
    background: #fef2f2;
}
QLineEdit, QSpinBox, QComboBox {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    padding: 6px 10px;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #2563eb;
}
QPlainTextEdit {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    font-family: "JetBrains Mono", "Consolas", "Cascadia Code", monospace;
    font-size: 13px;
    color: #374151;
}
QProgressBar {
    background: #e5e7eb;
    border: none;
    border-radius: 6px;
    text-align: center;
    height: 22px;
    font-size: 12px;
    color: #1f2937;
}
QProgressBar::chunk {
    background: #2563eb;
    border-radius: 6px;
}
QLabel#pageTitle {
    font-size: 18px;
    font-weight: bold;
    color: #1f2937;
    padding: 4px 0 8px 0;
}
QLabel#pageSubtitle {
    font-size: 13px;
    color: #6b7280;
    padding-bottom: 12px;
}
QSplitter::handle {
    background: #e5e7eb;
}
QStatusBar {
    background: #f0f1f3;
    color: #6b7280;
    border-top: 1px solid #e5e7eb;
}
QMenuBar {
    background: #f8f9fa;
    border-bottom: 1px solid #e5e7eb;
}
QMenuBar::item:selected {
    background: #e5e7eb;
}
QMenu {
    background: #ffffff;
    border: 1px solid #e5e7eb;
}
QMenu::item:selected {
    background: #f0f1f3;
}
QTableWidget {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    gridline-color: #f3f4f6;
}
QHeaderView::section {
    background: #f0f1f3;
    border: none;
    border-right: 1px solid #e5e7eb;
    padding: 6px 10px;
    font-weight: bold;
}
QTableWidget::item {
    padding: 4px 10px;
}
QScrollBar:vertical {
    background: #f8f9fa;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #d1d5db;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #9ca3af;
}
"""


def load_game_fonts() -> dict:
    """加载所有游戏字体到 QFontDatabase，返回 {key: family_name}"""
    loaded = {}
    all_fonts = {**GAME_TITLE_FONTS, **GAME_BODY_FONTS}
    for key, rel_path in all_fonts.items():
        font_path = os.path.join(FONT_DIR, rel_path)
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    loaded[key] = families[0]
    return loaded


def get_title_font(game_key: str, fonts: dict, size: int = 18) -> QFont:
    """获取指定游戏的标题字体"""
    family = fonts.get(game_key, "Microsoft YaHei")
    return QFont(family, size, QFont.Bold)


def get_game_color(game_key: str) -> str:
    """获取游戏主题色"""
    return GAME_THEME_COLORS.get(game_key, "#2563eb")


def apply_light_theme(app: QApplication, fonts: dict = None):
    """应用浅色主题"""
    app.setStyleSheet(LIGHT_QSS)
