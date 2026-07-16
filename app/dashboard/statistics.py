"""StatisticsMixin: tab Thống kê — nạp báo cáo, lọc ngày, xuất Excel, tinh chỉnh UI."""
import sqlite3

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QMessageBox

from app.config import DB_PATH


class StatisticsMixin:
    def setup_statistics_actions(self):
        if hasattr(self.ui_statistics, 'btnFilter'):
            self.ui_statistics.btnFilter.clicked.connect(self.statistics_filter)
        if hasattr(self.ui_statistics, 'btnRefresh'):
            self.ui_statistics.btnRefresh.clicked.connect(self.statistics_refresh)
        if hasattr(self.ui_statistics, 'btnXuatExcel'):
            self.ui_statistics.btnXuatExcel.clicked.connect(self.statistics_export_excel)
        
        # Mặc định bao trọn toàn bộ dữ liệu (từ trước đến nay)
        self.ui_statistics.dateStart.setDate(QtCore.QDate(2020, 1, 1))
        self.ui_statistics.dateEnd.setDate(QtCore.QDate.currentDate().addDays(1))
        # Nạp báo cáo toàn thời gian ngay khi khởi động
        self.load_statistics_data()

    def load_statistics_data(self, start_date=None, end_date=None):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            query = """
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
            """
            
            params = []
            if start_date and end_date:
                query += " WHERE l.ThoiGianBatDau BETWEEN ? AND ?"
                params = [start_date + " 00:00:00", end_date + " 23:59:59"]
                
            cursor.execute(query, params)
            rows = cursor.fetchall()
            self.populate_table(self.ui_statistics.tblStatistics, rows)
            self._format_stats_table()

            # Vẽ lại biểu đồ thống kê theo đúng bộ dữ liệu (kể cả khi lọc ngày)
            self.update_statistics_charts(rows, start_date, end_date)
            
            # Recalculate summary cards
            tot_rev = sum(row[3] for row in rows)
            tot_ord = sum(row[4] for row in rows)
            avg_val = tot_rev / tot_ord if tot_ord > 0 else 0
            
            if hasattr(self.ui_statistics, 'lblTotalRevenue'):
                self.ui_statistics.lblTotalRevenue.setText(f"{tot_rev:,.0f} VNĐ")
            if hasattr(self.ui_statistics, 'lblTotalOrders'):
                self.ui_statistics.lblTotalOrders.setText(f"{tot_ord:,} đơn đặt")
            if hasattr(self.ui_statistics, 'lblAvgOrderValue'):
                self.ui_statistics.lblAvgOrderValue.setText(f"{avg_val:,.0f} VNĐ")
                
            conn.close()
        except Exception as e:
            print(f"Error loading stats data: {e}")

    def statistics_filter(self):
        start_date = self.ui_statistics.dateStart.date().toString("yyyy-MM-dd")
        end_date = self.ui_statistics.dateEnd.date().toString("yyyy-MM-dd")
        self.load_statistics_data(start_date, end_date)
        if hasattr(self.ui_statistics, 'lblStatus'):
            self.ui_statistics.lblStatus.setText(f"Trạng thái: Đã lọc từ {start_date} đến {end_date}")

    def _open_statistics_tab(self):
        # Mở tab Thống kê: chuyển trang + tự nạp báo cáo toàn thời gian
        self.ui.stackedWidget.setCurrentWidget(self.page_statistics)
        self.load_statistics_data()

    def statistics_refresh(self):
        # Làm mới = xem lại toàn bộ dữ liệu từ trước đến nay
        self.ui_statistics.dateStart.setDate(QtCore.QDate(2020, 1, 1))
        self.ui_statistics.dateEnd.setDate(QtCore.QDate.currentDate().addDays(1))
        self.load_statistics_data()
        if hasattr(self.ui_statistics, 'lblStatus'):
            self.ui_statistics.lblStatus.setText("Trạng thái: Đã làm mới báo cáo.")

    def statistics_export_excel(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Lưu file Excel thống kê", "", "Excel Files (*.xlsx);;All Files (*)"
        )
        if not path:
            return
            
        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "ThongKeDoanhThu"
            
            headers = ["Mã Stream", "Tiêu Đề Livestream", "Người Bán", "Doanh Thu (VND)", "Số Đơn Đặt", "Sản Phẩm Đã Bán"]
            ws.append(headers)
            
            for row in range(self.ui_statistics.tblStatistics.rowCount()):
                row_data = []
                for col in range(self.ui_statistics.tblStatistics.columnCount()):
                    item = self.ui_statistics.tblStatistics.item(row, col)
                    row_data.append(item.text() if item else "")
                ws.append(row_data)
                
            wb.save(path)
            QMessageBox.information(self, "Thành công", f"Đã xuất file báo cáo Excel thành công tại:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file Excel: {e}")

    # --- BIỂU ĐỒ QTCHARTS (Dashboard + Statistics) ---
    def refactor_statistics_ui(self):
        """Tối ưu bố cục trang Thống kê: xếp dọc (KPI -> biểu đồ full-width -> bảng chi tiết),
        bảng canh số phải, xen màu, dòng thoáng. Chỉ chỉnh runtime, không đụng file .ui."""
        us = self.ui_statistics
        reports = us.layoutReports  # QHBox: [khối bảng | khối biểu đồ] -> chuyển sang dọc
        if reports.count() >= 2:
            reports.setDirection(QtWidgets.QBoxLayout.Direction.TopToBottom)
            reports.setSpacing(16)
            chart_item = reports.takeAt(1)   # khối biểu đồ đang ở cột phải
            reports.insertItem(0, chart_item)  # đưa lên trên, bảng xuống dưới -> đọc xu hướng trước

        # Biểu đồ full-width cần cao hơn để dễ đọc
        us.frameChart.setMinimumHeight(300)

        # Bảng chi tiết: chọn theo dòng, không sửa tay, xen màu, dòng thoáng
        tbl = us.tblStatistics
        tbl.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        tbl.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        tbl.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        tbl.setAlternatingRowColors(True)
        tbl.setStyleSheet(tbl.styleSheet() + "\nQTableWidget { alternate-background-color: #faf5ff; }")
        tbl.verticalHeader().setVisible(False)
        tbl.verticalHeader().setDefaultSectionSize(38)
        hh = tbl.horizontalHeader()
        hh.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)  # cột Tiêu đề co giãn
        for c in (0, 2, 3, 4, 5):
            hh.setSectionResizeMode(c, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def _format_stats_table(self):
        """Canh phải + phân tách nghìn cho các cột số của bảng thống kê."""
        tbl = self.ui_statistics.tblStatistics
        right = QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
        for r in range(tbl.rowCount()):
            for c in (3, 4, 5):  # Doanh thu, Số đơn, Sản phẩm đã bán
                it = tbl.item(r, c)
                if not it:
                    continue
                try:
                    it.setText(f"{float(it.text().replace(',', '').strip()):,.0f}")
                except ValueError:
                    pass
                it.setTextAlignment(right)

