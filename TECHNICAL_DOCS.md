# Tài liệu kỹ thuật — LiveSell UEL

Tài liệu chi tiết về kiến trúc, cơ chế đồng bộ dữ liệu, thuật toán nghiệp vụ và cấu trúc mã nguồn của ứng dụng quản lý bán hàng livestream.

---

## 1. Tổng quan kiến trúc

Ứng dụng desktop PyQt6 một cửa sổ (`QMainWindow` + `QStackedWidget`), mỗi màn hình là một trang con nhúng vào stack. Toàn bộ logic tách khỏi file giao diện Qt Designer, tổ chức thành package `app/` theo **domain**.

```
main.py (shim)
   │  re-export: main, DashboardEx, LoginEx, apply_order_status_effects, recalc_order_total
   ▼
app/app_main.py ── main() ──▶ QApplication + force_light_theme()
   │
   ▼
app/login.py ── LoginEx ── tra NGUOI_BAN ──▶ DashboardEx
   │
   ▼
app/dashboard/  ── DashboardEx = BaseMixin + StatisticsMixin + ChartsMixin + ProductMixin + SellerMixin + QMainWindow
   │
   ├── app/db_form_controller.py ── DbFormController (CRUD chung)
   ├── app/db_logic.py            ── nghiệp vụ thuần trên cursor (test được)
   ├── app/helpers.py             ── tiện ích UI (icon, emoji, đọc/ghi widget)
   └── app/config.py              ── hằng số + dependency tùy chọn
```

**Nguyên tắc thiết kế:**

- **Shim mỏng:** `main.py` chỉ set `sys.path`, re-export và gọi `main()`. Giữ tương thích ngược cho các import cũ.
- **Tách theo domain, ghép bằng mixin:** `DashboardEx` là god-class được chia thành 5 mixin. `__init__` nằm ở `BaseMixin`, gọi `super().__init__()` để đi tới `QMainWindow` qua MRO. Cắt-dán nguyên method, `self.*` không đổi → hành vi bất biến.
- **Cấu hình tập trung:** mọi đường dẫn (`DB_PATH`, `ASSETS_DIR`) và cờ dependency (`HAS_QTA`, `HAS_QTCHARTS`) khai báo một chỗ ở `config.py`; module khác import thay vì tự dò `__file__`.
- **Suy biến mềm:** thiếu `PyQt6-Charts` → app vẫn chạy, chỉ hiện placeholder thay biểu đồ; thiếu `qtawesome` → dùng text thường.

---

## 2. `DbFormController` — lớp CRUD tổng quát

Trái tim tái sử dụng của ứng dụng. Một instance nối **một bảng DB** với **một form** thông qua `col_mappings`, tự động hóa toàn bộ Thêm/Sửa/Xóa/Lưu/Hủy/Làm mới/Tìm kiếm/Xuất Excel.

### 2.1. Khai báo

```python
DbFormController(
    main_controller,   # DashboardEx — để gọi refresh_dependents() sau khi ghi
    ui_page,           # trang UI chứa các widget
    table_widget,      # QTableWidget hiển thị dữ liệu
    db_table,          # tên bảng SQLite
    pk_col,            # cột khóa chính
    col_mappings,      # list[(db_col, widget, widget_type)]
    refresh_callback,  # hàm đổ lại bảng sau khi ghi
)
```

`widget_type` quyết định cách đọc/ghi giá trị (`app/helpers.py`):

| `widget_type` | Widget           | Đọc (`get_widget_value`)          | Ghi (`set_widget_value`)         |
| ------------- | ---------------- | --------------------------------- | -------------------------------- |
| `text`        | `QLineEdit`      | `.text().strip()`                 | `.setText()`                     |
| `spin`        | `QSpinBox`       | `.value()`                        | `.setValue()`                    |
| `combo_text`  | `QComboBox`      | text (tách `"Mã - Tên"` lấy mã)   | so khớp item theo mã hoặc prefix |
| `combo_index` | `QComboBox`      | `.currentIndex()`                 | `.setCurrentIndex()`             |
| `date`        | `QDateEdit`      | `yyyy-MM-dd`                      | parse `yyyy-MM-dd`               |
| `datetime`    | `QDateTimeEdit`  | `yyyy-MM-dd HH:mm:ss`            | parse (fallback không giây)      |

Thêm màn hình CRUD mới = tạo thêm một instance, **không viết lại logic**.

