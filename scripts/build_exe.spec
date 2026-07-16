# PyInstaller spec — đóng gói LiveSell UEL thành 1 file exe (onefile).
# Ảnh (assets/) và database/ KHÔNG nhúng vào exe: để cạnh exe, đọc/ghi ngoài được.
# Build:  pyinstaller scripts/build_exe.spec        (chạy ở gốc dự án)
# Kết quả: dist/LiveSell.exe  -> copy exe + kèm 2 thư mục assets/, database/ khi mang đi.

import os

# SPECPATH do PyInstaller cấp = thư mục chứa file .spec (scripts/).
# Gốc dự án = cha của scripts/. Dùng đường dẫn tuyệt đối cho mọi thứ vì
# PyInstaller resolve script tương đối với thư mục spec, không phải cwd.
PROJECT_ROOT = os.path.dirname(os.path.abspath(SPECPATH))
UI_DIR = os.path.join(PROJECT_ROOT, "ui")
MAIN_SCRIPT = os.path.join(PROJECT_ROOT, "main.py")

# 13 package UI import động qua tên (Comment.Comment, Order.Order, ...) -> khai báo hiddenimports
UI_PACKAGES = [
    "Login", "Dashboard", "Comment", "Customer", "Livestream", "LivestreamDetail",
    "Order", "OrderDetail", "Payment", "Product", "Seller", "Statistics", "Voucher",
]
hidden = []
for pkg in UI_PACKAGES:
    hidden.append(f"{pkg}.{pkg}")           # module .py sinh bởi pyuic6
hidden += ["openpyxl", "PyQt6.QtCharts"]     # deps import trong try/except

a = Analysis(
    [MAIN_SCRIPT],
    pathex=[PROJECT_ROOT, UI_DIR],           # để PyInstaller tìm được app/ và ui/<Pkg>/
    binaries=[],
    datas=[],                                # KHÔNG nhúng assets/ database/ -> để ngoài cạnh exe
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=["pyodbc"],                     # legacy, không dùng
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="LiveSell",
    debug=False,
    strip=False,
    upx=True,
    console=False,                           # app GUI, không mở cửa sổ console
)
