"""Tiện ích UI thuần: đọc/ghi giá trị widget.

Emoji gốc trong file .ui được giữ nguyên (theo yêu cầu khôi phục emoji);
apply_fontawesome_icons cố ý là no-op để không strip/không gắn icon qtawesome.
"""
from PyQt6 import QtWidgets, QtCore


def strip_emoji(text):
    """No-op: giữ nguyên emoji (trước đây bỏ emoji khi dùng qtawesome)."""
    return text or ""


def apply_fontawesome_icons(root_widget):
    """No-op: giữ nguyên emoji gốc trong UI, không thay bằng icon Font Awesome."""
    return


def get_widget_value(widget, widget_type):
    if widget_type == "text":
        return widget.text().strip()
    elif widget_type == "spin":
        return widget.value()
    elif widget_type == "combo_text":
        val = widget.currentText()
        if " - " in val:
            return val.split(" - ")[0]
        if val == "Không":
            return None
        return val
    elif widget_type == "combo_index":
        return widget.currentIndex()
    elif widget_type == "date":
        return widget.date().toString("yyyy-MM-dd")
    elif widget_type == "datetime":
        return widget.dateTime().toString("yyyy-MM-dd HH:mm:ss")
    return ""


def set_widget_value(widget, widget_type, value):
    val_str = str(value if value is not None else "")
    if widget_type == "text":
        widget.setText(val_str)
    elif widget_type == "spin":
        try:
            widget.setValue(int(float(value)) if value else 0)
        except Exception:
            widget.setValue(0)
    elif widget_type == "combo_text":
        if not val_str or val_str == "None":
            widget.setCurrentText("Không")
            return
        for i in range(widget.count()):
            item_text = widget.itemText(i)
            if item_text == val_str or item_text.startswith(val_str + " - "):
                widget.setCurrentIndex(i)
                return
        widget.setCurrentText(val_str)
    elif widget_type == "combo_index":
        try:
            widget.setCurrentIndex(int(value) if value else 0)
        except Exception:
            widget.setCurrentIndex(0)
    elif widget_type == "date":
        qdate = QtCore.QDate.fromString(val_str[:10], "yyyy-MM-dd")
        if qdate.isValid():
            widget.setDate(qdate)
    elif widget_type == "datetime":
        qdatetime = QtCore.QDateTime.fromString(val_str, "yyyy-MM-dd HH:mm:ss")
        if not qdatetime.isValid():
            qdatetime = QtCore.QDateTime.fromString(val_str, "yyyy-MM-dd HH:mm")
        if qdatetime.isValid():
            widget.setDateTime(qdatetime)
