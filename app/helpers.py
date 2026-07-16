"""Tiện ích UI thuần: bỏ emoji, gắn icon Font Awesome, đọc/ghi giá trị widget."""
from PyQt6 import QtWidgets, QtCore

from app.config import HAS_QTA, _BUTTON_ICONS, _EMOJI_RE
if HAS_QTA:
    from app.config import qta


def strip_emoji(text):
    """Bỏ emoji khỏi chuỗi hiển thị (giữ nguyên chữ)."""
    return _EMOJI_RE.sub("", text or "").strip()


def apply_fontawesome_icons(root_widget):
    """Quét mọi widget con: bỏ emoji trong text, gắn icon Font Awesome cho nút đã đăng ký."""
    for w in root_widget.findChildren(QtWidgets.QWidget):
        name = w.objectName()
        if isinstance(w, QtWidgets.QAbstractButton):
            if HAS_QTA and name in _BUTTON_ICONS:
                icon_name, label = _BUTTON_ICONS[name]
                # Nút menu sidebar nằm trên nền tím đậm -> icon trắng; còn lại theo màu chữ nút
                icon_color = "#ffffff" if name.startswith("btnMenu") else w.palette().buttonText().color().name()
                try:
                    w.setIcon(qta.icon(icon_name, color=icon_color))
                except Exception:
                    w.setIcon(qta.icon(icon_name))
                w.setText(label if label is not None else strip_emoji(w.text()))
            else:
                w.setText(strip_emoji(w.text()))
        elif isinstance(w, QtWidgets.QLabel):
            if _EMOJI_RE.search(w.text() or ""):
                w.setText(strip_emoji(w.text()))
        elif isinstance(w, QtWidgets.QLineEdit):
            if _EMOJI_RE.search(w.placeholderText() or ""):
                w.setPlaceholderText(strip_emoji(w.placeholderText()))
    # Bỏ emoji trong tiêu đề cột của các bảng
    for tbl in root_widget.findChildren(QtWidgets.QTableWidget):
        for c in range(tbl.columnCount()):
            item = tbl.horizontalHeaderItem(c)
            if item and _EMOJI_RE.search(item.text() or ""):
                item.setText(strip_emoji(item.text()))


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
