# CLAUDE.md This file provides guidance Claude Code (claude.ai/code) when working with code in this repository.

## Tổng quan

Ứng dụng desktop PyQt6 quản lý bán hàng livestream (bài tập lớn môn Cơ sở dữ liệu — UEL). Không có hệ thống build, không có test suite, không phải git repo. Toàn bộ comment và UI text bằng tiếng Việt.

## Lệnh thường dùng

```bash
pip install PyQt6 openpyxl qtawesome "PyQt6-Charts==<bản khớp PyQt6>"   # deps (pyodbc chỉ cần cho Manager.py — legacy)
# Lưu ý: PyQt6-Charts phải cùng minor version với PyQt6 (vd PyQt6 6.10.0 → PyQt6-Charts 6.10.0), lệch version sẽ lỗi dlopen

python setup_database.py            # tạo lại data_db.sqlite từ Bang.sql — XÓA database cũ, mất dữ liệu đã nhập
python Main_Controller.py           # chạy ứng dụng tích hợp đầy đủ (entry point chính)
python Login/Login_App.py           # entry point thay thế (Login → Dashboard/Dashboard_Ex)

python Product/Product_Ex.py        # chạy riêng 1 widget để test (mỗi *_Ex.py đều có __main__)

pyuic6 Product/Product.ui -o Product/Product.py   # biên dịch lại UI sau khi sửa .ui trong Qt Designer
```

Đăng nhập: tra bảng `NGUOI_BAN` (`MaNguoiBan` / `MatKhau`). Khi lỗi DB, `Main_Controller.py` có bypass với username `admin` hoặc `NB01`.

## Kiến trúc

**Hai biến thể ứng dụng song song — đừng nhầm lẫn:**

1. **`Main_Controller.py` (~2300 dòng, monolith) — ứng dụng thật.** Chứa `LoginEx` → `DashboardEx` (QMainWindow với `QStackedWidget`, mỗi trang con là một `Ui_*Widget` được nhúng vào), truy vấn SQLite trực tiếp qua `DB_PATH = data_db.sqlite`. Lõi CRUD là `DbFormController` (dòng ~94): binding tổng quát bảng ↔ form theo `col_mappings` (danh sách tuple `(db_col, widget, widget_type)`), tự nối các nút `btnThem/btnSua/btnXoa/btnLuu/btnHuy/btnRefresh/btnSearch/btnXuatExcel` nếu tồn tại trên UI. Thêm màn hình CRUD mới = tạo thêm một instance `DbFormController`, không viết lại logic.

2. **Các file `*_Ex.py` trong từng thư mục** — phiên bản standalone của từng widget, phần lớn dùng dữ liệu giả lập (list Python hard-code), dùng để demo/test riêng lẻ. Logic ở đây KHÔNG đồng bộ với `Main_Controller.py`; sửa nghiệp vụ trong app tích hợp thì sửa `Main_Controller.py`.

**Quy ước mỗi thư mục feature** (Comment, Customer, Dashboard, Livestream, LivestreamDetail, Login, Order, OrderDetail, Payment, Product, Seller, Statistics, Voucher):
- `X.ui` — Qt Designer source
- `X.py` — sinh bởi `pyuic6`, KHÔNG sửa tay (sẽ bị ghi đè)
- `X_Ex.py` — logic, chạy được độc lập

**Database:** `Bang.sql` là schema T-SQL (SQL Server) với 10 bảng: `NGUOI_BAN`, `KHACH_HANG`, `SAN_PHAM`, `VOUCHER`, `LIVESTREAM`, `LIVESTREAM_SAN_PHAM`, `BINH_LUAN`, `DON_HANG`, `CHI_TIET_DON_HANG`, `HOA_DON`. `setup_database.py` chuyển đổi cú pháp T-SQL → SQLite (nvarchar→TEXT, bỏ `N'...'`) rồi nạp vào `data_db.sqlite`. Các file `.db` khác ở root (`data.db`, `csdl_cua_toi*.db`) là rác cũ. `Manager.py` là helper kết nối SQL Server qua pyodbc — di sản, app hiện tại không dùng.

**Import path:** mọi file đều tự chèn thư mục cha vào `sys.path` ở đầu file (để import chéo `Login.Login`, `Dashboard.Dashboard`... hoạt động khi chạy từ bất kỳ đâu). Giữ nguyên pattern này khi tạo file mới trong thư mục con.

## Quy tắc UI

- **Không dùng emoji trong UI/code** (nhãn nút, tiêu đề, thông báo, print). Thay bằng icon từ thư viện `qtawesome` (Font Awesome cho Qt): `qta.icon('fa5s.plus')`, `fa5s.edit`, `fa5s.trash`, `fa5s.search`, `fa5s.save`, `fa5s.sync`, `fa5s.file-excel`... Emoji còn sót trong file `.ui`/`*.py` sinh tự động sẽ được `apply_fontawesome_icons()` trong `Main_Controller.py` thay thế lúc runtime — nút mới thêm phải đăng ký vào đó.

## Lưu ý đã biết

- `Dashboard/Dashboard_Ex.py` và `Login/Login_Ex.py` mở SQLite bằng đường dẫn trỏ tới `Bang.sql` thay vì `data_db.sqlite` — bug có sẵn, login ở hai file này chỉ chạy nhờ nhánh except/bypass.
- Xuất Excel dùng `openpyxl`, import tại chỗ trong từng hàm export kèm QMessageBox báo cài đặt nếu thiếu.
