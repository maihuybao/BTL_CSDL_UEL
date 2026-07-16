import sys
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox

# Nhập lớp giao diện được tạo tự động từ file Payment.ui của bạn
from Payment import Ui_PaymentWidget


class PaymentEx(QtWidgets.QWidget, Ui_PaymentWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # --- CẤU HÌNH BẢNG TỰ ĐỘNG BẮT LỰA CHỌN DÒNG ---
        self.tblPayment.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblPayment.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblPayment.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # Dữ liệu giả lập danh mục Đơn hàng nạp vào ComboBox
        self.list_orders = ["DH001", "DH002", "DH003", "DH004"]
        self.cbDonHang.addItems(self.list_orders)

        # Dữ liệu giả lập danh sách Thanh toán ban đầu
        self.data_payments = [
            {"pay_id": "GD001", "order_id": "DH001", "date": "2026-07-15 08:30:00", "amount": 470000,
             "method": "Chuyển khoản", "status": "Đã thanh toán"},
            {"pay_id": "GD002", "order_id": "DH002", "date": "2026-07-15 09:15:00", "amount": 250000,
             "method": "Tiền mặt", "status": "Đã thanh toán"},
            {"pay_id": "GD003", "order_id": "DH003", "date": "2026-07-15 10:00:00", "amount": 1200000,
             "method": "Ví điện tử", "status": "Chưa thanh toán"}
        ]

        # Biến quản lý trạng thái thao tác: None, "THEM", hoặc "SUA"
        self.current_action = None

        # Kết nối sự kiện tương tác của các nút bấm chức năng
        self.btnSearch.clicked.connect(self.action_search)
        self.btnRefresh.clicked.connect(self.action_refresh)
        self.btnThem.clicked.connect(self.action_them)
        self.btnSua.clicked.connect(self.action_sua)
        self.btnXoa.clicked.connect(self.action_xoa)
        self.btnLuu.clicked.connect(self.action_luu)
        self.btnHuy.clicked.connect(self.action_huy)
        self.btnXuatExcel.clicked.connect(self.action_xuat_excel)

        # Sự kiện click chọn dòng trên TableWidget tự động nhảy thông tin lên Form nhập liệu
        self.tblPayment.itemSelectionChanged.connect(self.sync_table_to_form)

        # Đặt thời gian mặc định cho ô QDateTimeEdit là thời gian hiện tại
        self.dateThanhToan.setDateTime(QtCore.QDateTime.currentDateTime())

        # Tải dữ liệu mặc định hiển thị lên bảng và tạm khóa Form nhập liệu ban đầu
        self.load_data_to_table(self.data_payments)
        self.set_form_enabled(False)

    def load_data_to_table(self, data_list):
        """Hiển thị danh sách giao dịch thanh toán lên QTableWidget"""
        self.tblPayment.setRowCount(0)
        for row_idx, row_data in enumerate(data_list):
            self.tblPayment.insertRow(row_idx)
            self.tblPayment.setItem(row_idx, 0, QTableWidgetItem(row_data["pay_id"]))
            self.tblPayment.setItem(row_idx, 1, QTableWidgetItem(row_data["order_id"]))
            self.tblPayment.setItem(row_idx, 2, QTableWidgetItem(row_data["date"]))
            self.tblPayment.setItem(row_idx, 3, QTableWidgetItem(f"{row_data['amount']:,}"))
            self.tblPayment.setItem(row_idx, 4, QTableWidgetItem(row_data["method"]))
            self.tblPayment.setItem(row_idx, 5, QTableWidgetItem(row_data["status"]))

        # Tự co giãn các cột dữ liệu theo kích thước hiển thị của màn hình
        self.tblPayment.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def set_form_enabled(self, enabled=True):
        """Đóng/Mở trạng thái chỉnh sửa các ô nhập liệu tùy thuộc hành động"""
        self.cbDonHang.setEnabled(enabled)
        self.dateThanhToan.setEnabled(enabled)
        self.txtSoTien.setEnabled(enabled)
        self.cbPhuongThuc.setEnabled(enabled)
        self.cbTrangThai.setEnabled(enabled)

        # Khóa/Mở các nút chức năng tương ứng để ngăn ngừa xung đột dữ liệu
        self.btnThem.setEnabled(not enabled)
        self.btnSua.setEnabled(not enabled)
        self.btnXoa.setEnabled(not enabled)
        self.btnLuu.setEnabled(enabled)
        self.btnHuy.setEnabled(enabled)

    def sync_table_to_form(self):
        """Khi click chọn dòng trên bảng, đổ thông tin tương ứng sang khung bên cạnh"""
        if self.current_action is not None:
            return  # Đang trong trạng thái Thêm/Sửa thì không tự động chuyển dòng khi click bảng

        selected_rows = self.tblPayment.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        order_id = self.tblPayment.item(row, 1).text()
        date_str = self.tblPayment.item(row, 2).text()
        amount = self.tblPayment.item(row, 3).text().replace(",", "")
        method = self.tblPayment.item(row, 4).text()
        status = self.tblPayment.item(row, 5).text()

        # Chọn item tương ứng trên Form
        self.cbDonHang.setCurrentText(order_id)

        q_datetime = QtCore.QDateTime.fromString(date_str, "yyyy-MM-dd HH:mm:ss")
        if q_datetime.isValid():
            self.dateThanhToan.setDateTime(q_datetime)

        self.txtSoTien.setText(amount)
        self.cbPhuongThuc.setCurrentText(method)
        self.cbTrangThai.setCurrentText(status)

    def clear_form(self):
        """Xóa dữ liệu cũ trên form về mặc định để chuẩn bị thao tác mới"""
        if self.cbDonHang.count() > 0: self.cbDonHang.setCurrentIndex(0)
        self.dateThanhToan.setDateTime(QtCore.QDateTime.currentDateTime())
        self.txtSoTien.clear()
        self.cbPhuongThuc.setCurrentIndex(0)
        self.cbTrangThai.setCurrentIndex(0)

    # --- ĐỊNH NGHĨA CÁC HÀM XỬ LÝ SỰ KIỆN NÚT BẤM ---

    def action_search(self):
        """Tìm kiếm giao dịch theo Mã Đơn Hàng hoặc Phương Thức"""
        search_text = self.txtSearch.text().strip().lower()
        if not search_text:
            self.load_data_to_table(self.data_payments)
            return

        filtered_data = [
            item for item in self.data_payments
            if search_text in item["order_id"].lower() or search_text in item["method"].lower()
        ]
        self.load_data_to_table(filtered_data)
        self.lblStatus.setText(f"Trạng thái: Đã tìm thấy {len(filtered_data)} kết quả giao dịch.")

    def action_refresh(self):
        """Làm mới ô tìm kiếm và đặt danh sách bảng về trạng thái mặc định"""
        self.txtSearch.clear()
        self.load_data_to_table(self.data_payments)
        self.lblStatus.setText("Trạng thái: Đã làm mới danh sách thanh toán.")

    def action_them(self):
        """Kích hoạt trạng thái thêm mới giao dịch thanh toán"""
        self.current_action = "THEM"
        self.clear_form()
        self.set_form_enabled(True)
        self.txtSoTien.setFocus()
        self.lblStatus.setText("Trạng thái: Đang nhập mới thông tin giao dịch...")

    def action_sua(self):
        """Kích hoạt trạng thái sửa đổi thông tin giao dịch đang chọn"""
        selected_rows = self.tblPayment.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một giao dịch trên bảng để sửa!")
            return

        self.current_action = "SUA"
        self.set_form_enabled(True)
        self.lblStatus.setText("Trạng thái: Đang chỉnh sửa thông tin giao dịch thanh toán...")

    def action_xoa(self):
        """Xóa bỏ bản ghi giao dịch thanh toán đang được lựa chọn"""
        selected_rows = self.tblPayment.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một giao dịch trên bảng để xóa!")
            return

        row = selected_rows[0].row()
        pay_id = self.tblPayment.item(row, 0).text()

        confirm = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa mã giao dịch {pay_id} không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.data_payments = [item for item in self.data_payments if item["pay_id"] != pay_id]
            self.load_data_to_table(self.data_payments)
            self.clear_form()
            self.lblStatus.setText(f"Trạng thái: Đã xóa thành công mã giao dịch {pay_id}")

    def action_luu(self):
        """Lưu trữ thông tin dữ liệu sau khi nhấn Thêm mới hoặc Chỉnh sửa"""
        order_id = self.cbDonHang.currentText()
        date_str = self.dateThanhToan.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        method = self.cbPhuongThuc.currentText()
        status = self.cbTrangThai.currentText()

        try:
            amount_text = self.txtSoTien.text().replace(",", "").strip()
            amount = int(amount_text) if amount_text else 0
        except ValueError:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Số tiền thanh toán phải là số nguyên hợp lệ!")
            return

        if amount <= 0:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Số tiền thanh toán phải lớn hơn 0!")
            return

        if self.current_action == "THEM":
            # Tự động sinh mã giao dịch tăng tiến tiếp theo
            new_id = f"GD{len(self.data_payments) + 1:03d}"
            new_item = {
                "pay_id": new_id,
                "order_id": order_id,
                "date": date_str,
                "amount": amount,
                "method": method,
                "status": status
            }
            self.data_payments.append(new_item)
            self.lblStatus.setText(f"Trạng thái: Thêm mới thành công giao dịch {new_id}")

        elif self.current_action == "SUA":
            selected_rows = self.tblPayment.selectionModel().selectedRows()
            row = selected_rows[0].row()
            pay_id = self.tblPayment.item(row, 0).text()

            # Tiến hành cập nhật thông tin chỉnh sửa vào mảng dữ liệu
            for item in self.data_payments:
                if item["pay_id"] == pay_id:
                    item["order_id"] = order_id
                    item["date"] = date_str
                    item["amount"] = amount
                    item["method"] = method
                    item["status"] = status
                    break
            self.lblStatus.setText(f"Trạng thái: Đã cập nhật thành công giao dịch {pay_id}")

        self.load_data_to_table(self.data_payments)
        self.current_action = None
        self.set_form_enabled(False)

    def action_huy(self):
        """Hủy bỏ thao tác hiện tại"""
        self.current_action = None
        self.clear_form()
        self.set_form_enabled(False)
        self.sync_table_to_form()
        self.lblStatus.setText("Trạng thái: Đã hủy bỏ thao tác nghiệp vụ.")

    def action_xuat_excel(self):
        """Kết xuất cấu trúc dữ liệu của bảng thanh toán ra file CSV tiện ích"""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Lưu file dữ liệu báo cáo", "", "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8-sig') as f:
                    # Ghi dòng tiêu đề cột dữ liệu
                    headers = ["Mã Giao Dịch", "Mã Đơn Hàng", "Ngày Thanh Toán", "Số Tiền (VND)", "Phương Thức",
                               "Trạng Thái"]
                    f.write(",".join(headers) + "\n")
                    # Ghi nội dung chi tiết của từng bản ghi dữ liệu
                    for item in self.data_payments:
                        row_str = f"{item['pay_id']},{item['order_id']},{item['date']},{item['amount']},{item['method']},{item['status']}"
                        f.write(row_str + "\n")
                QMessageBox.information(self, "Xuất dữ liệu", f"Đã kết xuất dữ liệu thành công tại đường dẫn:\n{path}")
                self.lblStatus.setText("Trạng thái: Xuất file báo cáo thành công.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể lưu trữ tệp tin: {str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PaymentEx()
    window.show()
    sys.exit(app.exec())