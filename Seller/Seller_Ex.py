import os
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from openpyxl import Workbook
from Seller import Ui_SellerWidget


class SellerEx(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SellerWidget()
        self.ui.setupUi(self)

        self.data_store = []

        # Bắt sự kiện nhấn vào bất kỳ thuộc tính nào (tên, sđt,...) của người bán đều đẩy thông tin ra LineEdit
        self.ui.tableWidget.itemClicked.connect(self.display_detail)

        # Kết nối các nút xử lý
        self.ui.btn_add.clicked.connect(self.add_data)
        self.ui.btn_edit.clicked.connect(self.save_data)
        self.ui.btn_delete.clicked.connect(self.delete_data)
        self.ui.btn_search.clicked.connect(self.search_data)
        self.ui.btn_refresh.clicked.connect(self.refresh_data)
        self.ui.btn_cancel.clicked.connect(self.clear_table)
        self.ui.btn_excel.clicked.connect(self.export_excel)

        self.refresh_data()

    def sync_data_from_table(self):
        self.data_store = []
        for row in range(self.ui.tableWidget.rowCount()):
            row_data = []
            for col in range(self.ui.tableWidget.columnCount()):
                item = self.ui.tableWidget.item(row, col)
                row_data.append(item.text() if item else "")
            self.data_store.append(row_data)

    def display_data_to_table(self, data_list):
        self.ui.tableWidget.setRowCount(0)
        for row_idx, row_data in enumerate(data_list):
            self.ui.tableWidget.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                self.ui.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def display_detail(self, item):
        row = item.row()
        s_id = self.ui.tableWidget.item(row, 0).text() if self.ui.tableWidget.item(row, 0) else ""
        s_name = self.ui.tableWidget.item(row, 1).text() if self.ui.tableWidget.item(row, 1) else ""
        s_phone = self.ui.tableWidget.item(row, 2).text() if self.ui.tableWidget.item(row, 2) else ""
        s_address = self.ui.tableWidget.item(row, 3).text() if self.ui.tableWidget.item(row, 3) else ""

        self.ui.txt_seller_id.setText(s_id)
        self.ui.txt_seller_name.setText(s_name)
        self.ui.txt_seller_phone.setText(s_phone)
        self.ui.txt_seller_address.setText(s_address)

    def add_data(self):
        s_id = self.ui.txt_seller_id.text().strip()
        s_name = self.ui.txt_seller_name.text().strip()
        s_phone = self.ui.txt_seller_phone.text().strip()
        s_address = self.ui.txt_seller_address.text().strip()

        if not s_id or not s_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin Mã và Tên người bán!")
            return

        new_seller = [s_id, s_name, s_phone, s_address]
        self.data_store.append(new_seller)
        self.display_data_to_table(self.data_store)
        self.clear_inputs()

    def save_data(self):
        selected_items = self.ui.tableWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn người bán trên bảng để sửa!")
            return

        row = selected_items[0].row()
        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(self.ui.txt_seller_id.text()))
        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(self.ui.txt_seller_name.text()))
        self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(self.ui.txt_seller_phone.text()))
        self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(self.ui.txt_seller_address.text()))

        self.sync_data_from_table()
        QMessageBox.information(self, "Thành công", "Đã cập nhật hồ sơ người bán!")

    def delete_data(self):
        selected_items = self.ui.tableWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn hàng cần xóa khỏi cơ sở dữ liệu!")
            return

        row = selected_items[0].row()
        self.ui.tableWidget.removeRow(row)
        self.sync_data_from_table()
        self.clear_inputs()

    def search_data(self):
        search_keyword = self.ui.txt_search.text().strip().lower()
        if not search_keyword:
            self.display_data_to_table(self.data_store)
            return

        filtered_data = []
        for row in self.data_store:
            # Tìm kiếm gần đúng dựa trên Tên đối tác/Người bán (cột 1)
            if search_keyword in str(row[1]).lower():
                filtered_data.append(row)

        self.display_data_to_table(filtered_data)

    def refresh_data(self):
        self.data_store = [
            ["NB01", "Nguyễn Văn A", "0901234567", "Hà Nội"],
            ["NB02", "Trần Thị B", "0987654321", "TP. Hồ Chí Minh"]
        ]
        self.display_data_to_table(self.data_store)
        self.clear_inputs()

    def clear_table(self):
        self.ui.tableWidget.setRowCount(0)
        self.data_store = []
        self.clear_inputs()

    def export_excel(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "NguoiBan_Data"

        headers = ["Mã đối tác", "Tên người bán", "Số điện thoại", "Địa chỉ"]
        ws.append(headers)

        for row in range(self.ui.tableWidget.rowCount()):
            row_data = []
            for col in range(self.ui.tableWidget.columnCount()):
                item = self.ui.tableWidget.item(row, col)
                row_data.append(item.text() if item else "")
            ws.append(row_data)

        file_path = "Seller_Export.xlsx"
        wb.save(file_path)
        QMessageBox.information(self, "Thành công",
                                f"Đã xuất dữ liệu Excel thành công tại: {os.path.abspath(file_path)}")

    def clear_inputs(self):
        self.ui.txt_seller_id.clear()
        self.ui.txt_seller_name.clear()
        self.ui.txt_seller_phone.clear()
        self.ui.txt_seller_address.clear()