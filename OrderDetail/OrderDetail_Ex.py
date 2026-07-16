import sys
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox

# Nhập lớp giao diện được tạo tự động từ file OrderDetail.ui của bạn
from OrderDetail import Ui_OrderDetailWidget


class OrderDetailEx(QtWidgets.QWidget, Ui_OrderDetailWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # --- CẤU HÌNH BẢNG TỰ ĐỘNG BẮT LỰA CHỌN DÒNG ---
        self.tblOrderDetail.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblOrderDetail.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblOrderDetail.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # Dữ liệu giả lập danh mục Đơn hàng và Sản phẩm để nạp vào QComboBox
        self.list_orders = ["DH001", "DH002", "DH003"]
        self.dict_products = {
            "SP001": "Áo Thun Livestream Basic",
            "SP002": "Váy Hoa Dáng Xòe Mùa Hè",
            "SP003": "Quần Jean Nữ Lưng Cao"
        }

        # Dữ liệu giả lập danh sách Chi tiết đơn hàng ban đầu
        self.data_order_details = [
            {"detail_id": "CT001", "order_id": "DH001", "prod_id": "SP001", "prod_name": "Áo Thun Livestream Basic",
             "qty": 2, "price": 150000},
            {"detail_id": "CT002", "order_id": "DH001", "prod_id": "SP002", "prod_name": "Váy Hoa Dáng Xòe Mùa Hè",
             "qty": 1, "price": 320000},
            {"detail_id": "CT003", "order_id": "DH002", "prod_id": "SP003", "prod_name": "Quần Jean Nữ Lưng Cao",
             "qty": 3, "price": 250000}
        ]

        # Biến quản lý trạng thái thao tác: None, "THEM", hoặc "SUA"
        self.current_action = None

        # Nạp dữ liệu vào ComboBox đơn hàng và sản phẩm
        self.cbDonHang.addItems(self.list_orders)
        for p_id, p_name in self.dict_products.items():
            self.cbSanPham.addItem(f"{p_id} - {p_name}", p_id)  # Lưu p_id vào userData

        # Kết nối sự kiện thay đổi số lượng và giá bán để tự động tính Thành Tiền
        self.spinSoLuong.valueChanged.connect(self.update_subtotal)
        self.txtGiaBan.textChanged.connect(self.update_subtotal)

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
        self.tblOrderDetail.itemSelectionChanged.connect(self.sync_table_to_form)

        # Tải dữ liệu mặc định hiển thị lên bảng và tạm khóa Form nhập liệu ban đầu
        self.load_data_to_table(self.data_order_details)
        self.set_form_enabled(False)

    def load_data_to_table(self, data_list):
        """Hiển thị danh sách chi tiết đơn hàng lên QTableWidget"""
        self.tblOrderDetail.setRowCount(0)
        for row_idx, row_data in enumerate(data_list):
            subtotal = row_data["qty"] * row_data["price"]
            self.tblOrderDetail.insertRow(row_idx)
            self.tblOrderDetail.setItem(row_idx, 0, QTableWidgetItem(row_data["detail_id"]))
            self.tblOrderDetail.setItem(row_idx, 1, QTableWidgetItem(row_data["order_id"]))
            self.tblOrderDetail.setItem(row_idx, 2, QTableWidgetItem(row_data["prod_id"]))
            self.tblOrderDetail.setItem(row_idx, 3, QTableWidgetItem(row_data["prod_name"]))
            self.tblOrderDetail.setItem(row_idx, 4, QTableWidgetItem(str(row_data["qty"])))
            self.tblOrderDetail.setItem(row_idx, 5, QTableWidgetItem(f"{row_data['price']:,}"))
            self.tblOrderDetail.setItem(row_idx, 6, QTableWidgetItem(f"{subtotal:,}"))

        # Tự co giãn các cột dữ liệu theo kích thước hiển thị của màn hình
        self.tblOrderDetail.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def set_form_enabled(self, enabled=True):
        """Đóng/Mở trạng thái chỉnh sửa các ô nhập liệu tùy thuộc hành động"""
        self.cbDonHang.setEnabled(enabled)
        self.cbSanPham.setEnabled(enabled)
        self.spinSoLuong.setEnabled(enabled)
        self.txtGiaBan.setEnabled(enabled)

        # Khóa/Mở các nút chức năng tương ứng để ngăn ngừa xung đột dữ liệu
        self.btnThem.setEnabled(not enabled)
        self.btnSua.setEnabled(not enabled)
        self.btnXoa.setEnabled(not enabled)
        self.btnLuu.setEnabled(enabled)
        self.btnHuy.setEnabled(enabled)

    def update_subtotal(self):
        """Tự động tính toán và cập nhật Thành Tiền = Số lượng x Giá bán"""
        qty = self.spinSoLuong.value()
        try:
            price_text = self.txtGiaBan.text().replace(",", "").strip()
            price = int(price_text) if price_text else 0
        except ValueError:
            price = 0

        subtotal = qty * price
        self.txtThanhTien.setText(f"{subtotal:,}")

    def sync_table_to_form(self):
        """Khi click chọn dòng trên bảng, đổ thông tin tương ứng sang khung bên cạnh"""
        if self.current_action is not None:
            return  # Đang trong trạng thái Thêm/Sửa thì không tự động chuyển dòng khi click bảng

        selected_rows = self.tblOrderDetail.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        order_id = self.tblOrderDetail.item(row, 1).text()
        prod_id = self.tblOrderDetail.item(row, 2).text()
        qty = int(self.tblOrderDetail.item(row, 4).text())
        price = self.tblOrderDetail.item(row, 5).text().replace(",", "")

        # Chọn item tương ứng trên ComboBox đơn hàng
        self.cbDonHang.setCurrentText(order_id)

        # Chọn item tương ứng trên ComboBox sản phẩm
        for idx in range(self.cbSanPham.count()):
            if self.cbSanPham.itemData(idx) == prod_id:
                self.cbSanPham.setCurrentIndex(idx)
                break

        self.spinSoLuong.setValue(qty)
        self.txtGiaBan.setText(price)
        self.update_subtotal()

    def clear_form(self):
        """Xóa dữ liệu cũ trên form về mặc định để chuẩn bị thao tác mới"""
        if self.cbDonHang.count() > 0: self.cbDonHang.setCurrentIndex(0)
        if self.cbSanPham.count() > 0: self.cbSanPham.setCurrentIndex(0)
        self.spinSoLuong.setValue(1)
        self.txtGiaBan.clear()
        self.txtThanhTien.setText("0")

    # --- ĐỊNH NGHĨA CÁC HÀM XỬ LÝ SỰ KIỆN NÚT BẤM ---

    def action_search(self):
        """Tìm kiếm chi tiết đơn hàng theo Mã Đơn Hàng hoặc Tên Sản Phẩm"""
        search_text = self.txtSearch.text().strip().lower()
        if not search_text:
            self.load_data_to_table(self.data_order_details)
            return

        filtered_data = [
            item for item in self.data_order_details
            if search_text in item["order_id"].lower() or search_text in item["prod_name"].lower()
        ]
        self.load_data_to_table(filtered_data)
        self.lblStatus.setText(f"Trạng thái: Đã tìm thấy {len(filtered_data)} kết quả phù hợp.")

    def action_refresh(self):
        """Làm mới ô tìm kiếm và đặt danh sách bảng về trạng thái mặc định"""
        self.txtSearch.clear()
        self.load_data_to_table(self.data_order_details)
        self.lblStatus.setText("Trạng thái: Đã làm mới danh sách.")

    def action_them(self):
        """Kích hoạt trạng thái thêm mới chi tiết mặt hàng"""
        self.current_action = "THEM"
        self.clear_form()
        self.set_form_enabled(True)
        self.txtGiaBan.setFocus()
        self.lblStatus.setText("Trạng thái: Đang nhập mới thông tin sản phẩm bán ra...")

    def action_sua(self):
        """Kích hoạt trạng thái sửa đổi thông tin bản ghi đang chọn"""
        selected_rows = self.tblOrderDetail.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một dòng trên bảng để sửa!")
            return

        self.current_action = "SUA"
        self.set_form_enabled(True)
        self.lblStatus.setText("Trạng thái: Đang chỉnh sửa thông tin bản ghi...")

    def action_xoa(self):
        """Xóa bỏ bản ghi chi tiết đơn hàng đang được lựa chọn"""
        selected_rows = self.tblOrderDetail.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một bản ghi trên bảng để xóa!")
            return

        row = selected_rows[0].row()
        detail_id = self.tblOrderDetail.item(row, 0).text()

        confirm = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa mã chi tiết đơn hàng {detail_id} không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.data_order_details = [item for item in self.data_order_details if item["detail_id"] != detail_id]
            self.load_data_to_table(self.data_order_details)
            self.clear_form()
            self.lblStatus.setText(f"Trạng thái: Đã xóa thành công bản ghi {detail_id}")

    def action_luu(self):
        """Lưu trữ thông tin dữ liệu sau khi nhấn Thêm mới hoặc Chỉnh sửa"""
        order_id = self.cbDonHang.currentText()
        prod_id = self.cbSanPham.currentData()  # Lấy mã sản phẩm từ userData
        prod_name = self.dict_products.get(prod_id, "")
        qty = self.spinSoLuong.value()

        try:
            price_text = self.txtGiaBan.text().replace(",", "").strip()
            price = int(price_text) if price_text else 0
        except ValueError:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Giá bán phải là số nguyên hợp lệ!")
            return

        if price <= 0:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Giá bán thực tế phải lớn hơn 0!")
            return

        if self.current_action == "THEM":
            # Tự động sinh mã chi tiết tăng tiến tiếp theo
            new_id = f"CT{len(self.data_order_details) + 1:03d}"
            new_item = {
                "detail_id": new_id,
                "order_id": order_id,
                "prod_id": prod_id,
                "prod_name": prod_name,
                "qty": qty,
                "price": price
            }
            self.data_order_details.append(new_item)
            self.lblStatus.setText(f"Trạng thái: Thêm mới thành công bản ghi {new_id}")

        elif self.current_action == "SUA":
            selected_rows = self.tblOrderDetail.selectionModel().selectedRows()
            row = selected_rows[0].row()
            detail_id = self.tblOrderDetail.item(row, 0).text()

            # Tiến hành cập nhật thông tin chỉnh sửa vào mảng dữ liệu
            for item in self.data_order_details:
                if item["detail_id"] == detail_id:
                    item["order_id"] = order_id
                    item["prod_id"] = prod_id
                    item["prod_name"] = prod_name
                    item["qty"] = qty
                    item["price"] = price
                    break
            self.lblStatus.setText(f"Trạng thái: Đã cập nhật thành công thông tin {detail_id}")

        self.load_data_to_table(self.data_order_details)
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
        """Kết xuất cấu trúc dữ liệu của bảng chi tiết đơn hàng ra file CSV tiện ích"""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Lưu file dữ liệu báo cáo", "", "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8-sig') as f:
                    # Ghi dòng tiêu đề cột dữ liệu
                    headers = ["Mã Chi Tiết ĐH", "Đơn Hàng", "Mã Sản Phẩm", "Tên Sản Phẩm", "SL Mua", "Đơn Giá Bán",
                               "Thành Tiền (VND)"]
                    f.write(",".join(headers) + "\n")
                    # Ghi nội dung chi tiết của từng bản ghi dữ liệu
                    for item in self.data_order_details:
                        subtotal = item["qty"] * item["price"]
                        row_str = f"{item['detail_id']},{item['order_id']},{item['prod_id']},{item['prod_name']},{item['qty']},{item['price']},{subtotal}"
                        f.write(row_str + "\n")
                QMessageBox.information(self, "Xuất dữ liệu", f"Đã kết xuất dữ liệu thành công tại đường dẫn:\n{path}")
                self.lblStatus.setText("Trạng thái: Xuất file báo cáo thành công.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể lưu trữ tệp tin: {str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = OrderDetailEx()
    window.show()
    sys.exit(app.exec())