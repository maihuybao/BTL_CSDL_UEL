# Kiểm tra logic đồng bộ tồn kho + hóa đơn theo trạng thái đơn hàng.
# Chạy: python test_order_sync.py
import sqlite3

from Main_Controller import apply_order_status_effects, recalc_order_total


def make_db():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE SAN_PHAM (MaSP TEXT PRIMARY KEY, TenSP TEXT, GiaBan REAL, SoLuongTon INT);
        CREATE TABLE VOUCHER (MaVoucher TEXT PRIMARY KEY, TenVoucher TEXT, GiaTriGiam REAL);
        CREATE TABLE DON_HANG (MaDonHang TEXT PRIMARY KEY, MaVoucher TEXT, TongTien REAL, TrangThaiDH TEXT);
        CREATE TABLE CHI_TIET_DON_HANG (MaDonHang TEXT, MaSP TEXT, SoLuong INT, DonGia REAL, ThanhTien REAL);
        CREATE TABLE HOA_DON (MaHoaDon TEXT PRIMARY KEY, MaDonHang TEXT, TongTien REAL, TrangThaiHD TEXT);

        INSERT INTO SAN_PHAM VALUES ('SP01', 'Áo', 100000, 10), ('SP02', 'Quần', 200000, 5);
        INSERT INTO VOUCHER VALUES ('V01', 'Giảm 50k', 50000);
        INSERT INTO DON_HANG VALUES ('DH01', 'V01', 0, 'Chờ xác nhận');
        INSERT INTO CHI_TIET_DON_HANG VALUES ('DH01', 'SP01', 2, 100000, 200000), ('DH01', 'SP02', 1, 200000, 200000);
        INSERT INTO HOA_DON VALUES ('HD01', 'DH01', 0, 'Chưa thanh toán');
    """)
    return conn, cur


def ton(cur, sp):
    return cur.execute("SELECT SoLuongTon FROM SAN_PHAM WHERE MaSP=?", (sp,)).fetchone()[0]


def hd_status(cur):
    return cur.execute("SELECT TrangThaiHD FROM HOA_DON WHERE MaDonHang='DH01'").fetchone()[0]


conn, cur = make_db()

# 1. Giao hàng: trừ kho + hóa đơn "Đã thanh toán"
apply_order_status_effects(cur, "DH01", "Chờ xác nhận", "Đã giao")
assert ton(cur, "SP01") == 8, f"SP01 phải còn 8, được {ton(cur, 'SP01')}"
assert ton(cur, "SP02") == 4, f"SP02 phải còn 4, được {ton(cur, 'SP02')}"
assert hd_status(cur) == "Đã thanh toán"

# 2. Lưu lại cùng trạng thái: không trừ kho lần hai
apply_order_status_effects(cur, "DH01", "Đã giao", "Đã giao")
assert ton(cur, "SP01") == 8, "không được trừ kho lặp"

# 3. Hủy đơn đã giao: hoàn kho + hóa đơn "Hoàn tiền"
apply_order_status_effects(cur, "DH01", "Đã giao", "Đã hủy")
assert ton(cur, "SP01") == 10 and ton(cur, "SP02") == 5, "hủy phải hoàn kho"
assert hd_status(cur) == "Hoàn tiền"

# 4. Hủy đơn chưa giao: không cộng kho khống
apply_order_status_effects(cur, "DH01", "Chờ xác nhận", "Đã hủy")
assert ton(cur, "SP01") == 10, "hủy đơn chưa giao không được cộng kho"
assert hd_status(cur) == "Hoàn tiền"

# 5. Tổng tiền = SUM(ThanhTien) - voucher, đồng bộ sang hóa đơn
recalc_order_total(cur, "DH01")
tong = cur.execute("SELECT TongTien FROM DON_HANG WHERE MaDonHang='DH01'").fetchone()[0]
assert tong == 350000, f"400000 - 50000 = 350000, được {tong}"
assert cur.execute("SELECT TongTien FROM HOA_DON WHERE MaDonHang='DH01'").fetchone()[0] == 350000

# 6. Voucher lớn hơn giá trị đơn: tổng không âm
cur.execute("UPDATE VOUCHER SET GiaTriGiam = 999999999 WHERE MaVoucher='V01'")
recalc_order_total(cur, "DH01")
assert cur.execute("SELECT TongTien FROM DON_HANG WHERE MaDonHang='DH01'").fetchone()[0] == 0

conn.close()
print("OK: toàn bộ kiểm tra logic tồn kho + thanh toán đều đạt.")