### 2.2. Cơ chế Sửa/Lưu hợp nhất (mọi tab)

Khác với CRUD truyền thống dùng 2 nút riêng, ứng dụng gộp **một nút toggle**:

```
[chọn dòng]  ──▶  form đổ dữ liệu, ô nhập KHÓA, nút = "Sửa"
     │
[bấm Sửa]    ──▶  ô nhập MỞ, nút = "Lưu", current_action = "SUA"
     │
[bấm Lưu]    ──▶  ghi DB, form khóa lại, nút = "Sửa", refresh_dependents()
```

- Nút `btnLuu` riêng bị ẩn — mọi submit đi qua nút Sửa/Lưu đã toggle.
- Trạng thái điều khiển bởi `current_action ∈ {None, "THEM", "SUA"}`.
- Áp dụng cho cả 8 tab dùng `DbFormController` lẫn 2 tab custom (Product/Seller) qua `_on_product_edit_button` / `_on_seller_edit_button`.
- Bảng đặt `SelectRows` + `SingleSelection` + `NoEditTriggers` → click dòng luôn tạo selection ổn định để đổ form.

---

## 3. Đồng bộ dữ liệu chéo màn hình

Yêu cầu cốt lõi: thao tác ở một màn hình phải tự phản ánh sang các màn hình liên quan mà không cần khởi động lại.

### 3.1. Hook đồng bộ toàn cục

Sau **mỗi** lần ghi (`action_luu`, `action_xoa`), controller gọi:

```python
DashboardEx.refresh_dependents():
    load_all_data_from_database()   # đổ lại TẤT CẢ bảng mọi tab + thẻ số liệu
    populate_all_comboboxes()       # nạp lại combobox (voucher, sản phẩm, khách...)
    load_statistics_data()          # nạp lại báo cáo thống kê toàn thời gian
    update_all_charts()             # vẽ lại biểu đồ Dashboard + Thống kê
```

Một hook duy nhất phủ mọi luồng đồng bộ dưới đây.

### 3.2. Các luồng đồng bộ cụ thể

| Nguồn → Đích              | Cơ chế                                                                                              |
| ------------------------- | --------------------------------------------------------------------------------------------------- |
| Livestream → Chi tiết     | Chung nguồn `LIVESTREAM_SAN_PHAM`; chọn phiên live đổ danh sách sản phẩm của phiên                   |
| Đơn hàng → Chi tiết đơn   | `refresh_order_detail_table` JOIN `DON_HANG`/`VOUCHER`, thêm cột "Voucher"                           |
| Đơn hàng → Tồn kho        | `apply_order_status_effects` (xem §4.1) trừ/cộng `SAN_PHAM.SoLuongTon` theo trạng thái               |
| Đơn hàng → Thanh toán     | Cùng hàm trên: "Đã giao" → `HOA_DON = 'Đã thanh toán'`, "Đã hủy" → `'Hoàn tiền'`                     |
| Voucher → Tổng tiền đơn   | `recalc_order_total` (xem §4.2) trừ thẳng `GiaTriGiam` vào tổng đơn                                  |
| Mọi thay đổi → Thống kê   | `refresh_dependents` gọi lại `load_statistics_data` + `update_all_charts`                            |

---

## 4. Thuật toán nghiệp vụ

Ba hàm trong `app/db_logic.py` là logic thuần: nhận sẵn `cursor` (không tự mở kết nối) nên **test được không cần GUI** — xem `scripts/test_order_sync.py`.

### 4.1. Đồng bộ tồn kho theo trạng thái đơn — `apply_order_status_effects(cursor, ma_dh, old_status, new_status)`

```
if old_status == new_status:            # lưu lại cùng trạng thái → không làm gì (chống trừ kho lặp)
    return

new_status == "Đã giao" và old != "Đã giao":
    SAN_PHAM.SoLuongTon −= SoLuong (từng dòng CHI_TIET_DON_HANG)
    HOA_DON.TrangThaiHD = "Đã thanh toán"

new_status == "Đã hủy":
    nếu old == "Đã giao":               # chỉ hoàn kho nếu trước đó ĐÃ trừ
        SAN_PHAM.SoLuongTon += SoLuong
    HOA_DON.TrangThaiHD = "Hoàn tiền"
```

**Bất biến quan trọng:** chỉ trừ kho một lần khi chuyển *sang* "Đã giao", và chỉ hoàn kho nếu hủy đơn *đã từng* giao → không bao giờ trừ/cộng khống.

