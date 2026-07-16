import sys
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox

# Nhập class giao diện từ file Order.py (đã được biên dịch từ file UI của bạn)
from Order import Ui_OrderWidget


class OrderEx(QtWidgets.QWidget, Ui_OrderWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # --- CẤU HÌNH BẢNG ĐỂ TỰ ĐỘNG BẮT SỰ KIỆN CLICK CHỌN DÒNG ---
        self.tblOrder.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblOrder.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblOrder.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        # ------------------------------------------------------------

        # Dữ liệu mẫu ban đầu cho danh sách đơn hàng chính (đổ vào tblOrder)
        self.data_orders = [
            {
                "order_id": "HD001", "date": "2026-07-15 09:30", "cust_name": "Nguyễn Văn A",
                "phone": "0901234567", "address": "123 Đường Lê Lợi, Q.1, HCM", "live": "Live xả kho quần áo hè",
                "total": "348,000", "voucher": "GIAM50K", "payment": "Chuyển khoản", "status": "Đã xác nhận",
                "products": [("Áo thun Unisex", "2", "99,000"), ("Quần Jean Baggy", "1", "150,000")]
            },
            {
                "order_id": "HD002", "date": "2026-07-15 10:15", "cust_name": "Trần Thị B",
                "phone": "0987654321", "address": "456 Đường Nguyễn Huệ, Q.3, HCM",
                "live": "Săn deal mỹ phẩm chính hãng",
                "total": "250,000", "voucher": "Không có", "payment": "Tiền mặt", "status": "Chờ xác nhận",
                "products": [("Son lì Matte", "1", "250,000")]
            }
        ]

        # Biến trạng thái hành động: None, "THEM", hoặc "SUA"
        self.current_action = None

        # Khởi tạo dữ liệu cho các ComboBox (Livestream và Voucher)
        self.init_combobox_data()

        # Kết nối sự kiện nút bấm điều hướng & chức năng
        self.btnSearch.clicked.connect(self.action_search)
        self.btnRefresh.clicked.connect(self.action_refresh)
        self.btnThem.clicked.connect(self.action_them)
        self.btnSua.clicked.connect(self.action_sua)
        self.btnXoa.clicked.connect(self.action_xoa)
        self.btnLuu.clicked.connect(self.action_luu)
        self.btnHuy.clicked.connect(self.action_huy)
        self.btnXuatExcel.clicked.connect(self.action_xuat_excel)

        # Sự kiện click chọn dòng trên Table đơn hàng chính để đồng bộ lên Form nhập
        self.tblOrder.itemSelectionChanged.connect(self.sync_table_to_form)

        # Tải dữ liệu ban đầu lên bảng đơn hàng và khóa form
        self.load_orders_to_table(self.data_orders)
        self.set_form_enabled(False)

    def init_combobox_data(self):
        """Khởi tạo danh sách buổi Livestream và Voucher giảm giá"""
        self.cbLivestream.clear()
        self.cbLivestream.addItems(["Live xả kho quần áo hè", "Săn deal mỹ phẩm chính hãng", "Đồ gia dụng thông minh"])

        self.cbVoucher.clear()
        self.cbVoucher.addItems(["Không có", "GIAM50K", "FREESHIP", "VIP10"])

    def load_orders_to_table(self, data_list):
        """Đổ danh sách đơn hàng vào QTableWidget đơn hàng (tblOrder)"""
        self.tblOrder.setRowCount(0)
        for row_idx, row_data in enumerate(data_list):
            self.tblOrder.insertRow(row_idx)
            self.tblOrder.setItem(row_idx, 0, QTableWidgetItem(row_data["order_id"]))
            self.tblOrder.setItem(row_idx, 1, QTableWidgetItem(row_data["date"]))
            self.tblOrder.setItem(row_idx, 2, QTableWidgetItem(row_data["cust_name"]))
            self.tblOrder.setItem(row_idx, 3, QTableWidgetItem(row_data["phone"]))
            self.tblOrder.setItem(row_idx, 4, QTableWidgetItem(row_data["total"]))
            self.tblOrder.setItem(row_idx, 5, QTableWidgetItem(row_data["voucher"]))
            self.tblOrder.setItem(row_idx, 6, QTableWidgetItem(row_data["status"]))

        self.tblOrder.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def load_products_to_sub_table(self, products_list):
        """Đổ danh sách sản phẩm đã mua của đơn hàng được chọn vào bảng phụ (tblOrderProductsList)"""
        self.tblOrderProductsList.setRowCount(0)
        for row_idx, prod in enumerate(products_list):
            self.tblOrderProductsList.insertRow(row_idx)
            self.tblOrderProductsList.setItem(row_idx, 0, QTableWidgetItem(prod[0]))  # Tên sản phẩm
            self.tblOrderProductsList.setItem(row_idx, 1, QTableWidgetItem(str(prod[1])))  # Số lượng
            self.tblOrderProductsList.setItem(row_idx, 2, QTableWidgetItem(str(prod[2])))  # Đơn giá

        self.tblOrderProductsList.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def set_form_enabled(self, enabled=True):
        """Đóng/Mở khóa các thành phần nhập liệu của Form"""
        self.dateNgayDat.setEnabled(enabled)
        self.cbLivestream.setEnabled(enabled)
        self.txtTenKhachHang.setEnabled(enabled)
        self.txtSoDienThoai.setEnabled(enabled)
        self.txtDiaChiGiao.setEnabled(enabled)
        self.cbVoucher.setEnabled(enabled)
        self.cbPaymentMode.setEnabled(enabled)
        self.cbTrangThai.setEnabled(enabled)
        # Bảng chọn sản phẩm cho phép sửa trực tiếp nếu ở trạng thái chỉnh sửa
        self.tblOrderProductsList.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers if enabled
            else QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.btnThem.setEnabled(not enabled)
        self.btnSua.setEnabled(not enabled)
        self.btnXoa.setEnabled(not enabled)
        self.btnLuu.setEnabled(enabled)
        self.btnHuy.setEnabled(enabled)

    def sync_table_to_form(self):
        """Đồng bộ thông tin từ dòng đơn hàng được chọn lên bảng và form chi tiết"""
        if self.current_action is not None:
            return

        selected_rows = self.tblOrder.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        order_id = self.tblOrder.item(row, 0).text()

        # Tìm dữ liệu đơn gốc dựa vào mã hóa đơn
        order_data = next((item for item in self.data_orders if item["order_id"] == order_id), None)
        if not order_data:
            return

        # Hiển thị thông tin văn bản sang khung kế bên
        self.txtTenKhachHang.setText(order_data["cust_name"])
        self.txtSoDienThoai.setText(order_data["phone"])
        self.txtDiaChiGiao.setText(order_data["address"])
        self.txtTongTien.setText(order_data["total"])

        # Đồng bộ ComboBox
        idx_live = self.cbLivestream.findText(order_data["live"])
        if idx_live >= 0: self.cbLivestream.setCurrentIndex(idx_live)

        idx_vouch = self.cbVoucher.findText(order_data["voucher"])
        if idx_vouch >= 0: self.cbVoucher.setCurrentIndex(idx_vouch)

        idx_pay = self.cbPaymentMode.findText(order_data["payment"])
        if idx_pay >= 0: self.cbPaymentMode.setCurrentIndex(idx_pay)

        idx_status = self.cbTrangThai.findText(order_data["status"])
        if idx_status >= 0: self.cbTrangThai.setCurrentIndex(idx_status)

        # Đồng bộ ngày giờ
        qdatetime = QtCore.QDateTime.fromString(order_data["date"], "yyyy-MM-dd HH:mm")
        if qdatetime.isValid():
            self.dateNgayDat.setDateTime(qdatetime)

        # Hiển thị danh sách sản phẩm đi kèm đơn hàng vào bảng nhỏ
        self.load_products_to_sub_table(order_data["products"])

    def clear_form(self):
        """Làm sạch Form để chuẩn bị thêm đơn hàng mới"""
        self.txtTenKhachHang.clear()
        self.txtSoDienThoai.clear()
        self.txtDiaChiGiao.clear()
        self.txtTongTien.setText("0")
        self.dateNgayDat.setDateTime(QtCore.QDateTime.currentDateTime())
        self.cbLivestream.setCurrentIndex(0)
        self.cbVoucher.setCurrentIndex(0)
        self.cbPaymentMode.setCurrentIndex(0)
        self.cbTrangThai.setCurrentIndex(0)

        # Tạo sẵn hàng trống ở bảng sản phẩm để người dùng tự điền trực tiếp
        self.tblOrderProductsList.setRowCount(0)
        self.tblOrderProductsList.insertRow(0)
        self.tblOrderProductsList.setItem(0, 0, QTableWidgetItem("Sản phẩm mới"))
        self.tblOrderProductsList.setItem(0, 1, QTableWidgetItem("1"))
        self.tblOrderProductsList.setItem(0, 2, QTableWidgetItem("100,000"))

    # --- CÁC HÀM XỬ LÝ CHỨC NĂNG HÀNH ĐỘNG ---

    def action_search(self):
        """Tìm kiếm đơn hàng theo tên khách hàng hoặc số điện thoại"""
        search_text = self.txtSearch.text().strip().lower()
        if not search_text:
            self.load_orders_to_table(self.data_orders)
            return

        filtered = [
            item for item in self.data_orders
            if search_text in item["cust_name"].lower() or search_text in item["phone"]
        ]
        self.load_orders_to_table(filtered)
        self.lblStatus.setText(f"Trạng thái: Tìm thấy {len(filtered)} đơn hàng thỏa mãn.")

    def action_refresh(self):
        """Làm mới thanh tìm kiếm và tải lại danh sách gốc"""
        self.txtSearch.clear()
        self.load_orders_to_table(self.data_orders)
        self.lblStatus.setText("Trạng thái: Làm mới danh sách đơn hàng thành công.")

    def action_them(self):
        """Kích hoạt giao diện thêm đơn hàng mới"""
        self.current_action = "THEM"
        self.clear_form()
        self.set_form_enabled(True)
        self.lblStatus.setText("Trạng thái: Đang nhập thông tin tạo đơn hàng mới...")

    def action_sua(self):
        """Kích hoạt chỉnh sửa đơn hàng đang chọn"""
        selected_rows = self.tblOrder.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn đơn hàng cần sửa đổi trong bảng!")
            return

        self.current_action = "SUA"
        self.set_form_enabled(True)
        self.lblStatus.setText("Trạng thái: Đang điều chỉnh chi tiết đơn hàng...")

    def action_xoa(self):
        """Xóa đơn hàng hiện tại"""
        selected_rows = self.tblOrder.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn đơn hàng cần xóa bỏ!")
            return

        row = selected_rows[0].row()
        order_id = self.tblOrder.item(row, 0).text()

        confirm = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn hủy bỏ và xóa đơn hàng {order_id} khỏi hệ thống?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.data_orders = [item for item in self.data_orders if item["order_id"] != order_id]
            self.load_orders_to_table(self.data_orders)
            self.tblOrderProductsList.setRowCount(0)
            self.clear_form()
            self.lblStatus.setText(f"Trạng thái: Đã xóa hoàn toàn đơn hàng {order_id}.")

    def action_luu(self):
        """Lưu lại thông tin đơn hàng sau khi Thêm hoặc Sửa"""
        cust_name = self.txtTenKhachHang.text().strip()
        phone = self.txtSoDienThoai.text().strip()

        if not cust_name or not phone:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Không được để trống Tên khách hàng và Số điện thoại!")
            return

        # Lấy dữ liệu từ giao diện
        date_str = self.dateNgayDat.dateTime().toString("yyyy-MM-dd HH:mm")
        live = self.cbLivestream.currentText()
        address = self.txtDiaChiGiao.text().strip()
        voucher = self.cbVoucher.currentText()
        payment = self.cbPaymentMode.currentText()
        status = self.cbTrangThai.currentText()

        # Đọc danh sách sản phẩm từ bảng phụ tblOrderProductsList
        products_list = []
        sub_rows = self.tblOrderProductsList.rowCount()
        for r in range(sub_rows):
            p_name = self.tblOrderProductsList.item(r, 0).text() if self.tblOrderProductsList.item(r,
                                                                                                   0) else "Sản phẩm ẩn"
            p_qty = self.tblOrderProductsList.item(r, 1).text() if self.tblOrderProductsList.item(r, 1) else "1"
            p_price = self.tblOrderProductsList.item(r, 2).text() if self.tblOrderProductsList.item(r, 2) else "0"
            products_list.append((p_name, p_qty, p_price))

        if self.current_action == "THEM":
            new_id = f"HD{len(self.data_orders) + 1:03d}"
            new_order = {
                "order_id": new_id, "date": date_str, "cust_name": cust_name, "phone": phone,
                "address": address, "live": live, "total": "150,000", "voucher": voucher,
                "payment": payment, "status": status, "products": products_list
            }
            self.data_orders.append(new_order)
            self.lblStatus.setText(f"Trạng thái: Thêm mới đơn hàng {new_id} thành công.")

        elif self.current_action == "SUA":
            selected_rows = self.tblOrder.selectionModel().selectedRows()
            row = selected_rows[0].row()
            order_id = self.tblOrder.item(row, 0).text()

            for item in self.data_orders:
                if item["order_id"] == order_id:
                    item["date"] = date_str
                    item["cust_name"] = cust_name
                    item["phone"] = phone
                    item["address"] = address
                    item["live"] = live
                    item["voucher"] = voucher
                    item["payment"] = payment
                    item["status"] = status
                    item["products"] = products_list
                    break
            self.lblStatus.setText(f"Trạng thái: Cập nhật thông tin đơn {order_id} thành công.")

        self.load_orders_to_table(self.data_orders)
        self.current_action = None
        self.set_form_enabled(False)

    def action_huy(self):
        """Hủy bỏ thao tác hiện tại và đưa Form về trạng thái cũ"""
        self.current_action = None
        self.clear_form()
        self.set_form_enabled(False)
        self.sync_table_to_form()
        self.lblStatus.setText("Trạng thái: Đã hủy thao tác.")

    def action_xuat_excel(self):
        """Xuất danh sách quản lý đơn hàng ra file CSV báo cáo nhanh"""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Xuất báo cáo đơn hàng", "", "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8-sig') as f:
                    headers = ["Mã Hóa Đơn", "Ngày Đặt", "Khách Hàng", "Số Điện Thoại", "Tổng Tiền (VND)",
                               "Voucher Sử Dụng", "Trạng Thái"]
                    f.write(",".join(headers) + "\n")
                    for item in self.data_orders:
                        row_str = f"{item['order_id']},{item['date']},{item['cust_name']},{item['phone']},{item['total']},{item['voucher']},{item['status']}"
                        f.write(row_str + "\n")
                QMessageBox.information(self, "Thành công", f"Báo cáo đơn hàng đã xuất tại:\n{path}")
                self.lblStatus.setText("Trạng thái: Xuất file Excel (CSV) thành công.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi ghi file", f"Không thể lưu file báo cáo: {str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = OrderEx()
    window.show()
    sys.exit(app.exec())