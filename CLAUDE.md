# CLAUDE.md This file provides guidance Claude Code (claude.ai/code) when working with code in this repository.

## Tổng quan

Ứng dụng desktop PyQt6 quản lý bán hàng livestream (bài tập lớn môn Cơ sở dữ liệu — UEL). Không có hệ thống build, không có test suite, không phải git repo. Toàn bộ comment và UI text bằng tiếng Việt.

## Lệnh thường dùng

```bash
pip install PyQt6 openpyxl qtawesome "PyQt6-Charts==<bản khớp PyQt6>"   # deps (pyodbc chỉ cần cho Manager.py — legacy)
# Lưu ý: PyQt6-Charts phải cùng minor version với PyQt6 (vd PyQt6 6.10.0 → PyQt6-Charts 6.10.0), lệch version sẽ lỗi dlopen

python scripts/setup_database.py    # tạo lại database/data_db.sqlite từ Bang.sql — XÓA database cũ, mất dữ liệu đã nhập
python scripts/test_order_sync.py   # test logic tồn kho + thanh toán (assert, không cần framework)
python Main_Controller.py           # chạy ứng dụng tích hợp đầy đủ (entry point chính)
python ui/Login/Login_App.py        # entry point thay thế (Login → Dashboard/Dashboard_Ex)

python ui/Product/Product_Ex.py     # chạy riêng 1 widget để test (mỗi *_Ex.py đều có __main__)

pyuic6 ui/Product/Product.ui -o ui/Product/Product.py   # biên dịch lại UI sau khi sửa .ui trong Qt Designer
```

Đăng nhập: tra bảng `NGUOI_BAN` (`MaNguoiBan` / `MatKhau`). Khi lỗi DB, `Main_Controller.py` có bypass với username `admin` hoặc `NB01`.

## Kiến trúc

**Hai biến thể ứng dụng song song — đừng nhầm lẫn:**

1. **Package `app/` — ứng dụng thật.** `Main_Controller.py` giờ là **shim mỏng** (~25 dòng): set `sys.path`, re-export `main`/`DashboardEx`/`LoginEx`/`apply_order_status_effects`/`recalc_order_total` rồi gọi `main()`. Logic thật tách theo domain:
   - `app/config.py` — `PROJECT_ROOT`, `DB_PATH`, cờ `HAS_QTA`/`HAS_QTCHARTS` (+ `qta`, các lớp QtCharts), map `_BUTTON_ICONS`, `_EMOJI_RE`. Mọi module import hằng từ đây (không tự dò `__file__`).
   - `app/helpers.py` — `strip_emoji`, `apply_fontawesome_icons`, `get_widget_value`/`set_widget_value`.
   - `app/db_logic.py` — `ensure_schema`, `apply_order_status_effects`, `recalc_order_total` (thuần, nhận sẵn cursor → test được không cần GUI).
   - `app/db_form_controller.py` — `DbFormController`: binding tổng quát bảng ↔ form theo `col_mappings` (tuple `(db_col, widget, widget_type)`), tự nối `btnThem/btnSua/btnXoa/btnLuu/btnHuy/btnRefresh/btnSearch/btnXuatExcel`. Nút Sửa toggle thành Lưu (mọi tab). Thêm màn CRUD mới = tạo thêm một instance, không viết lại logic.
   - `app/dashboard/` — `DashboardEx` (QMainWindow + `QStackedWidget`) ghép từ 5 **mixin**: `base` (khởi tạo, nạp/đổ bảng, refresh, combobox), `statistics`, `charts` (QtCharts), `product`, `seller`. `__init__.py` lắp ráp: `class DashboardEx(BaseMixin, StatisticsMixin, ChartsMixin, ProductMixin, SellerMixin, QMainWindow)`.
   - `app/login.py` — `LoginEx`; `app/app_main.py` — `force_light_theme`, `main`.

2. **Các file `*_Ex.py` trong từng thư mục** — phiên bản standalone của từng widget, phần lớn dùng dữ liệu giả lập (list Python hard-code), dùng để demo/test riêng lẻ. Logic ở đây KHÔNG đồng bộ với app tích hợp; sửa nghiệp vụ thì sửa trong `app/`.

**Quy ước mỗi thư mục feature** (Comment, Customer, Dashboard, Livestream, LivestreamDetail, Login, Order, OrderDetail, Payment, Product, Seller, Statistics, Voucher):
- `X.ui` — Qt Designer source
- `X.py` — sinh bởi `pyuic6`, KHÔNG sửa tay (sẽ bị ghi đè)
- `X_Ex.py` — logic, chạy được độc lập

**Database:** `Bang.sql` là schema T-SQL (SQL Server) với 10 bảng: `NGUOI_BAN`, `KHACH_HANG`, `SAN_PHAM`, `VOUCHER`, `LIVESTREAM`, `LIVESTREAM_SAN_PHAM`, `BINH_LUAN`, `DON_HANG`, `CHI_TIET_DON_HANG`, `HOA_DON`. `scripts/setup_database.py` chuyển đổi cú pháp T-SQL → SQLite (nvarchar→TEXT, bỏ `N'...'`) rồi nạp vào `database/data_db.sqlite` (đường dẫn cấu hình ở `app/config.py` — `DATABASE_DIR`/`DB_PATH`). Ảnh sản phẩm gom ở `assets/` (`app/config.py` — `ASSETS_DIR`); `SAN_PHAM.HinhAnh` chỉ lưu tên file, code tìm trong `assets/` trước rồi mới tới gốc dự án. Các script phụ trợ (khởi tạo DB, test) nằm trong `scripts/`. `scripts/Manager.py` là helper kết nối SQL Server qua pyodbc — di sản, app hiện tại không dùng.

**Import path:** mọi file đều tự chèn thư mục cha vào `sys.path` ở đầu file (để import chéo `Login.Login`, `Dashboard.Dashboard`... hoạt động khi chạy từ bất kỳ đâu). Giữ nguyên pattern này khi tạo file mới trong thư mục con.

## Quy tắc UI

- **Không dùng emoji trong UI/code** (nhãn nút, tiêu đề, thông báo, print). Thay bằng icon từ thư viện `qtawesome` (Font Awesome cho Qt): `qta.icon('fa5s.plus')`, `fa5s.edit`, `fa5s.trash`, `fa5s.search`, `fa5s.save`, `fa5s.sync`, `fa5s.file-excel`... Emoji còn sót trong file `.ui`/`*.py` sinh tự động sẽ được `apply_fontawesome_icons()` trong `Main_Controller.py` thay thế lúc runtime — nút mới thêm phải đăng ký vào đó.

## Lưu ý đã biết

- `ui/Dashboard/Dashboard_Ex.py` và `ui/Login/Login_Ex.py` mở SQLite bằng đường dẫn trỏ tới `Bang.sql` thay vì `data_db.sqlite` — bug có sẵn, login ở hai file này chỉ chạy nhờ nhánh except/bypass.
- 13 thư mục UI (`Login/`, `Order/`, …) đã gom vào `ui/`. `app/config.py` thêm `ui/` vào `sys.path` nên mọi import `from Order.Order import ...` vẫn giữ nguyên, không cần sửa.
- Xuất Excel dùng `openpyxl`, import tại chỗ trong từng hàm export kèm QMessageBox báo cài đặt nếu thiếu.