### 4.2. Tính tổng tiền đơn — `recalc_order_total(cursor, ma_dh)`

```
DON_HANG.TongTien = MAX(0, SUM(CHI_TIET_DON_HANG.ThanhTien) − VOUCHER.GiaTriGiam)
HOA_DON.TongTien  = DON_HANG.TongTien        # đồng bộ sang hóa đơn
```

Giảm giá phẳng theo `GiaTriGiam`; kẹp sàn 0 để voucher lớn hơn giá trị đơn không làm tổng âm.

### 4.3. Migration nhẹ — `ensure_schema()`

Chạy lúc khởi động: `PRAGMA table_info(VOUCHER)`, nếu thiếu thì `ALTER TABLE VOUCHER ADD COLUMN LoaiUuDai TEXT` / `GiamToiDa REAL`. Idempotent — chạy nhiều lần vô hại, sống sót sau khi chạy lại `setup_database.py`.

---

## 5. Biểu đồ (QtCharts)

`app/dashboard/charts.py` — bọc trong `try/import`, thiếu thư viện thì hiện placeholder.

| Vị trí     | Biểu đồ                                                    | Nguồn dữ liệu                                        |
| ---------- | --------------------------------------------------------- | ---------------------------------------------------- |
| Dashboard  | Cột — doanh thu theo tháng                                 | `HOA_DON` đã thanh toán, gom `strftime('%Y-%m')`     |
| Dashboard  | Tròn — số đơn theo `TrangThaiDH`                           | `DON_HANG`                                           |
| Thống kê   | Cột — doanh thu theo livestream + Tròn — tỷ trọng sản phẩm | Kết quả truy vấn thống kê (theo bộ lọc ngày)         |

Trục Y đặt `setRange(0, max*1.1 or 1)` để tránh giá trị `NaN` khi rỗng.

---

## 6. Giao diện & theme

- **`force_light_theme(app)`:** ép `Fusion` style + `QPalette` nền sáng, chữ đen `#000000` — sửa lỗi macOS dark mode làm chữ trắng biến mất trên nền sáng.
- **`apply_fontawesome_icons(root)`:** quét mọi widget, bỏ emoji trong text và gắn icon Font Awesome cho nút đã đăng ký trong `_BUTTON_ICONS`. Nút menu sidebar (nền tím) dùng icon trắng.
- **Bảng:** `populate_table` ép chữ đen từng cell (chống trùng màu nền). Bảng thống kê xen màu dòng, cột số canh phải + phân tách nghìn.

---

## 7. Kiểm thử

Không dùng framework — assert thuần, chạy trực tiếp:

```bash
python3 scripts/test_order_sync.py
```

Tạo SQLite in-memory, nạp schema + seed, gọi `apply_order_status_effects` và `recalc_order_total`, kiểm:

- Giao đơn → tồn kho giảm đúng lượng + hóa đơn "Đã thanh toán".
- Lưu lại cùng trạng thái → không trừ kho lần hai.
- Hủy đơn đã giao → hoàn kho + "Hoàn tiền"; hủy đơn chưa giao → không cộng kho khống.
- Tổng tiền = `SUM(ThanhTien) − voucher`, đồng bộ sang hóa đơn, không âm khi voucher vượt giá trị đơn.

---

## 8. Chuyển đổi schema T-SQL → SQLite

`Bang.sql` là schema T-SQL (SQL Server) gốc. `scripts/setup_database.py` chuyển đổi khi nạp:

- `nvarchar`/`varchar(max)` → `TEXT`, `float` → `REAL`, `datetime` → `TEXT`
- Bỏ tiền tố chuỗi Unicode `N'...'`
- Neo đường dẫn theo gốc dự án (`__file__` → cha của `scripts/`), ghi DB vào `database/data_db.sqlite`

---

## 9. Công nghệ

- **Ngôn ngữ:** Python 3.10+
- **GUI:** PyQt6 + Qt Designer (`.ui` biên dịch bằng `pyuic6`)
- **Biểu đồ:** PyQt6-Charts (cùng minor version với PyQt6)
- **CSDL:** SQLite 3 (module `sqlite3` chuẩn)
- **Icons:** qtawesome (Font Awesome)
- **Xuất Excel:** openpyxl
- **AI Assistant:** Claude (Anthropic) — hỗ trợ tách monolith, sửa lỗi đồng bộ, tối ưu UI qua Claude Code
