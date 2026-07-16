"""Logic nghiệp vụ thuần trên DB: migration nhẹ, đồng bộ tồn kho/hóa đơn, tính tổng đơn.

3 hàm dưới nhận sẵn cursor (không tự mở kết nối) nên test được không cần GUI —
xem test_order_sync.py.
"""
import sqlite3

from app.config import DB_PATH


def ensure_schema():
    """Bổ sung cột LoaiUuDai/GiamToiDa cho bảng VOUCHER nếu chưa có (chạy nhiều lần vô hại)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(VOUCHER)")
        cols = [row[1] for row in cursor.fetchall()]
        if "LoaiUuDai" not in cols:
            cursor.execute("ALTER TABLE VOUCHER ADD COLUMN LoaiUuDai TEXT")
        if "GiamToiDa" not in cols:
            cursor.execute("ALTER TABLE VOUCHER ADD COLUMN GiamToiDa REAL")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Lỗi ensure_schema: {e}")


def apply_order_status_effects(cursor, ma_dh, old_status, new_status):
    """Đồng bộ tồn kho + hóa đơn theo trạng thái đơn hàng.

    - Sang "Đã giao": trừ tồn kho theo chi tiết đơn, hóa đơn -> "Đã thanh toán".
    - Sang "Đã hủy": nếu trước đó đã trừ kho ("Đã giao") thì cộng trả, hóa đơn -> "Hoàn tiền".
    """
    if old_status == new_status:
        return

    if new_status == "Đã giao" and old_status != "Đã giao":
        cursor.execute("""
            UPDATE SAN_PHAM SET SoLuongTon = SoLuongTon - (
                SELECT ct.SoLuong FROM CHI_TIET_DON_HANG ct
                WHERE ct.MaDonHang = ? AND ct.MaSP = SAN_PHAM.MaSP
            )
            WHERE MaSP IN (SELECT MaSP FROM CHI_TIET_DON_HANG WHERE MaDonHang = ?)
        """, (ma_dh, ma_dh))
        cursor.execute("UPDATE HOA_DON SET TrangThaiHD = 'Đã thanh toán' WHERE MaDonHang = ?", (ma_dh,))
    elif new_status == "Đã hủy":
        if old_status == "Đã giao":
            cursor.execute("""
                UPDATE SAN_PHAM SET SoLuongTon = SoLuongTon + (
                    SELECT ct.SoLuong FROM CHI_TIET_DON_HANG ct
                    WHERE ct.MaDonHang = ? AND ct.MaSP = SAN_PHAM.MaSP
                )
                WHERE MaSP IN (SELECT MaSP FROM CHI_TIET_DON_HANG WHERE MaDonHang = ?)
            """, (ma_dh, ma_dh))
        cursor.execute("UPDATE HOA_DON SET TrangThaiHD = 'Hoàn tiền' WHERE MaDonHang = ?", (ma_dh,))


def recalc_order_total(cursor, ma_dh):
    """Tổng tiền đơn = SUM(ThanhTien) - GiaTriGiam voucher (không âm), đồng bộ sang HOA_DON."""
    # ponytail: giảm phẳng theo GiaTriGiam, bỏ qua DieuKienApDung dạng text — nâng cấp khi cần parse điều kiện
    cursor.execute("""
        UPDATE DON_HANG SET TongTien = MAX(0,
            COALESCE((SELECT SUM(ThanhTien) FROM CHI_TIET_DON_HANG WHERE MaDonHang = ?), 0)
            - COALESCE((SELECT v.GiaTriGiam FROM VOUCHER v WHERE v.MaVoucher = DON_HANG.MaVoucher), 0)
        ) WHERE MaDonHang = ?
    """, (ma_dh, ma_dh))
    cursor.execute("UPDATE HOA_DON SET TongTien = COALESCE((SELECT TongTien FROM DON_HANG WHERE MaDonHang = ?), 0) WHERE MaDonHang = ?", (ma_dh, ma_dh))
