import sys
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox

# Nhập class giao diện được tạo tự động từ file Customer.ui của bạn
from Customer import Ui_CustomerWidget


class CustomerEx(QtWidgets.QWidget, Ui_CustomerWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # --- CẤU HÌNH BẢNG TỰ ĐỘNG BẮT LỰA CHỌN DÒNG ---
        self.tblKhachHang.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblKhachHang.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblKhachHang.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # Dữ liệu giả lập khách hàng ban đầu
        self.data_customers = [
            {"cust_id": "KH001", "name": "Nguyễn Hoàng Nam", "phone": "0901234567", "email": "nam.nh@gmail.com", "address": "Quận 1, TP. HCM", "join_date": "2026-01-10", "note": "Khách VIP"},
            {"cust_id": "KH002", "name": "Trần Thu Thủy", "phone": "0987654321", "email": "thuy.tt@gmail.com", "address": "Quận Cầu Giấy, Hà Nội", "join_date": "2026-03-15", "note": "Ưu tiên giao hàng nhanh"},
            {"cust_id": "KH003", "name": "Lê Kiều Trang", "phone": "0912345678", "email": "trang.lk@gmail.com", "address": "Quận Hải Châu, Đà Nẵng", "join_date": "2026-05-20", "note": ""}
        ]

        # Biến quản lý trạng thái thao tác: None, "THEM", hoặc "SUA"
        self.current_action = None

        # Cài đặt ngày mặc định
        self.dateNgayThamGia.setDate(QtCore.QDate.currentDate())

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
        self.tblKhachHang.itemSelectionChanged.connect(self.sync_table_to_form)

        # Tải dữ liệu mặc định hiển thị lên bảng và tạm khóa Form nhập liệu ban đầu
        self.load_data_to_table(self.data_customers)
        self.set_form_enabled(False)

    def load_data_to_table(self, data_list):
        """Hiển thị danh sách khách hàng lên QTableWidget"""
        self.tblKhachHang.setRowCount(0)
        for row_idx, row_data in enumerate(data_list):
            self.tblKhachHang.insertRow(row_idx)
            self.tblKhachHang.setItem(row_idx, 0, QTableWidgetItem(row_data["cust_id"]))
            self.tblKhachHang.setItem(row_idx, 1, QTableWidgetItem(row_data["name"]))
            self.tblKhachHang.setItem(row_idx, 2, QTableWidgetItem(row_data["phone"]))
            self.tblKhachHang.setItem(row_idx, 3, QTableWidgetItem(row_data["email"]))
            self.tblKhachHang.setItem(row_idx, 4, QTableWidgetItem(row_data["address"]))
            self.tblKhachHang.setItem(row_idx, 5, QTableWidgetItem(row_data["join_date"]))

        # Tự co giãn các cột dữ liệu theo kích thước hiển thị của màn hình
        self.tblKhachHang.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def set_form_enabled(self, enabled=True):
        """Đóng/Mở trạng thái chỉnh sửa các ô nhập liệu bên trái tùy thuộc hành động"""
        self.txtTenKhachHang.setEnabled(enabled)
        self.txtSoDienThoai.setEnabled(enabled)
        self.txtEmail.setEnabled(enabled)
        self.txtDiaChi.setEnabled(enabled)
        self.dateNgayThamGia.setEnabled(enabled)
        self.txtGhiChu.setEnabled(enabled)

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

        selected_rows = self.tblKhachHang.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        cust_id = self.tblKhachHang.item(row, 0).text()

        # Tìm đối tượng trong data gốc để lấy thêm cả trường Ghi chú (Note)
        customer = next((item for item in self.data_customers if item["cust_id"] == cust_id), None)
        if customer:
            self.txtTenKhachHang.setText(customer["name"])
            self.txtSoDienThoai.setText(customer["phone"])
            self.txtEmail.setText(customer["email"])
            self.txtDiaChi.setText(customer["address"])
            self.txtGhiChu.setText(customer["note"])

            dt = QtCore.QDate.fromString(customer["join_date"], "yyyy-MM-dd")
            if dt.isValid():
                self.dateNgayThamGia.setDate(dt)

    def clear_form(self):
        """Xóa trắng thông tin trên form để chuẩn bị nhập dữ liệu mới"""
        self.txtTenKhachHang.clear()
        self.txtSoDienThoai.clear()
        self.txtEmail.clear()
        self.txtDiaChi.clear()
        self.txtGhiChu.clear()
        self.dateNgayThamGia.setDate(QtCore.QDate.currentDate())

    # --- ĐỊNH NGHĨA CÁC HÀM XỬ LÝ SỰ KIỆN NÚT BẤM ---

    def action_search(self):
        """Tìm kiếm khách hàng theo Tên hoặc Số điện thoại"""
        search_text = self.txtSearch.text().strip().lower()
        if not search_text:
            self.load_data_to_table(self.data_customers)
            return

        filtered_data = [
            item for item in self.data_customers
            if search_text in item["name"].lower() or search_text in item["phone"]
        ]
        self.load_data_to_table(filtered_data)
        self.lblStatus.setText(f"Trạng thái: Đã tìm thấy {len(filtered_data)} kết quả phù hợp.")

    def action_refresh(self):
        """Làm mới ô tìm kiếm và đặt danh sách bảng về dữ liệu mặc định"""
        self.txtSearch.clear()
        self.load_data_to_table(self.data_customers)
        self.lblStatus.setText("Trạng thái: Đã làm mới danh sách khách hàng.")

    def action_them(self):
        """Kích hoạt trạng thái thêm mới khách hàng"""
        self.current_action = "THEM"
        self.clear_form()
        self.set_form_enabled(True)
        self.txtTenKhachHang.setFocus()
        self.lblStatus.setText("Trạng thái: Đang nhập mới thông tin khách hàng...")

    def action_sua(self):
        """Kích hoạt trạng thái sửa đổi thông tin khách hàng đang chọn"""
        selected_rows = self.tblKhachHang.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một khách hàng trên bảng để sửa!")
            return

        self.current_action = "SUA"
        self.set_form_enabled(True)
        self.lblStatus.setText("Trạng thái: Đang chỉnh sửa thông tin bản ghi...")

    def action_xoa(self):
        """Xóa bỏ bản ghi khách hàng đang được lựa chọn"""
        selected_rows = self.tblKhachHang.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một khách hàng trên bảng để xóa!")
            return

        row = selected_rows[0].row()
        cust_id = self.tblKhachHang.item(row, 0).text()
        cust_name = self.tblKhachHang.item(row, 1).text()

        confirm = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa khách hàng {cust_name} ({cust_id}) không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.data_customers = [item for item in self.data_customers if item["cust_id"] != cust_id]
            self.load_data_to_table(self.data_customers)
            self.clear_form()
            self.lblStatus.setText(f"Trạng thái: Đã xóa thành công khách hàng {cust_id}")

    def action_luu(self):
        """Lưu trữ thông tin dữ liệu sau khi nhấn Thêm mới hoặc Chỉnh sửa"""
        name = self.txtTenKhachHang.text().strip()
        phone = self.txtSoDienThoai.text().strip()
        email = self.txtEmail.text().strip()
        address = self.txtDiaChi.text().strip()
        note = self.txtGhiChu.text().strip()
        join_date_str = self.dateNgayThamGia.date().toString("yyyy-MM-dd")

        # Kiểm tra điều kiện dữ liệu bắt buộc không được bỏ trống
        if not name or not phone:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Tên khách hàng và Số điện thoại không được để trống!")
            return

        if self.current_action == "THEM":
            # Tự động tạo mã ID khách hàng tăng tiến tiếp theo
            new_id = f"KH{len(self.data_customers) + 1:03d}"
            new_item = {
                "cust_id": new_id,
                "name": name,
                "phone": phone,
                "email": email,
                "address": address,
                "join_date": join_date_str,
                "note": note
            }
            self.data_customers.append(new_item)
            self.lblStatus.setText(f"Trạng thái: Thêm mới thành công khách hàng {new_id}")

        elif self.current_action == "SUA":
            selected_rows = self.tblKhachHang.selectionModel().selectedRows()
            row = selected_rows[0].row()
            cust_id = self.tblKhachHang.item(row, 0).text()

            # Tiến hành cập nhật thông tin chỉnh sửa vào mảng cấu trúc dữ liệu
            for item in self.data_customers:
                if item["cust_id"] == cust_id:
                    item["name"] = name
                    item["phone"] = phone
                    item["email"] = email
                    item["address"] = address
                    item["join_date"] = join_date_str
                    item["note"] = note
                    break
            self.lblStatus.setText(f"Trạng thái: Đã cập nhật thành công thông tin khách hàng {cust_id}")

        self.load_data_to_table(self.data_customers)
        self.current_action = None
        self.set_form_enabled(False)

    def action_huy(self):
        """Hủy bỏ tiến trình hành động hiện tại"""
        self.current_action = None
        self.clear_form()
        self.set_form_enabled(False)
        self.sync_table_to_form()
        self.lblStatus.setText("Trạng thái: Đã hủy bỏ thao tác nghiệp vụ.")

    def action_xuat_excel(self):
        """Kết xuất cấu trúc dữ liệu của bảng khách hàng hiện tại ra file CSV tiện ích"""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Lưu file dữ liệu báo cáo", "", "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8-sig') as f:
                    # Ghi dòng tiêu đề cột dữ liệu
                    headers = ["Mã Khách Hàng", "Tên Khách Hàng", "Số Điện Thoại", "Email", "Địa Chỉ", "Ngày Tham Gia", "Ghi Chú"]
                    f.write(",".join(headers) + "\n")
                    # Ghi nội dung chi tiết của từng bản ghi dữ liệu
                    for item in self.data_customers:
                        row_str = f"{item['cust_id']},{item['name']},{item['phone']},{item['email']},{item['address']},{item['join_date']},{item['note']}"
                        f.write(row_str + "\n")
                QMessageBox.information(self, "Xuất dữ liệu", f"Đã kết xuất dữ liệu thành công tại đường dẫn:\n{path}")
                self.lblStatus.setText("Trạng thái: Xuất file báo cáo thành công.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể lưu trữ tệp tin: {str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CustomerEx()
    window.show()
    sys.exit(app.exec())