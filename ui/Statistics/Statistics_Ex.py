import os
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from openpyxl import Workbook
from Ui_StatisticsWidget import Ui_StatisticsWidget  # Thay bằng tên file convert ui của bạn


class StatisticsEx(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_StatisticsWidget()
        self.ui.setupUi(self)

        # Giả lập database cục bộ để lưu trữ trạng thái dữ liệu (Không sửa hàm load data của bạn)
        self.data_store = []

        # Kết nối sự kiện click dòng trên TableView/TableWidget
        self.ui.tableWidget.itemClicked.connect(self.display_detail)

        # Kết nối các nút chức năng
        self.ui.btn_add.clicked.connect(self.add_data)
        self.ui.btn_edit.clicked.connect(self.save_data)  # Nút "Lưu lại" sau khi sửa
        self.ui.btn_delete.clicked.connect(self.delete_data)
        self.ui.btn_search.clicked.connect(self.search_data)
        self.ui.btn_refresh.clicked.connect(self.refresh_data)
        self.ui.btn_cancel.clicked.connect(self.clear_table)  # Nút "Hủy" để xóa sạch bảng
        self.ui.btn_excel.clicked.connect(self.export_excel)

        # Khởi tạo nạp dữ liệu gốc ban đầu
        self.refresh_data()

    def sync_data_from_table(self):
        """Đọc dữ liệu hiện tại từ Table để đồng bộ với bộ nhớ tạm data_store"""
        self.data_store = []
        row_count = self.ui.tableWidget.rowCount()
        col_count = self.ui.tableWidget.columnCount()
        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                item = self.ui.tableWidget.item(row, col)
                row_data.append(item.text() if item else "")
            self.data_store.append(row_data)

    def display_data_to_table(self, data_list):
        """Hàm nạp dữ liệu lên bảng (Giữ nguyên cơ chế đẩy data truyền thống của bạn)"""
        self.ui.tableWidget.setRowCount(0)
        for row_idx, row_data in enumerate(data_list):
            self.ui.tableWidget.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                self.ui.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def display_detail(self, item):
        """Khi click vào bất kỳ ô/hàng nào, hiển thị thông tin lên các LineEdit"""
        row = item.row()
        # Đọc dữ liệu từ hàng được chọn
        id_val = self.ui.tableWidget.item(row, 0).text() if self.ui.tableWidget.item(row, 0) else ""
        name_val = self.ui.tableWidget.item(row, 1).text() if self.ui.tableWidget.item(row, 1) else ""
        qty_val = self.ui.tableWidget.item(row, 2).text() if self.ui.tableWidget.item(row, 2) else ""
        price_val = self.ui.tableWidget.item(row, 3).text() if self.ui.tableWidget.item(row, 3) else ""

        # Đẩy dữ liệu vào các LineEdit tương ứng trong khung thông tin
        self.ui.txt_id.setText(id_val)
        self.ui.txt_name.setText(name_val)
        self.ui.txt_quantity.setText(qty_val)
        self.ui.txt_price.setText(price_val)

    def add_data(self):
        """Thêm mới dữ liệu từ các ô LineEdit vào bảng"""
        id_val = self.ui.txt_id.text().strip()
        name_val = self.ui.txt_name.text().strip()
        qty_val = self.ui.txt_quantity.text().strip()
        price_val = self.ui.txt_price.text().strip()

        if not id_val or not name_val:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ Mã và Tên sản phẩm!")
            return

        new_row = [id_val, name_val, qty_val, price_val]
        self.data_store.append(new_row)
        self.display_data_to_table(self.data_store)
        self.clear_inputs()

    def save_data(self):
        """Nút Lưu lại: cập nhật thông tin chỉnh sửa từ LineEdit xuống dòng đang chọn"""
        selected_items = self.ui.tableWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một hàng trong bảng để sửa đổi!")
            return

        row = selected_items[0].row()
        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(self.ui.txt_id.text()))
        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(self.ui.txt_name.text()))
        self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(self.ui.txt_quantity.text()))
        self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(self.ui.txt_price.text()))

        self.sync_data_from_table()
        QMessageBox.information(self, "Thành công", "Đã cập nhật dữ liệu sản phẩm!")

    def delete_data(self):
        """Xóa hàng dữ liệu đang được chọn"""
        selected_items = self.ui.tableWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn sản phẩm cần xóa!")
            return

        row = selected_items[0].row()
        self.ui.tableWidget.removeRow(row)
        self.sync_data_from_table()
        self.clear_inputs()

    def search_data(self):
        """Tìm kiếm gần đúng (Ví dụ: Nhập 'áo thun' tìm thấy 'áo thun cực chất')"""
        search_keyword = self.ui.txt_search.text().strip().lower()
        if not search_keyword:
            self.display_data_to_table(self.data_store)
            return

        filtered_data = []
        for row in self.data_store:
            # So sánh gần đúng tại cột Tên sản phẩm (cột chỉ số 1)
            if search_keyword in str(row[1]).lower():
                filtered_data.append(row)

        self.display_data_to_table(filtered_data)

    def refresh_data(self):
        """Làm mới dữ liệu để giải quyết tình trạng nghẽn mạch"""
        # Giả lập dữ liệu ban đầu phục vụ nạp lại
        self.data_store = [
            ["SP01", "Áo thun cực chất", "50", "150000"],
            ["SP02", "Quần jean baggy", "30", "290000"],
            ["SP03", "Áo khoác dù", "20", "350000"]
        ]
        self.display_data_to_table(self.data_store)
        self.clear_inputs()

    def clear_table(self):
        """Nút Hủy: Xóa sạch toàn bộ dữ liệu khỏi bảng"""
        self.ui.tableWidget.setRowCount(0)
        self.data_store = []
        self.clear_inputs()

    def export_excel(self):
        """Xuất dữ liệu trên bảng hiện tại ra file Excel sử dụng OpenPyXL"""
        wb = Workbook()
        ws = wb.active
        ws.title = "ThongKe_SanPham"

        # Ghi Header
        headers = ["Mã sản phẩm", "Tên sản phẩm", "Số lượng", "Đơn giá"]
        ws.append(headers)

        # Ghi các dòng dữ liệu hiện tại trên bảng
        row_count = self.ui.tableWidget.rowCount()
        for row in range(row_count):
            row_data = []
            for col in range(self.ui.tableWidget.columnCount()):
                item = self.ui.tableWidget.item(row, col)
                row_data.append(item.text() if item else "")
            ws.append(row_data)

        file_path = "ThongKe_Export.xlsx"
        wb.save(file_path)
        QMessageBox.information(self, "Thành công", f"Đã xuất file Excel thành công tại: {os.path.abspath(file_path)}")

    def clear_inputs(self):
        """Xóa văn bản trên các khung LineEdit"""
        self.ui.txt_id.clear()
        self.ui.txt_name.clear()
        self.ui.txt_quantity.clear()
        self.ui.txt_price.clear()