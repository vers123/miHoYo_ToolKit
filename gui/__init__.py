"""GUI 模块入口"""

import os
import sys

from gui.main_window import MainWindow
from gui.theme import load_game_fonts, apply_light_theme


def launch_gui():
    """启动 GUI 应用"""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    app.setApplicationName("米游社工具箱")
    app.setOrganizationName("miHoYo ToolKit")

    fonts = load_game_fonts()
    apply_light_theme(app, fonts)

    window = MainWindow()
    window.fonts = fonts
    window.show()

    sys.exit(app.exec())


__all__ = ["launch_gui", "MainWindow"]
