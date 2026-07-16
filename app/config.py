"""Cấu hình chung: đường dẫn gốc dự án, DB, dependency tùy chọn, icon map.

Mọi module khác import hằng từ đây thay vì tự dò __file__ — vì sau khi tách
vào app/, __file__ của từng module không còn trỏ về gốc dự án nữa.
"""
import os
import sys
import re as _re

# Gốc dự án = thư mục cha của app/ (app/config.py -> app/ -> gốc)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Bảo đảm import được các package UI (đã gom vào ui/) và mã ở gốc dự án
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
UI_DIR = os.path.join(PROJECT_ROOT, "ui")
if UI_DIR not in sys.path:
    sys.path.insert(0, UI_DIR)

# Ảnh sản phẩm gom ở assets/, database SQLite ở database/
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")

# Tương thích tên cũ trong logic: nơi đặt ảnh (trước đây current_dir = gốc dự án)
current_dir = ASSETS_DIR
parent_dir = PROJECT_ROOT

DB_PATH = os.path.join(DATABASE_DIR, "data_db.sqlite")

# QtCharts là tùy chọn: thiếu thì app vẫn chạy, chỉ không vẽ biểu đồ
try:
    from PyQt6.QtCharts import (QChart, QChartView, QBarSeries, QBarSet,
                                QBarCategoryAxis, QValueAxis, QPieSeries)
    HAS_QTCHARTS = True
except ImportError:
    HAS_QTCHARTS = False

# qtawesome (Font Awesome): thay toàn bộ emoji trên UI bằng icon chuẩn
try:
    import qtawesome as qta
    HAS_QTA = True
except ImportError:
    HAS_QTA = False

# Bộ icon Font Awesome cho các nút chức năng (khóa = tên objectName của nút)
_BUTTON_ICONS = {
    "btnThem": ("fa5s.plus", "Thêm mới"),
    "btnSua": ("fa5s.edit", "Sửa"),
    "btnXoa": ("fa5s.trash-alt", "Xóa bỏ"),
    "btnLuu": ("fa5s.save", "Lưu lại"),
    "btnHuy": ("fa5s.times", "Hủy bỏ"),
    "btnRefresh": ("fa5s.sync", "Làm mới"),
    "btnSearch": ("fa5s.search", "Tìm kiếm"),
    "btnXuatExcel": ("fa5s.file-excel", "Xuất Excel"),
    "btnFilter": ("fa5s.filter", "Lọc dữ liệu"),
    "btnLogin": ("fa5s.sign-in-alt", None),
    "btnExit": ("fa5s.sign-out-alt", None),
    "btnMenuDashboard": ("fa5s.home", None),
    "btnMenuSeller": ("fa5s.user-tie", None),
    "btnMenuProduct": ("fa5s.box-open", None),
    "btnMenuCustomer": ("fa5s.users", None),
    "btnMenuLivestream": ("fa5s.video", None),
    "btnMenuLivestreamDetail": ("fa5s.list-alt", None),
    "btnMenuComment": ("fa5s.comments", None),
    "btnMenuOrder": ("fa5s.shopping-cart", None),
    "btnMenuOrderDetail": ("fa5s.clipboard-list", None),
    "btnMenuPayment": ("fa5s.credit-card", None),
    "btnMenuVoucher": ("fa5s.ticket-alt", None),
    "btnMenuStatistics": ("fa5s.chart-bar", None),
    "btnMenuLogout": ("fa5s.sign-out-alt", None),
}

_EMOJI_RE = _re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF⬀-⯿←-⇿️⃣]+"
)
