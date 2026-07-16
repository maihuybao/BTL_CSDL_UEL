"""Entry point: dựng QApplication, ép giao diện nền sáng, mở màn đăng nhập."""
import sys

from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication

from app.login import LoginEx


def force_light_theme(app):
    """UI thiết kế nền sáng nhưng macOS dark mode đổi chữ mặc định thành trắng — ép theme sáng."""
    app.setStyle("Fusion")
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#f8fafc"))
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor("#000000"))
    palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor("#ffffff"))
    palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor("#f1f5f9"))
    palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("#000000"))
    palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#e2e8f0"))
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor("#000000"))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor("#ffffff"))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor("#000000"))
    palette.setColor(QtGui.QPalette.ColorRole.PlaceholderText, QtGui.QColor("#94a3b8"))
    palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor("#7c3aed"))
    palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor("#ffffff"))
    app.setPalette(palette)


def main():
    app = QApplication(sys.argv)
    force_light_theme(app)
    login_window = LoginEx()
    login_window.show()
    sys.exit(app.exec())
