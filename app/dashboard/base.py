"""BaseMixin: khởi tạo, nạp dữ liệu, đổ bảng, nối nút CRUD chung cho DashboardEx.

Tách từ Main_Controller.py — self.* giữ nguyên, không đổi logic.
"""
import os
import sqlite3

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QMainWindow, QWidget, QTableWidgetItem, QMessageBox

from app.config import DB_PATH, PROJECT_ROOT
from app.helpers import apply_fontawesome_icons, get_widget_value, set_widget_value
from app.db_logic import ensure_schema
from app.db_form_controller import DbFormController

from Dashboard.Dashboard import Ui_MainWindow
from Comment.Comment import Ui_CommentWidget
from Customer.Customer import Ui_CustomerWidget
from Livestream.Livestream import Ui_LivestreamWidget
from LivestreamDetail.LivestreamDetail import Ui_LivestreamDetailWidget
from Order.Order import Ui_OrderWidget
from OrderDetail.OrderDetail import Ui_OrderDetailWidget
from Payment.Payment import Ui_PaymentWidget
from Product.Product import Ui_ProductWidget
from Seller.Seller import Ui_SellerWidget
from Statistics.Statistics import Ui_StatisticsWidget
from Voucher.Voucher import Ui_VoucherWidget


class BaseMixin:
    def __init__(self, seller_id="Admin", seller_name="Người bán", login_window=None):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.seller_id = seller_id
        self.seller_name = seller_name
        self.login_window = login_window

        # Hiển thị tên người bán đăng nhập thành công lên Header
        if hasattr(self.ui, 'lblUserScope'):
            self.ui.lblUserScope.setText(f"Xin chào, {self.seller_name} ({self.seller_id})")

        # 0. Bổ sung cột còn thiếu cho schema (an toàn khi chạy lại)
        ensure_schema()

        # 1. Khởi tạo các trang con
        self.init_sub_pages()

        # 2. Định tuyến Menu Sidebar và Nút Đăng xuất
        self.connect_sidebar_buttons()

        # 2b. Tinh chỉnh form: mở khóa ô nhập, thêm cột bảng, khu vực biểu đồ
        self.setup_form_tweaks()
        self.setup_charts_area()
        self.refactor_statistics_ui()

        # 3. Đọc dữ liệu từ SQLite đẩy lên Dashboard
        self.load_all_data_from_database()

        # 4. Thiết lập sự kiện và chức năng cho màn hình Người bán & Sản phẩm
        self.setup_seller_product_actions()

        # 5. Thiết lập sự kiện và chức năng cho tất cả các giao diện khác
        self.setup_all_other_actions()

        # 6. Vẽ biểu đồ lần đầu + thay emoji bằng icon Font Awesome
        self.update_all_charts()
        apply_fontawesome_icons(self)
        self.setup_tab_badges()

    def setup_tab_badges(self):
        """Gắn emoji vào badge tròn gradient ở đầu mỗi tab (khôi phục emoji thay icon Font Awesome)."""
        badges = {
            "ui_seller": "👤",
            "ui_product": "📦",
            "ui_customer": "👥",
            "ui_livestream": "🎥",
            "ui_livestream_detail": "📋",
            "ui_comment": "💬",
            "ui_order": "🛒",
            "ui_order_detail": "📝",
            "ui_payment": "💳",
            "ui_voucher": "🎟️",
            "ui_statistics": "📈",
        }
        for ui_attr, emoji in badges.items():
            ui_page = getattr(self, ui_attr, None)
            badge = getattr(ui_page, "lblIconBadge", None) if ui_page else None
            if badge is None:
                continue
            badge.setText(emoji)
            badge.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Logo thương hiệu ở sidebar (nền gradient tròn) — biểu tượng phát trực tiếp
        if hasattr(self.ui, "lblSidebarLogo"):
            self.ui.lblSidebarLogo.setText("📡")
            self.ui.lblSidebarLogo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Badge emoji tròn màu cho các thẻ số liệu tổng quan trên Dashboard
        cards = {
            "lblCardCustomerIcon": ("👥", "#8b5cf6"),
            "lblCardLivestreamIcon": ("🎥", "#ec4899"),
            "lblCardProductIcon": ("📦", "#f59e0b"),
            "lblCardOrderIcon": ("🛒", "#3b82f6"),
            "lblCardRevenueIcon": ("💰", "#10b981"),
            "lblCardVoucherIcon": ("🎟️", "#ef4444"),
        }
        for lbl_name, (emoji, color) in cards.items():
            lbl = getattr(self.ui, lbl_name, None)
            if lbl is None:
                continue
            lbl.setText(emoji)
            lbl.setMinimumSize(QtCore.QSize(44, 44))
            lbl.setMaximumSize(QtCore.QSize(44, 44))
            lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"background-color: {color}; border-radius: 22px; font-size: 20px;")

        self.style_dashboard_panels()

    def style_dashboard_panels(self):
        """Bọc nền trắng bo góc cho thẻ số liệu và 2 bảng, đồng bộ với 2 khung biểu đồ."""
        panel_css = ("background-color: #ffffff; border: 1px solid #e2e8f0;"
                     " border-radius: 12px;")
        # 6 thẻ số liệu tổng quan
        for card_name in ("cardCustomer", "cardLivestream", "cardProduct",
                          "cardOrder", "cardRevenue", "cardVoucher"):
            card = getattr(self.ui, card_name, None)
            if card is not None:
                # icon con đã có style riêng nên chỉ nhắm đúng QFrame gốc
                card.setStyleSheet(f"QFrame#{card_name} {{ {panel_css} }}")

        # 2 bảng bên dưới: bảng trong suốt để lộ nền card, header không kẻ viền
        for tbl in (self.ui.tblTopProducts, self.ui.tblActiveLivestreams):
            tbl.setStyleSheet(
                "QTableWidget { background-color: transparent; border: none;"
                " gridline-color: #eef2f7; }"
                "QHeaderView::section { background-color: #f8fafc; color: #334155;"
                " border: none; padding: 6px; font-weight: 600; }"
            )

        # Gộp tiêu đề + bảng vào chung một card nền trắng (giống khung biểu đồ)
        self._wrap_in_card(self.ui.verticalLayout_table1)
        self._wrap_in_card(self.ui.verticalLayout_table2)

        # In đậm tất cả tiêu đề panel trên Dashboard cho dễ nhận biết
        for lbl_name in ("lblChart1Title", "lblChart2Title", "lblTable1Header", "lblTable2Header"):
            lbl = getattr(self.ui, lbl_name, None)
            if lbl is not None:
                f = lbl.font()
                f.setBold(True)
                f.setPointSize(max(f.pointSize(), 12))
                lbl.setFont(f)
                lbl.setStyleSheet("color: #1e293b;")

    def _wrap_in_card(self, inner_layout):
        """Chuyển một QVBoxLayout (tiêu đề + bảng) vào trong QFrame nền trắng bo góc."""
        idx = self.ui.layoutTables.indexOf(inner_layout)
        if idx < 0:
            return
        # Gỡ layout con khỏi layoutTables để có thể gắn vào frame (layout không được có 2 parent)
        self.ui.layoutTables.removeItem(inner_layout)
        card = QtWidgets.QFrame(parent=self.ui.pageDashboard)
        card.setObjectName(f"panelCard{idx}")
        card.setStyleSheet(f"QFrame#panelCard{idx} {{ background-color: #ffffff;"
                           " border: 1px solid #e2e8f0; border-radius: 12px; }")
        card.setLayout(inner_layout)  # reparent layout + các widget con vào frame
        inner_layout.setContentsMargins(16, 14, 16, 16)
        self.ui.layoutTables.insertWidget(idx, card)

    def setup_form_tweaks(self):
        """Mở khóa các ô nhập bị readOnly trong .ui và bổ sung cột bảng bằng code."""
        # Ô Tổng tiền (Order) và Thành tiền (OrderDetail) bị đặt readOnly trong Qt Designer
        self.ui_order.txtTongTien.setReadOnly(False)
        self.ui_order_detail.txtThanhTien.setReadOnly(False)

        # Bảng Đơn hàng: thêm cột "Sản phẩm" hiển thị các SP khách mua
        tbl = self.ui_order.tblOrder
        col = tbl.columnCount()
        tbl.setColumnCount(col + 1)
        tbl.setHorizontalHeaderItem(col, QTableWidgetItem("Sản phẩm"))

        # Bảng Chi tiết đơn: thêm cột "Voucher" của đơn hàng tương ứng
        tbl = self.ui_order_detail.tblOrderDetail
        col = tbl.columnCount()
        tbl.setColumnCount(col + 1)
        tbl.setHorizontalHeaderItem(col, QTableWidgetItem("Voucher"))

        # OrderDetail: chọn sản phẩm tự điền giá bán; SL/giá đổi thì tự tính thành tiền
        self.ui_order_detail.cbSanPham.currentIndexChanged.connect(self._orderdetail_autofill_price)
        self.ui_order_detail.spinSoLuong.valueChanged.connect(self._orderdetail_recalc_total)
        self.ui_order_detail.txtGiaBan.textEdited.connect(self._orderdetail_recalc_total)

    def _orderdetail_autofill_price(self):
        ma_sp = get_widget_value(self.ui_order_detail.cbSanPham, "combo_text")
        if not ma_sp:
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT GiaBan FROM SAN_PHAM WHERE MaSP = ?", (ma_sp,))
            row = cursor.fetchone()
            conn.close()
            if row and row[0] is not None:
                self.ui_order_detail.txtGiaBan.setText(f"{row[0]:g}")
                self._orderdetail_recalc_total()
        except Exception:
            pass

    def _orderdetail_recalc_total(self):
        try:
            gia = float(self.ui_order_detail.txtGiaBan.text().strip().replace(",", "") or 0)
        except ValueError:
            gia = 0
        so_luong = self.ui_order_detail.spinSoLuong.value()
        self.ui_order_detail.txtThanhTien.setText(f"{gia * so_luong:g}")

    def refresh_dependents(self):
        """Đồng bộ mọi màn hình liên quan sau mỗi lần Lưu/Xóa: bảng, combobox, thẻ số liệu, biểu đồ."""
        self.load_all_data_from_database()
        self.populate_all_comboboxes()
        self.load_statistics_data()
        self.update_all_charts()

    def init_sub_pages(self):
        self.page_product = QWidget()
        self.ui_product = Ui_ProductWidget()
        self.ui_product.setupUi(self.page_product)
        self.ui.stackedWidget.addWidget(self.page_product)

        self.page_comment = QWidget()
        self.ui_comment = Ui_CommentWidget()
        self.ui_comment.setupUi(self.page_comment)
        self.ui.stackedWidget.addWidget(self.page_comment)

        self.page_order = QWidget()
        self.ui_order = Ui_OrderWidget()
        self.ui_order.setupUi(self.page_order)
        self.ui.stackedWidget.addWidget(self.page_order)

        self.page_voucher = QWidget()
        self.ui_voucher = Ui_VoucherWidget()
        self.ui_voucher.setupUi(self.page_voucher)
        self.ui.stackedWidget.addWidget(self.page_voucher)

        self.page_livestream_detail = QWidget()
        self.ui_livestream_detail = Ui_LivestreamDetailWidget()
        self.ui_livestream_detail.setupUi(self.page_livestream_detail)
        self.ui.stackedWidget.addWidget(self.page_livestream_detail)

        self.page_order_detail = QWidget()
        self.ui_order_detail = Ui_OrderDetailWidget()
        self.ui_order_detail.setupUi(self.page_order_detail)
        self.ui.stackedWidget.addWidget(self.page_order_detail)

        self.page_payment = QWidget()
        self.ui_payment = Ui_PaymentWidget()
        self.ui_payment.setupUi(self.page_payment)
        self.ui.stackedWidget.addWidget(self.page_payment)

        self.page_statistics = QWidget()
        self.ui_statistics = Ui_StatisticsWidget()
        self.ui_statistics.setupUi(self.page_statistics)
        self.ui.stackedWidget.addWidget(self.page_statistics)

        self.page_livestream = QWidget()
        self.ui_livestream = Ui_LivestreamWidget()
        self.ui_livestream.setupUi(self.page_livestream)
        self.ui.stackedWidget.addWidget(self.page_livestream)

        self.page_seller = QWidget()
        self.ui_seller = Ui_SellerWidget()
        self.ui_seller.setupUi(self.page_seller)
        self.ui.stackedWidget.addWidget(self.page_seller)

        self.page_customer = QWidget()
        self.ui_customer = Ui_CustomerWidget()
        self.ui_customer.setupUi(self.page_customer)
        self.ui.stackedWidget.addWidget(self.page_customer)

    def connect_sidebar_buttons(self):
        self.ui.btnMenuProduct.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.page_product))
        self.ui.btnMenuComment.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.page_comment))
        self.ui.btnMenuOrder.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.page_order))
        self.ui.btnMenuVoucher.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.page_voucher))
        self.ui.btnMenuLivestreamDetail.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.page_livestream_detail))
        self.ui.btnMenuOrderDetail.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.page_order_detail))
        self.ui.btnMenuPayment.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.page_payment))
        self.ui.btnMenuStatistics.clicked.connect(self._open_statistics_tab)
        self.ui.btnMenuLivestream.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.page_livestream))
        self.ui.btnMenuSeller.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.page_seller))

        if hasattr(self.ui, "btnMenuCustomer"):
            self.ui.btnMenuCustomer.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.page_customer))
        if hasattr(self.ui, "btnMenuDashboard"):
            self.ui.btnMenuDashboard.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        if hasattr(self.ui, 'btnMenuLogout'):
            self.ui.btnMenuLogout.clicked.connect(self.process_logout)

    def process_logout(self):
        if self.login_window:
            self.login_window.show()
        self.close()

    # ==================== ĐẨY DỮ LIỆU THỰC TẾ TỪ SQLITE LÊN UI ====================
    def load_all_data_from_database(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # --- 1. THẺ THỐNG KÊ (STATS CARDS) ON MAIN DASHBOARD ---
            cursor.execute("SELECT COUNT(*) FROM KHACH_HANG")
            self.ui.lblCardCustomerNum.setText(str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM LIVESTREAM")
            self.ui.lblCardLivestreamNum.setText(str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM SAN_PHAM")
            self.ui.lblCardProductNum.setText(str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM DON_HANG")
            self.ui.lblCardOrderNum.setText(str(cursor.fetchone()[0]))

            cursor.execute(
                "SELECT SUM(TongTien) FROM HOA_DON WHERE TrangThaiHD = 'Đã thanh toán' OR TrangThaiHD LIKE '%Da%'")
            total_revenue = cursor.fetchone()[0] or 0
            if total_revenue >= 1_000_000:
                self.ui.lblCardRevenueNum.setText(f"{total_revenue / 1_000_000:.1f}M")
            else:
                self.ui.lblCardRevenueNum.setText(f"{total_revenue:,.0f} VND")

            cursor.execute("SELECT COUNT(*) FROM VOUCHER WHERE TrangThai = 'Đang áp dụng' OR TrangThai LIKE '%ap%'")
            self.ui.lblCardVoucherNum.setText(str(cursor.fetchone()[0]))

            # --- 2. CÁC BẢNG TRÊN TRANG CHỦ DASHBOARD ---
            # Sản phẩm bán chạy: nhiều đơn "Đã giao" + hóa đơn "Đã thanh toán", cảnh báo tồn thấp
            cursor.execute("""
                SELECT p.MaSP, p.TenSP,
                       COALESCE(SUM(c.SoLuong), 0) as DaBan,
                       p.SoLuongTon
                FROM SAN_PHAM p
                JOIN CHI_TIET_DON_HANG c ON p.MaSP = c.MaSP
                JOIN DON_HANG dh ON c.MaDonHang = dh.MaDonHang AND dh.TrangThaiDH = 'Đã giao'
                JOIN HOA_DON hd ON hd.MaDonHang = dh.MaDonHang AND hd.TrangThaiHD = 'Đã thanh toán'
                GROUP BY p.MaSP ORDER BY DaBan DESC LIMIT 5
            """)
            top_rows = cursor.fetchall()
            self.populate_table(self.ui.tblTopProducts, top_rows)
            for c_idx, header in enumerate(["Mã SP", "Tên SP", "Đã bán", "Tồn kho"]):
                self.ui.tblTopProducts.setHorizontalHeaderItem(c_idx, QTableWidgetItem(header))
            for r_idx, row in enumerate(top_rows):
                if row[3] is not None and row[3] < 10:
                    item = self.ui.tblTopProducts.item(r_idx, 3)
                    if item:
                        item.setForeground(QtGui.QBrush(QtGui.QColor("#dc2626")))
                        item.setText(f"{row[3]} (sắp hết)")

            # Livestream đang chạy hoặc gần nhất (đồng bộ với tab Livestream)
            cursor.execute("""
                SELECT MaLive, TenLive, MaNguoiBan, TrangThai FROM LIVESTREAM
                ORDER BY CASE WHEN TrangThai LIKE '%ang%' THEN 0 ELSE 1 END, ThoiGianBatDau DESC
                LIMIT 5
            """)
            self.populate_table(self.ui.tblActiveLivestreams, cursor.fetchall())

            # --- 3. ĐỔ DỮ LIỆU VÀO CÁC PHÂN HỆ CON ---
            # Phân hệ Sản phẩm
            if hasattr(self.ui_product, 'tblProduct'):
                cursor.execute("SELECT MaSP, TenSP, GiaBan, SoLuongTon, HinhAnh, CASE WHEN SoLuongTon > 0 THEN 'Còn hàng' ELSE 'Hết hàng' END FROM SAN_PHAM")
                self.populate_table(self.ui_product.tblProduct, cursor.fetchall())

            # Phân hệ Bình luận
            if hasattr(self.ui_comment, 'tblComment'):
                cursor.execute("SELECT MaBinhLuan, MaLive, NguoiBinhLuan, NoiDung, ThoiGian FROM BINH_LUAN")
                self.populate_table(self.ui_comment.tblComment, cursor.fetchall())

            # Phân hệ Đơn hàng (query dùng chung với refresh_order_table)
            self.refresh_order_table()

            # Phân hệ Khách hàng (Đã sửa từ tblCustomer sang tblKhachHang)
            if hasattr(self.ui_customer, 'tblKhachHang'):
                cursor.execute("SELECT MaKhachHang, HoTen, SoDienThoai, Email, DiaChi, '2026-07-15' FROM KHACH_HANG")
                self.populate_table(self.ui_customer.tblKhachHang, cursor.fetchall())

            # Phân hệ Người bán
            if hasattr(self.ui_seller, 'tblSeller'):
                cursor.execute("SELECT MaNguoiBan, HoTen, SoDienThoai, Email, TenCuaHang FROM NGUOI_BAN")
                self.populate_table(self.ui_seller.tblSeller, cursor.fetchall())

            # Phân hệ Voucher
            if hasattr(self.ui_voucher, 'tblVoucher'):
                cursor.execute("""
                    SELECT
                        MaVoucher,
                        COALESCE(LoaiUuDai, 'Số tiền cố định (VND)') AS LoaiUuDai,
                        GiaTriGiam,
                        DieuKienApDung,
                        COALESCE(GiamToiDa, GiaTriGiam) AS GiamToiDa,
                        NgayBatDau,
                        NgayKetThuc,
                        TrangThai
                    FROM VOUCHER
                """)
                self.populate_table(self.ui_voucher.tblVoucher, cursor.fetchall())

            # Phân hệ Livestream
            if hasattr(self.ui_livestream, 'tblLivestream'):
                cursor.execute("SELECT MaLive, TenLive, ThoiGianBatDau, MaNguoiBan, TrangThai FROM LIVESTREAM")
                self.populate_table(self.ui_livestream.tblLivestream, cursor.fetchall())

            # Phân hệ Livestream Chi Tiết
            if hasattr(self.ui_livestream_detail, 'tblLivestreamDetail'):
                cursor.execute("""
                    SELECT 
                        (lsp.MaLive || '-' || lsp.MaSP) AS MaChiTietLive,
                        l.TenLive,
                        lsp.MaSP,
                        p.TenSP,
                        p.SoLuongTon,
                        p.GiaBan
                    FROM LIVESTREAM_SAN_PHAM lsp
                    JOIN LIVESTREAM l ON lsp.MaLive = l.MaLive
                    JOIN SAN_PHAM p ON lsp.MaSP = p.MaSP
                """)
                self.populate_table(self.ui_livestream_detail.tblLivestreamDetail, cursor.fetchall())

            # Phân hệ Chi Tiết Đơn Hàng (query dùng chung với refresh_order_detail_table)
            self.refresh_order_detail_table()

            # Phân hệ Thanh Toán (Payment)
            if hasattr(self.ui_payment, 'tblPayment'):
                cursor.execute("SELECT MaHoaDon, MaDonHang, ThoiGianLap, TongTien, PhuongThucTT, TrangThaiHD FROM HOA_DON")
                self.populate_table(self.ui_payment.tblPayment, cursor.fetchall())

            # Phân hệ Thống Kê (Statistics)
            if hasattr(self.ui_statistics, 'tblStatistics'):
                cursor.execute("""
                    SELECT 
                        l.MaLive,
                        l.TenLive,
                        nb.HoTen,
                        COALESCE((
                            SELECT SUM(dh.TongTien) 
                            FROM DON_HANG dh
                            JOIN BINH_LUAN bl ON dh.MaBinhLuan = bl.MaBinhLuan
                            WHERE bl.MaLive = l.MaLive
                        ), 0) AS DoanhThu,
                        COALESCE((
                            SELECT COUNT(dh.MaDonHang) 
                            FROM DON_HANG dh
                            JOIN BINH_LUAN bl ON dh.MaBinhLuan = bl.MaBinhLuan
                            WHERE bl.MaLive = l.MaLive
                        ), 0) AS SoDonDat,
                        COALESCE((
                            SELECT SUM(ct.SoLuong) 
                            FROM CHI_TIET_DON_HANG ct
                            JOIN DON_HANG dh ON ct.MaDonHang = dh.MaDonHang
                            JOIN BINH_LUAN bl ON dh.MaBinhLuan = bl.MaBinhLuan
                            WHERE bl.MaLive = l.MaLive
                        ), 0) AS SanPhamDaBan
                    FROM LIVESTREAM l
                    LEFT JOIN NGUOI_BAN nb ON l.MaNguoiBan = nb.MaNguoiBan
                """)
                self.populate_table(self.ui_statistics.tblStatistics, cursor.fetchall())
                self._format_stats_table()

                # Cập nhật Thẻ Thống kê (Summary Cards) trên trang Thống kê
                cursor.execute("SELECT SUM(TongTien) FROM HOA_DON WHERE TrangThaiHD = 'Đã thanh toán' OR TrangThaiHD LIKE '%Da%'")
                tot_rev = cursor.fetchone()[0] or 0
                cursor.execute("SELECT COUNT(*) FROM DON_HANG")
                tot_ord = cursor.fetchone()[0] or 0
                avg_val = tot_rev / tot_ord if tot_ord > 0 else 0

                if hasattr(self.ui_statistics, 'lblTotalRevenue'):
                    self.ui_statistics.lblTotalRevenue.setText(f"{tot_rev:,.0f} VNĐ")
                if hasattr(self.ui_statistics, 'lblTotalOrders'):
                    self.ui_statistics.lblTotalOrders.setText(f"{tot_ord:,} đơn đặt")
                if hasattr(self.ui_statistics, 'lblAvgOrderValue'):
                    self.ui_statistics.lblAvgOrderValue.setText(f"{avg_val:,.0f} VNĐ")

            conn.close()
        except Exception as e:
            print(f"Lỗi truy vấn SQL: {e}")

    def populate_table(self, table_widget, data):
        table_widget.setRowCount(0)
        for row_idx, row_data in enumerate(data):
            table_widget.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                val_str = str(value if value is not None else "")
                item = QTableWidgetItem(val_str)
                # Stylesheet nền sáng nhưng màu chữ mặc định theo theme bị trùng nền — ép chữ đen
                item.setForeground(QtGui.QBrush(QtGui.QColor("#000000")))
                table_widget.setItem(row_idx, col_idx, item)
        if hasattr(table_widget, 'horizontalHeader') and table_widget.horizontalHeader():
            table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    # ==================== PHÂN HỆ QUẢN LÝ NGƯỜI BÁN & SẢN PHẨM KHỚP SQLITE ====================

    def setup_seller_product_actions(self):
        # Biến lưu trữ ID dòng đang chọn
        self.selected_product_id = None
        self.selected_seller_id = None

        # Thiết lập chế độ chọn dòng và không cho sửa trực tiếp trên bảng
        if hasattr(self.ui_product, 'tblProduct'):
            self.ui_product.tblProduct.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
            self.ui_product.tblProduct.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
            self.ui_product.tblProduct.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            self.ui_product.tblProduct.cellClicked.connect(self.product_cell_clicked)
            self.ui_product.btnThem.clicked.connect(self.product_action_them)
            self.ui_product.btnSua.clicked.connect(self._on_product_edit_button)
            self.ui_product.btnLuu.clicked.connect(self.product_action_save)
            self.ui_product.btnLuu.setVisible(False)
            self._product_action = None
            self._set_product_form_enabled(False)
            self.ui_product.btnXoa.clicked.connect(self.product_action_xoa)
            self.ui_product.btnHuy.clicked.connect(self.product_action_clear)
            self.ui_product.btnXuatExcel.clicked.connect(self.product_export_excel)
            self.ui_product.btnSearch.clicked.connect(self.product_search)
            self.ui_product.btnRefresh.clicked.connect(self.product_refresh)
            if hasattr(self.ui_product, 'btnSelectImage'):
                self.ui_product.btnSelectImage.clicked.connect(self.product_select_image)

            # Đồng bộ combobox trạng thái và spinbox tồn kho
            self.ui_product.spinSoLuongTon.valueChanged.connect(self.product_spin_changed)
            self.ui_product.cbTrangThai.currentIndexChanged.connect(self.product_status_changed)

        if hasattr(self.ui_seller, 'tblSeller'):
            self.ui_seller.tblSeller.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
            self.ui_seller.tblSeller.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
            self.ui_seller.tblSeller.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            self.ui_seller.tblSeller.cellClicked.connect(self.seller_cell_clicked)
            self.ui_seller.btnThem.clicked.connect(self.seller_action_them)
            self.ui_seller.btnSua.clicked.connect(self._on_seller_edit_button)
            self.ui_seller.btnLuu.clicked.connect(self.seller_action_save)
            self.ui_seller.btnLuu.setVisible(False)
            self._seller_action = None
            self._set_seller_form_enabled(False)
            self.ui_seller.btnXoa.clicked.connect(self.seller_action_xoa)
            self.ui_seller.btnHuy.clicked.connect(self.seller_action_clear)
            self.ui_seller.btnXuatExcel.clicked.connect(self.seller_export_excel)
            self.ui_seller.btnSearch.clicked.connect(self.seller_search)
            self.ui_seller.btnRefresh.clicked.connect(self.seller_refresh)

    def setup_all_other_actions(self):
        # Initial populate of combo boxes
        self.populate_all_comboboxes()

        # Comment Tab
        comment_mappings = [
            ("MaLive", self.ui_comment.cbLivestream, "combo_text"),
            ("NguoiBinhLuan", self.ui_comment.txtTenNguoiDung, "text"),
            ("NoiDung", self.ui_comment.txtNoiDung, "text"),
            ("ThoiGian", self.ui_comment.dateThoiGian, "datetime")
        ]
        self.comment_controller = DbFormController(
            self, self.ui_comment, self.ui_comment.tblComment, "BINH_LUAN", "MaBinhLuan", comment_mappings, self.refresh_comment_table
        )

        # Customer Tab
        customer_mappings = [
            ("HoTen", self.ui_customer.txtTenKhachHang, "text"),
            ("SoDienThoai", self.ui_customer.txtSoDienThoai, "text"),
            ("Email", self.ui_customer.txtEmail, "text"),
            ("DiaChi", self.ui_customer.txtDiaChi, "text")
        ]
        self.customer_controller = DbFormController(
            self, self.ui_customer, self.ui_customer.tblKhachHang, "KHACH_HANG", "MaKhachHang", customer_mappings, self.refresh_customer_table
        )

        # Livestream Tab
        livestream_mappings = [
            ("TenLive", self.ui_livestream.txtTieuDe, "text"),
            ("MaNguoiBan", self.ui_livestream.cbNguoiBan, "combo_text"),
            ("ThoiGianBatDau", self.ui_livestream.dateNgayKhaiMac, "datetime"),
            ("TrangThai", self.ui_livestream.cbTrangThai, "combo_text")
        ]
        self.livestream_controller = DbFormController(
            self, self.ui_livestream, self.ui_livestream.tblLivestream, "LIVESTREAM", "MaLive", livestream_mappings, self.refresh_livestream_table
        )

        # Livestream Detail Tab
        livestream_detail_mappings = [
            ("MaLive", self.ui_livestream_detail.cbLivestream, "combo_text"),
            ("MaSP", self.ui_livestream_detail.cbSanPham, "combo_text"),
            ("SoLuongTon", self.ui_livestream_detail.spinSoLuongGioiThieu, "spin"),
            ("GiaBan", self.ui_livestream_detail.txtGiaKhuyenMai, "text")
        ]
        self.livestream_detail_controller = DbFormController(
            self, self.ui_livestream_detail, self.ui_livestream_detail.tblLivestreamDetail, "LIVESTREAM_SAN_PHAM", "MaChiTietLive", livestream_detail_mappings, self.refresh_livestream_detail_table
        )

        # Order Tab
        order_mappings = [
            ("NgayDat", self.ui_order.dateNgayDat, "datetime"),
            ("MaLive", self.ui_order.cbLivestream, "combo_text"),
            ("HoTen", self.ui_order.txtTenKhachHang, "text"),
            ("SoDienThoai", self.ui_order.txtSoDienThoai, "text"),
            ("DiaChi", self.ui_order.txtDiaChiGiao, "text"),
            ("MaVoucher", self.ui_order.cbVoucher, "combo_text"),
            ("TrangThaiDH", self.ui_order.cbTrangThai, "combo_text"),
            ("TongTien", self.ui_order.txtTongTien, "text")
        ]
        self.order_controller = DbFormController(
            self, self.ui_order, self.ui_order.tblOrder, "DON_HANG", "MaDonHang", order_mappings, self.refresh_order_table
        )

        # Order Detail Tab
        order_detail_mappings = [
            ("MaDonHang", self.ui_order_detail.cbDonHang, "combo_text"),
            ("MaSP", self.ui_order_detail.cbSanPham, "combo_text"),
            ("SoLuong", self.ui_order_detail.spinSoLuong, "spin"),
            ("DonGia", self.ui_order_detail.txtGiaBan, "text"),
            ("ThanhTien", self.ui_order_detail.txtThanhTien, "text")
        ]
        self.order_detail_controller = DbFormController(
            self, self.ui_order_detail, self.ui_order_detail.tblOrderDetail, "CHI_TIET_DON_HANG", "MaChiTietDH", order_detail_mappings, self.refresh_order_detail_table
        )

        # Payment Tab
        payment_mappings = [
            ("MaDonHang", self.ui_payment.cbDonHang, "combo_text"),
            ("ThoiGianLap", self.ui_payment.dateThanhToan, "datetime"),
            ("TongTien", self.ui_payment.txtSoTien, "text"),
            ("PhuongThucTT", self.ui_payment.cbPhuongThuc, "combo_text"),
            ("TrangThaiHD", self.ui_payment.cbTrangThai, "combo_text")
        ]
        self.payment_controller = DbFormController(
            self, self.ui_payment, self.ui_payment.tblPayment, "HOA_DON", "MaHoaDon", payment_mappings, self.refresh_payment_table
        )

        # Voucher Tab
        voucher_mappings = [
            ("MaVoucher", self.ui_voucher.txtMaVoucher, "text"),
            ("LoaiUuDai", self.ui_voucher.cbLoaiVoucher, "combo_text"),
            ("GiaTriGiam", self.ui_voucher.txtGiaTriGiam, "text"),
            ("DieuKienApDung", self.ui_voucher.txtDonHangToiThieu, "text"),
            ("GiamToiDa", self.ui_voucher.txtGiamToiDa, "text"),
            ("NgayBatDau", self.ui_voucher.dateStart, "date"),
            ("NgayKetThuc", self.ui_voucher.dateEnd, "date"),
            ("TrangThai", self.ui_voucher.cbKichHoat, "combo_text")
        ]
        self.voucher_controller = DbFormController(
            self, self.ui_voucher, self.ui_voucher.tblVoucher, "VOUCHER", "MaVoucher", voucher_mappings, self.refresh_voucher_table
        )

        # Statistics Tab
        self.setup_statistics_actions()

    def populate_all_comboboxes(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 1. Fetch Livestreams
            cursor.execute("SELECT MaLive, TenLive FROM LIVESTREAM")
            lives = cursor.fetchall()
            live_items = [f"{row[0]} - {row[1]}" for row in lives]
            
            self.ui_comment.cbLivestream.clear()
            self.ui_comment.cbLivestream.addItems(live_items)
            
            self.ui_livestream_detail.cbLivestream.clear()
            self.ui_livestream_detail.cbLivestream.addItems(live_items)
            
            self.ui_order.cbLivestream.clear()
            self.ui_order.cbLivestream.addItems(live_items)
            
            # 2. Fetch Sellers
            cursor.execute("SELECT MaNguoiBan, HoTen FROM NGUOI_BAN")
            sellers = cursor.fetchall()
            seller_items = [f"{row[0]} - {row[1]}" for row in sellers]
            self.ui_livestream.cbNguoiBan.clear()
            self.ui_livestream.cbNguoiBan.addItems(seller_items)
            
            # 3. Fetch Products
            cursor.execute("SELECT MaSP, TenSP FROM SAN_PHAM")
            prods = cursor.fetchall()
            prod_items = [f"{row[0]} - {row[1]}" for row in prods]
            
            self.ui_livestream_detail.cbSanPham.clear()
            self.ui_livestream_detail.cbSanPham.addItems(prod_items)
            
            self.ui_order_detail.cbSanPham.clear()
            self.ui_order_detail.cbSanPham.addItems(prod_items)
            
            # 4. Fetch Vouchers
            cursor.execute("SELECT MaVoucher, TenVoucher FROM VOUCHER")
            vouchers = cursor.fetchall()
            voucher_items = ["Không"] + [f"{row[0]} - {row[1]}" for row in vouchers]
            self.ui_order.cbVoucher.clear()
            self.ui_order.cbVoucher.addItems(voucher_items)
            
            # 5. Fetch Orders
            cursor.execute("SELECT MaDonHang FROM DON_HANG")
            orders = cursor.fetchall()
            order_items = [row[0] for row in orders]
            
            self.ui_order_detail.cbDonHang.clear()
            self.ui_order_detail.cbDonHang.addItems(order_items)
            
            self.ui_payment.cbDonHang.clear()
            self.ui_payment.cbDonHang.addItems(order_items)
            
            conn.close()
        except Exception as e:
            print(f"Error populating comboboxes: {e}")

    def refresh_comment_table(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT MaBinhLuan, MaLive, NguoiBinhLuan, NoiDung, ThoiGian FROM BINH_LUAN")
            self.populate_table(self.ui_comment.tblComment, cursor.fetchall())
            conn.close()
            self.populate_all_comboboxes()
        except Exception as e:
            print(f"Error refreshing comments: {e}")

    def refresh_customer_table(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT MaKhachHang, HoTen, SoDienThoai, Email, DiaChi, '2026-07-15' FROM KHACH_HANG")
            self.populate_table(self.ui_customer.tblKhachHang, cursor.fetchall())
            conn.close()
            self.populate_all_comboboxes()
        except Exception as e:
            print(f"Error refreshing customers: {e}")

    def refresh_livestream_table(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT MaLive, TenLive, ThoiGianBatDau, MaNguoiBan, TrangThai FROM LIVESTREAM")
            self.populate_table(self.ui_livestream.tblLivestream, cursor.fetchall())
            conn.close()
            self.populate_all_comboboxes()
        except Exception as e:
            print(f"Error refreshing livestreams: {e}")

    def refresh_livestream_detail_table(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    (lsp.MaLive || '-' || lsp.MaSP) AS MaChiTietLive,
                    l.TenLive,
                    lsp.MaSP,
                    p.TenSP,
                    p.SoLuongTon,
                    p.GiaBan
                FROM LIVESTREAM_SAN_PHAM lsp
                JOIN LIVESTREAM l ON lsp.MaLive = l.MaLive
                JOIN SAN_PHAM p ON lsp.MaSP = p.MaSP
            """)
            self.populate_table(self.ui_livestream_detail.tblLivestreamDetail, cursor.fetchall())
            conn.close()
            self.populate_all_comboboxes()
        except Exception as e:
            print(f"Error refreshing livestream details: {e}")

    def refresh_order_table(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    dh.MaDonHang,
                    dh.NgayDat,
                    kh.HoTen,
                    kh.SoDienThoai,
                    dh.TongTien,
                    COALESCE(v.TenVoucher, dh.MaVoucher),
                    dh.TrangThaiDH,
                    COALESCE((SELECT GROUP_CONCAT(p.TenSP, ', ')
                              FROM CHI_TIET_DON_HANG ct JOIN SAN_PHAM p ON ct.MaSP = p.MaSP
                              WHERE ct.MaDonHang = dh.MaDonHang), '(chưa có SP)')
                FROM DON_HANG dh
                LEFT JOIN KHACH_HANG kh ON dh.MaKhachHang = kh.MaKhachHang
                LEFT JOIN VOUCHER v ON dh.MaVoucher = v.MaVoucher
            """)
            self.populate_table(self.ui_order.tblOrder, cursor.fetchall())
            conn.close()
            self.populate_all_comboboxes()
        except Exception as e:
            print(f"Error refreshing orders: {e}")

    def refresh_order_detail_table(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    (ct.MaDonHang || '-' || ct.MaSP) AS MaChiTietDH,
                    ct.MaDonHang,
                    ct.MaSP,
                    p.TenSP,
                    ct.SoLuong,
                    ct.DonGia,
                    ct.ThanhTien,
                    COALESCE(v.TenVoucher, dh.MaVoucher, 'Không')
                FROM CHI_TIET_DON_HANG ct
                JOIN SAN_PHAM p ON ct.MaSP = p.MaSP
                LEFT JOIN DON_HANG dh ON ct.MaDonHang = dh.MaDonHang
                LEFT JOIN VOUCHER v ON dh.MaVoucher = v.MaVoucher
            """)
            self.populate_table(self.ui_order_detail.tblOrderDetail, cursor.fetchall())
            conn.close()
            self.populate_all_comboboxes()
        except Exception as e:
            print(f"Error refreshing order details: {e}")

    def refresh_payment_table(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT MaHoaDon, MaDonHang, ThoiGianLap, TongTien, PhuongThucTT, TrangThaiHD FROM HOA_DON")
            self.populate_table(self.ui_payment.tblPayment, cursor.fetchall())
            conn.close()
            self.populate_all_comboboxes()
        except Exception as e:
            print(f"Error refreshing payments: {e}")

    def refresh_voucher_table(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    MaVoucher,
                    COALESCE(LoaiUuDai, 'Số tiền cố định (VND)') AS LoaiUuDai,
                    GiaTriGiam,
                    DieuKienApDung,
                    COALESCE(GiamToiDa, GiaTriGiam) AS GiamToiDa,
                    NgayBatDau,
                    NgayKetThuc,
                    TrangThai
                FROM VOUCHER
            """)
            self.populate_table(self.ui_voucher.tblVoucher, cursor.fetchall())
            conn.close()
            self.populate_all_comboboxes()
        except Exception as e:
            print(f"Error refreshing vouchers: {e}")

    def search_table_generic(self, table_widget, db_table, pk_col, search_text, refresh_callback):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({db_table})")
            cols = [row[1] for row in cursor.fetchall()]
            if not cols:
                conn.close()
                return

            conditions = []
            params = []
            for col in cols:
                conditions.append(f"{col} LIKE ?")
                params.append(f"%{search_text}%")

            query = f"SELECT * FROM {db_table} WHERE {' OR '.join(conditions)}"
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            self.populate_table(table_widget, results)
        except Exception as e:
            print(f"Error generic searching: {e}")


