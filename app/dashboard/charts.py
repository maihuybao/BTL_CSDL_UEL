"""ChartsMixin: dựng và cập nhật biểu đồ QtCharts cho Dashboard + Thống kê."""
import sqlite3

from PyQt6 import QtWidgets, QtGui, QtCore

from app.config import DB_PATH, HAS_QTCHARTS
if HAS_QTCHARTS:
    from app.config import (QChart, QChartView, QBarSeries, QBarSet,
                            QBarCategoryAxis, QValueAxis, QPieSeries)


class ChartsMixin:
    def setup_charts_area(self):
        """Chuẩn bị QChartView gắn vào các frame có sẵn; thiếu PyQt6-Charts thì để nguyên placeholder."""
        self._chart_views = {}
        if not HAS_QTCHARTS:
            for lbl in (getattr(self.ui, 'lblChart1Placeholder', None),
                        getattr(self.ui, 'lblChart2Placeholder', None),
                        getattr(self.ui_statistics, 'lblChartPlaceholder', None)):
                if lbl:
                    lbl.setText("Cài PyQt6-Charts để xem biểu đồ: pip install PyQt6-Charts")
            return

        def make_view(layout, placeholder, max_height=None):
            if placeholder:
                placeholder.hide()
            view = QChartView()
            view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            view.setMinimumHeight(180)
            if max_height:
                view.setMaximumHeight(max_height)
            layout.addWidget(view)
            return view

        # Dashboard: bar doanh thu + pie số đơn — giãn lấp đầy card (không giới hạn cao, tránh khoảng trắng khi phóng to)
        self._chart_views['dash_revenue'] = make_view(self.ui.verticalLayout_chart1, self.ui.lblChart1Placeholder)
        self._chart_views['dash_orders'] = make_view(self.ui.verticalLayout_chart2, self.ui.lblChart2Placeholder)

        # Statistics: bar doanh thu theo livestream + pie doanh thu theo sản phẩm (đặt cạnh nhau)
        stats_row = QtWidgets.QHBoxLayout()
        self.ui_statistics.verticalLayout_innerChart.addLayout(stats_row)
        self._chart_views['stats_bar'] = make_view(stats_row, self.ui_statistics.lblChartPlaceholder)
        self._chart_views['stats_pie'] = make_view(stats_row, None)

    def _set_chart(self, key, chart):
        view = self._chart_views.get(key)
        if view:
            old = view.chart()
            view.setChart(chart)
            if old is not None:
                old.deleteLater()

    @staticmethod
    def _make_bar_chart(title, categories, values, series_label):
        if not values:
            categories, values = ["(chưa có dữ liệu)"], [0]
        values = [float(v or 0) for v in values]
        bar_set = QBarSet(series_label)
        for v in values:
            bar_set.append(v)
        series = QBarSeries()
        series.append(bar_set)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, QtCore.Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        axis_y = QValueAxis()
        axis_y.setRange(0, max(values) * 1.1 or 1)
        chart.addAxis(axis_y, QtCore.Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        chart.legend().setVisible(False)
        chart.setMargins(QtCore.QMargins(4, 4, 4, 4))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        return chart

    @staticmethod
    def _make_pie_chart(title, pairs):
        series = QPieSeries()
        for label, value in pairs:
            if value:
                series.append(f"{label} ({value:g})", value)
        series.setLabelsVisible(True)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        chart.setMargins(QtCore.QMargins(4, 4, 4, 4))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        return chart

    def update_all_charts(self):
        """Biểu đồ Dashboard: bar doanh thu theo tháng + pie số đơn theo trạng thái."""
        if not HAS_QTCHARTS:
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Doanh thu theo tháng từ hóa đơn đã thanh toán
            cursor.execute("""
                SELECT strftime('%Y-%m', ThoiGianLap) AS Thang, SUM(TongTien)
                FROM HOA_DON WHERE TrangThaiHD = 'Đã thanh toán' AND ThoiGianLap IS NOT NULL
                GROUP BY Thang ORDER BY Thang
            """)
            rows = cursor.fetchall()
            self._set_chart('dash_revenue', self._make_bar_chart(
                "Doanh thu theo tháng (VND)", [r[0] or "?" for r in rows], [r[1] or 0 for r in rows], "Doanh thu"))

            # Số đơn theo trạng thái
            cursor.execute("SELECT TrangThaiDH, COUNT(*) FROM DON_HANG GROUP BY TrangThaiDH")
            self._set_chart('dash_orders', self._make_pie_chart(
                "Số đơn hàng theo trạng thái", cursor.fetchall()))
            conn.close()
        except Exception as e:
            print(f"Lỗi vẽ biểu đồ dashboard: {e}")

    def update_statistics_charts(self, stat_rows, start_date=None, end_date=None):
        """Biểu đồ Statistics: bar doanh thu theo livestream + pie doanh thu theo sản phẩm."""
        if not HAS_QTCHARTS:
            return
        try:
            suffix = f" ({start_date} → {end_date})" if start_date and end_date else ""
            self._set_chart('stats_bar', self._make_bar_chart(
                "Doanh thu theo livestream" + suffix,
                [r[0] for r in stat_rows], [r[3] or 0 for r in stat_rows], "Doanh thu"))

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            params = []
            date_cond = ""
            if start_date and end_date:
                date_cond = " AND dh.NgayDat BETWEEN ? AND ?"
                params = [start_date + " 00:00:00", end_date + " 23:59:59"]
            cursor.execute(f"""
                SELECT p.TenSP, SUM(ct.ThanhTien)
                FROM CHI_TIET_DON_HANG ct
                JOIN SAN_PHAM p ON ct.MaSP = p.MaSP
                JOIN DON_HANG dh ON ct.MaDonHang = dh.MaDonHang
                WHERE dh.TrangThaiDH != 'Đã hủy'{date_cond}
                GROUP BY p.MaSP ORDER BY 2 DESC
            """, params)
            self._set_chart('stats_pie', self._make_pie_chart(
                "Tỷ trọng doanh thu theo sản phẩm" + suffix, cursor.fetchall()))
            conn.close()
        except Exception as e:
            print(f"Lỗi vẽ biểu đồ thống kê: {e}")

    # --- HÀM TRUY CẬP ẢNH SẢN PHẨM ---
