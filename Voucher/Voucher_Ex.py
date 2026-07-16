import os
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox
from openpyxl import Workbook
from Voucher import Ui_VoucherWidget  # Thay bằng tên file convert ui của bạn


class VoucherEx(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_VoucherWidget()
        self.ui.setupUi(self)

        self.data_store = []

        # Kết nối sự kiện tương tác bảng dữ liệu
        self.ui.tableWidget.itemClicked.connect(self.display_detail)

        # Kết nối các nút bấm chức năng
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
        v_code = self.ui.tableWidget.item(row, 0).text() if self.ui.tableWidget.item(row, 0) else ""
        v_name = self.ui.tableWidget.item(row, 1).text() if self.ui.tableWidget.item(row, 1) else ""
        v_discount = self.ui.tableWidget.item(row, 2).text() if self.ui.tableWidget.item(row, 2) else ""
        v_condition = self.ui.tableWidget.item(row, 3).text() if self.ui.tableWidget.item(row, 3) else ""

        self.ui.txt_voucher_code.setText(v_code)
        self.ui.txt_voucher_name.setText(v_name)
        self.ui.txt_discount.setText(v_discount)
        self.ui.txt_condition.setText(v_condition)

    def add_data(self):
        v_code = self.ui.txt_voucher_code.text().strip()
        v_name = self.ui.txt_voucher_name.text().strip()
        v_discount = self.ui.txt_discount.text().strip()
        v_condition = self.ui.txt_condition.text().strip()

        if not v_code or not v_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Mã và Tên voucher!")
            return

        new_voucher = [v_code, v_name, v_discount, v_condition]
        self.data_store.append(new_voucher)
        self.display_data_to_table(self.data_store)
        self.clear_inputs()

    def save_data(self):
        selected_items = self.ui.tableWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn dòng voucher để sửa đổi!")
            return

        row = selected_items[0].row()
        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(self.ui.txt_voucher_code.text()))
        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(self.ui.txt_voucher_name.text()))
        self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(self.ui.txt_discount.text()))
        self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(self.ui.txt_condition.text()))

        self.sync_data_from_table()
        QMessageBox.information(self, "Thành công", "Đã cập nhật dữ liệu voucher!")

    def delete_data(self):
        selected_items = self.ui.tableWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn dòng voucher cần xóa!")
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
            # Tìm kiếm gần đúng dựa theo tên voucher (cột 1)
            if search_keyword in str(row[1]).lower():
                filtered_data.append(row)

        self.display_data_to_table(filtered_data)

    def refresh_data(self):
        self.data_store = [
            ["VOUCHER10", "Giảm giá hè rực rỡ", "10%", "Đơn từ 200k"],
            ["VOUCHER50", "Siêu sale cuối năm", "50%", "Đơn từ 500k"]
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
        ws.title = "DanhSach_Voucher"

        headers = ["Mã Voucher", "Tên Chương Trình", "Mức Giảm Giá", "Điều Kiện"]
        ws.append(headers)

        for row in range(self.ui.tableWidget.rowCount()):
            row_data = []
            for col in range(self.ui.tableWidget.columnCount()):
                item = self.ui.tableWidget.item(row, col)
                row_data.append(item.text() if item else "")
            ws.append(row_data)

        file_path = "Voucher_Export.xlsx"
        wb.save(file_path)
        QMessageBox.information(self, "Thành công", f"Đã xuất file Excel tại: {os.path.abspath(file_path)}")

    def clear_inputs(self):
        self.ui.txt_voucher_code.clear()
        self.ui.txt_voucher_name.clear()
        self.ui.txt_discount.clear()
        self.ui.txt_condition.clear()