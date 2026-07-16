# Đóng gói exe (Windows)

App đọc/ghi **ảnh** (`assets/`) và **database** (`database/data_db.sqlite`) từ thư mục **cạnh exe**, không nhúng trong exe — nên đổi ảnh/dữ liệu sau khi build không cần build lại.

## Build

Chạy ở **thư mục gốc dự án** (nơi có `main.py`):

```bash
pip install pyinstaller PyQt6 openpyxl "PyQt6-Charts==<bản khớp PyQt6>"
pyinstaller scripts/build_exe.spec
```

Kết quả: `dist/LiveSell.exe`

## Mang sang máy khác

Copy **exe + 2 thư mục** đặt cạnh nhau:

```
LiveSell/
├── LiveSell.exe
├── assets/               # ảnh sản phẩm (.png)
└── database/
    └── data_db.sqlite    # DB (tạo bằng: python scripts/setup_database.py)
```

> Thiếu `database/data_db.sqlite` → app báo không đăng nhập được. Thiếu `assets/` → sản phẩm không hiện ảnh (app vẫn chạy).

## Cách hoạt động

`app/config.py` phát hiện chế độ đóng gói qua `sys.frozen`:
- **Chạy exe:** `PROJECT_ROOT = thư mục chứa exe` (`sys.executable`) → `assets/`, `database/` cạnh exe.
- **Chạy dev (`python main.py`):** `PROJECT_ROOT = gốc dự án`.
