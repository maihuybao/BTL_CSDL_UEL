# LiveSell UEL

Phần mềm quản lý bán hàng qua livestream cho người bán — bài tập lớn môn Cơ sở dữ liệu, Trường Đại học Kinh tế Luật (UEL). Xây dựng bằng Python + PyQt6, lưu trữ dữ liệu SQLite.

---

## Vai trò trong dự án

[Tôi](https://github.com/maihuybao) tham gia dự án với vai trò hỗ trợ kỹ thuật cho một nhóm sinh viên UEL làm bài tập lớn cho môn CSDL. Công việc bao gồm hướng dẫn kiến trúc ứng dụng, tách monolith thành package theo domain, review code, xử lý lỗi đồng bộ dữ liệu và tối ưu giao diện trong quá trình nhóm phát triển phần mềm.


## Yêu cầu

- Python 3.10+
- PyQt6 · PyQt6-Charts (cùng minor version với PyQt6) · openpyxl · qtawesome


```bash
pip install PyQt6 openpyxl qtawesome "PyQt6-Charts==<bản khớp PyQt6>"
```

> `PyQt6-Charts` phải cùng minor version với `PyQt6` (vd `PyQt6 6.10.0` → `PyQt6-Charts 6.10.0`), lệch version sẽ lỗi `dlopen`.


---

## Chạy ứng dụng


```bash
# Lần đầu: tạo DB và nạp dữ liệu mẫu từ Bang.sql
python3 scripts/setup_database.py

# Khởi động
python3 main.py
```

Chạy lại `scripts/setup_database.py` bất cứ lúc nào để reset toàn bộ dữ liệu về mặc định (thao tác này **xóa** DB cũ, mất dữ liệu đã nhập).


---

## Tài khoản mặc định

Đăng nhập bằng bảng `NGUOI_BAN` (mã người bán / mật khẩu):

| Vai trò    | Username | Password |
| ---------- | -------- | -------- |
| Người bán  | `NB01`   | `123`    |
| Người bán  | `NB02`   | `456`    |
| Người bán  | `NB03`   | `789`    |

> Tổng cộng 9 tài khoản người bán (`NB01`–`NB09`). Khi lỗi kết nối DB, `main.py` có nhánh bypass với username `admin` hoặc `NB01`.


---

## Chức năng

Ứng dụng gồm 12 màn hình quản lý, điều hướng qua sidebar, dữ liệu **tự đồng bộ chéo** giữa các màn hình liên quan.

| Màn hình              | Chức năng                                                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Dashboard             | Thẻ thống kê tổng quan + Top sản phẩm bán chạy + Livestream đang diễn ra + biểu đồ doanh thu (cột) và trạng thái đơn (tròn) |
| Người bán (Seller)    | CRUD người bán, tìm kiếm, xuất Excel                                                                                     |
| Sản phẩm (Product)    | CRUD sản phẩm kèm ảnh, tồn kho, tìm kiếm, xuất Excel                                                                     |
| Khách hàng (Customer) | CRUD khách hàng, tìm kiếm, xuất Excel                                                                                    |
| Livestream            | CRUD phiên live, gắn sản phẩm cho từng phiên                                                                             |
| Chi tiết Livestream   | Tự đổ danh sách sản phẩm của phiên live được chọn                                                                        |
| Bình luận (Comment)   | Quản lý bình luận/chốt đơn theo phiên live                                                                               |
| Đơn hàng (Order)      | CRUD đơn, hiển thị sản phẩm đã mua; đổi trạng thái **"Đã giao"** → trừ tồn kho + hóa đơn "Đã thanh toán", **"Đã hủy"** → hoàn kho + "Hoàn tiền" |
| Chi tiết đơn hàng     | Chọn sản phẩm tự điền giá, tự tính thành tiền; hiển thị voucher đã áp dụng                                               |
| Thanh toán (Payment)  | Quản lý hóa đơn, đồng bộ trạng thái theo đơn hàng                                                                        |
| Voucher               | CRUD voucher (loại ưu đãi, giá trị giảm, điều kiện, giảm tối đa), trừ thẳng vào tổng tiền đơn                            |
| Thống kê (Statistics) | Báo cáo doanh thu toàn thời gian, lọc theo ngày, biểu đồ cột + tròn, xuất Excel                                          |

**Cơ chế Sửa/Lưu (mọi tab):** chọn dòng trên bảng → form đổ dữ liệu (ô nhập khóa) → bấm **Sửa** (nút biến thành **Lưu**) → chỉnh field → bấm **Lưu** ghi vào DB.


---

## Cấu trúc dự án


```
BTL_CSDL_UEL/
├── main.py                     # Entry point (shim): re-export + gọi main()
├── Bang.sql                    # Schema T-SQL gốc + dữ liệu mẫu
├── app/                        # Toàn bộ logic ứng dụng, tách theo domain
│   ├── config.py               # PROJECT_ROOT, DB_PATH, ASSETS_DIR, cờ HAS_QTA/HAS_QTCHARTS, icon map
│   ├── helpers.py              # strip_emoji, apply_fontawesome_icons, get/set_widget_value
│   ├── db_logic.py             # ensure_schema, đồng bộ tồn kho/hóa đơn, tính tổng đơn (thuần, test được)
│   ├── db_form_controller.py   # DbFormController — lớp CRUD chung bảng ↔ form
│   ├── login.py                # LoginEx — màn hình đăng nhập
│   ├── app_main.py             # force_light_theme + main()
│   └── dashboard/              # DashboardEx ghép từ 5 mixin theo domain
│       ├── __init__.py         # class DashboardEx(BaseMixin, StatisticsMixin, ChartsMixin, ProductMixin, SellerMixin, QMainWindow)
│       ├── base.py             # Khởi tạo, nạp/đổ bảng, refresh, combobox
│       ├── statistics.py       # Tab Thống kê
│       ├── charts.py           # Biểu đồ QtCharts
│       ├── product.py          # Tab Sản phẩm
│       └── seller.py           # Tab Người bán
├── ui/                         # 13 package giao diện Qt Designer (.ui + .py sinh bởi pyuic6 + *_Ex.py demo)
├── assets/                     # 10 file ảnh sản phẩm PNG
├── database/
│   └── data_db.sqlite          # Cơ sở dữ liệu SQLite
└── scripts/
    ├── setup_database.py       # Tạo lại DB từ Bang.sql (T-SQL → SQLite)
    ├── test_order_sync.py      # Test logic tồn kho + thanh toán (assert, không framework)
    └── Manager.py              # Helper kết nối SQL Server qua pyodbc — di sản, không dùng
```


---

## Cơ sở dữ liệu

SQLite với 10 bảng:

| Bảng                  | Các cột chính                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------ |
| `NGUOI_BAN`           | `MaNguoiBan`, `MatKhau`, `HoTen`, `SoDienThoai`, `Email`, `TenCuaHang`, `DiaChi`                        |
| `KHACH_HANG`          | `MaKhachHang`, `HoTen`, `SoDienThoai`, `Email`, `DiaChi`                                                |
| `SAN_PHAM`            | `MaSP`, `TenSP`, `MoTa`, `GiaBan`, `SoLuongTon`, `HinhAnh`                                              |
| `VOUCHER`             | `MaVoucher`, `TenVoucher`, `GiaTriGiam`, `DieuKienApDung`, `NgayBatDau`, `NgayKetThuc`, `TrangThai`, `LoaiUuDai`, `GiamToiDa` |
| `LIVESTREAM`          | `MaLive`, `MaNguoiBan`, `TenLive`, `ThoiGianBatDau`, `ThoiGianKetThuc`, `TrangThai`                     |
| `LIVESTREAM_SAN_PHAM` | `MaLive`, `MaSP` (khóa chính ghép)                                                                      |
| `BINH_LUAN`           | `MaBinhLuan`, `MaLive`, `NoiDung`, `ThoiGian`, `NguoiBinhLuan`, `LoaiBinhLuan`                          |
| `DON_HANG`            | `MaDonHang`, `MaKhachHang`, `MaBinhLuan`, `MaVoucher`, `NgayDat`, `TongTien`, `TrangThaiDH`             |
| `CHI_TIET_DON_HANG`   | `MaDonHang`, `MaSP`, `SoLuong`, `DonGia`, `ThanhTien` (khóa chính ghép)                                 |
| `HOA_DON`             | `MaHoaDon`, `MaDonHang`, `PhuongThucTT`, `TongTien`, `ThoiGianLap`, `TrangThaiHD`                       |

**Ghi chú:**

- Tổng tiền đơn được tính **động** khi thêm/sửa chi tiết: `MAX(0, SUM(ThanhTien) − GiaTriGiam voucher)`, rồi đồng bộ sang `HOA_DON`.
- Tồn kho `SAN_PHAM.SoLuongTon` chỉ trừ khi đơn chuyển sang **"Đã giao"**, hoàn lại khi hủy đơn đã giao — tránh trừ/cộng khống.
- `VOUCHER.LoaiUuDai` và `GiamToiDa` được bổ sung bằng migration nhẹ (`ensure_schema`) khi khởi động, sống sót sau khi chạy lại `setup_database.py`.
- `SAN_PHAM.HinhAnh` chỉ lưu tên file; code tìm ảnh trong `assets/` trước rồi mới tới gốc dự án.

---

## Công nghệ

- Python 3.10+ · PyQt6 · PyQt6-Charts · SQLite 3 · Qt Designer (`.ui`)
- Xuất Excel: openpyxl
- Icons: qtawesome (Font Awesome) — thay toàn bộ emoji trên UI bằng icon chuẩn
- AI Assistant: Claude (Anthropic) — hỗ trợ phát triển qua Claude Code

Chi tiết kiến trúc, database schema, thuật toán đồng bộ: xem [`TECHNICAL_DOCS.md`](TECHNICAL_DOCS.md).
