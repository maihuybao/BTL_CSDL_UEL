import sys
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox

# Nhập class giao diện từ file LivestreamDetail.py (được biên dịch từ file UI của bạn)
from LivestreamDetail.LivestreamDetail import Ui_LivestreamDetailWidget


class LivestreamDetailEx(QtWidgets.QWidget, Ui_LivestreamDetailWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # --- CẤU HÌNH BẢNG ĐỂ TỰ ĐỘNG BẮT SỰ KIỆN CLICK CHỌN DÒNG ---
        self.tblLivestreamDetail.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblLivestreamDetail.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblLivestreamDetail.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        # ------------------------------------------------------------

        # Dữ liệu mẫu ban đầu để hiển thị lên TableWidget
        self.data_details = [
            {"dt_id": "DET001", "live_title": "Xả kho quần áo hè", "prod_id": "SP001", "prod_name": "Áo thun Unisex",
             "qty": 150, "price": "99,000"},
            {"dt_id": "DET002", "live_title": "Xả kho quần áo hè", "prod_id": "SP002", "prod_name": "Quần Jean Baggy",
             "qty": 80, "price": "199,000"},
            {"dt_id": "DET003", "live_title": "Săn deal mỹ phẩm chính hãng", "prod_id": "SP003",
             "prod_name": "Son lì Matte", "qty": 200, "price": "250,000"}
        ]

        # Biến trạng thái hành động: None, "THEM", hoặc "SUA"
        self.current_action = None

        # Khởi tạo dữ liệu cho các ComboBox (Buổi Live và Sản phẩm)
        self.init_combobox_data()

        # Kết nối sự kiện nút bấm
        self.btnSearch.clicked.connect(self.action_search)
        self.btnRefresh.clicked.connect(self.action_refresh)
        self.btnThem.clicked.connect(self.action_them)
        self.btnSua.clicked.connect(self.action_sua)
        self.btnXoa.clicked.connect(self.action_xoa)
        self.btnLuu.clicked.connect(self.action_luu)
        self.btnHuy.clicked.connect(self.action_huy)
        self.btnXuatExcel.clicked.connect(self.action_xuat_excel)

        # Sự kiện thay đổi dòng chọn trên TableWidget để đồng bộ lên Form nhập
        self.tblLivestreamDetail.itemSelectionChanged.connect(self.sync_table_to_form)

        # Tải dữ liệu ban đầu lên giao diện
        self.load_data_to_table(self.data_details)
        self.set_form_enabled(False)

    def init_combobox_data(self):
        """Khởi tạo danh sách buổi livestream và sản phẩm mẫu"""
        self.cbLivestream.clear()
        self.cbLivestream.addItems(
            ["Xả kho quần áo hè", "Săn deal mỹ phẩm chính hãng", "Đồ gia dụng thông minh giá rẻ"])

        self.cbSanPham.clear()
        # Định dạng dạng "Mã SP - Tên SP" để dễ tách dữ liệu khi lưu
        self.cbSanPham.addItems([
            "SP001 - Áo thun Unisex",
            "SP002 - Quần Jean Baggy",
            "SP003 - Son lì Matte",
            "SP004 - Chảo chống dính Sunhouse"
        ])

    def load_data_to_table(self, data_list):
        """Đổ dữ liệu từ danh sách vào QTableWidget"""
        self.tblLivestreamDetail.setRowCount(0)
        for row_idx, row_data in enumerate(data_list):
            self.tblLivestreamDetail.insertRow(row_idx)
            self.tblLivestreamDetail.setItem(row_idx, 0, QTableWidgetItem(row_data["dt_id"]))
            self.tblLivestreamDetail.setItem(row_idx, 1, QTableWidgetItem(row_data["live_title"]))
            self.tblLivestreamDetail.setItem(row_idx, 2, QTableWidgetItem(row_data["prod_id"]))
            self.tblLivestreamDetail.setItem(row_idx, 3, QTableWidgetItem(row_data["prod_name"]))
            self.tblLivestreamDetail.setItem(row_idx, 4, QTableWidgetItem(str(row_data["qty"])))
            self.tblLivestreamDetail.setItem(row_idx, 5, QTableWidgetItem(row_data["price"]))

        self.tblLivestreamDetail.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def set_form_enabled(self, enabled=True):
        """Đóng/Mở các ô nhập liệu của Form để tránh xung đột dữ liệu"""
        self.cbLivestream.setEnabled(enabled)
        self.cbSanPham.setEnabled(enabled)
        self.spinSoLuongGioiThieu.setEnabled(enabled)
        self.txtGiaKhuyenMai.setEnabled(enabled)

        self.btnThem.setEnabled(not enabled)
        self.btnSua.setEnabled(not enabled)
        self.btnXoa.setEnabled(not enabled)
        self.btnLuu.setEnabled(enabled)
        self.btnHuy.setEnabled(enabled)

    def sync_table_to_form(self):
        """Đồng bộ dữ liệu từ dòng được chọn trong bảng sang Form nhập liệu bên trái"""
        if self.current_action is not None:
            return

        selected_rows = self.tblLivestreamDetail.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()

        live_title = self.tblLivestreamDetail.item(row, 1).text()
        prod_id = self.tblLivestreamDetail.item(row, 2).text()
        prod_name = self.tblLivestreamDetail.item(row, 3).text()
        qty = int(self.tblLivestreamDetail.item(row, 4).text())
        price = self.tblLivestreamDetail.item(row, 5).text()

        # Đổ thông tin vào các widget controls
        idx_live = self.cbLivestream.findText(live_title)
        if idx_live >= 0: self.cbLivestream.setCurrentIndex(idx_live)

        full_prod_text = f"{prod_id} - {prod_name}"
        idx_prod = self.cbSanPham.findText(full_prod_text)
        if idx_prod >= 0: self.cbSanPham.setCurrentIndex(idx_prod)

        self.spinSoLuongGioiThieu.setValue(qty)
        self.txtGiaKhuyenMai.setText(price)

    def clear_form(self):
        """Xóa dữ liệu cũ trên form khi bấm Thêm mới"""
        self.cbLivestream.setCurrentIndex(0)
        self.cbSanPham.setCurrentIndex(0)
        self.spinSoLuongGioiThieu.setValue(0)
        self.txtGiaKhuyenMai.clear()

    # --- HÀM XỬ LÝ CÁC CHỨC NĂNG NÚT BẤM ---

    def action_search(self):
        """Tìm kiếm dữ liệu theo Tiêu đề Live hoặc Tên sản phẩm"""
        search_text = self.txtSearch.text().strip().lower()
        if not search_text:
            self.load_data_to_table(self.data_details)
            return

        filtered = [
            item for item in self.data_details
            if search_text in item["live_title"].lower() or search_text in item["prod_name"].lower()
        ]
        self.load_data_to_table(filtered)
        self.lblStatus.setText(f"Trạng thái: Đã tìm thấy {len(filtered)} bản ghi.")

    def action_refresh(self):
        """Làm mới ô tìm kiếm và đặt bảng về dữ liệu gốc"""
        self.txtSearch.clear()
        self.load_data_to_table(self.data_details)
        self.lblStatus.setText("Trạng thái: Đã làm mới dữ liệu bảng.")

    def action_them(self):
        """Kích hoạt trạng thái Thêm mới"""
        self.current_action = "THEM"
        self.clear_form()
        self.set_form_enabled(True)
        self.lblStatus.setText("Trạng thái: Đang thêm mới chi tiết sản phẩm live...")

    def action_sua(self):
        """Kích hoạt trạng thái Chỉnh sửa bản ghi đang chọn"""
        selected_rows = self.tblLivestreamDetail.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn bản ghi trong bảng cần sửa!")
            return

        self.current_action = "SUA"
        self.set_form_enabled(True)
        self.lblStatus.setText("Trạng thái: Đang sửa đổi thông tin bản ghi...")

    def action_xoa(self):
        """Xóa dòng dữ liệu đang được chọn"""
        selected_rows = self.tblLivestreamDetail.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn bản ghi trong bảng cần xóa!")
            return

        row = selected_rows[0].row()
        dt_id = self.tblLivestreamDetail.item(row, 0).text()

        confirm = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa mã chi tiết {dt_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.data_details = [item for item in self.data_details if item["dt_id"] != dt_id]
            self.load_data_to_table(self.data_details)
            self.clear_form()
            self.lblStatus.setText(f"Trạng thái: Đã xóa thành công bản ghi {dt_id}")

    def action_luu(self):
        """Lưu lại dữ liệu khi Thêm hoặc Sửa"""
        price_text = self.txtGiaKhuyenMai.text().strip()
        if not price_text:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập giá khuyến mãi!")
            return

        live_title = self.cbLivestream.currentText()
        prod_full_text = self.cbSanPham.currentText()
        # Tách mã sản phẩm và tên sản phẩm từ định dạng "Mã SP - Tên SP"
        prod_id, prod_name = [x.strip() for x in prod_full_text.split("-", 1)]
        qty = self.spinSoLuongGioiThieu.value()

        if self.current_action == "THEM":
            new_id = f"DET{len(self.data_details) + 1:03d}"
            new_item = {
                "dt_id": new_id,
                "live_title": live_title,
                "prod_id": prod_id,
                "prod_name": prod_name,
                "qty": qty,
                "price": price_text
            }
            self.data_details.append(new_item)
            self.lblStatus.setText(f"Trạng thái: Thêm mới thành công mã {new_id}")

        elif self.current_action == "SUA":
            selected_rows = self.tblLivestreamDetail.selectionModel().selectedRows()
            row = selected_rows[0].row()
            dt_id = self.tblLivestreamDetail.item(row, 0).text()

            for item in self.data_details:
                if item["dt_id"] == dt_id:
                    item["live_title"] = live_title
                    item["prod_id"] = prod_id
                    item["prod_name"] = prod_name
                    item["qty"] = qty
                    item["price"] = price_text
                    break
            self.lblStatus.setText(f"Trạng thái: Cập nhật thành công mã {dt_id}")

        self.load_data_to_table(self.data_details)
        self.current_action = None
        self.set_form_enabled(False)

    def action_huy(self):
        """Hủy bỏ hành động hiện tại và quay về ban đầu"""
        self.current_action = None
        self.clear_form()
        self.set_form_enabled(False)
        self.sync_table_to_form()
        self.lblStatus.setText("Trạng thái: Đã hủy bỏ thao tác.")

    def action_xuat_excel(self):
        """Xuất danh sách chi tiết livestream ra file CSV tiện dụng"""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Xuất file CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8-sig') as f:
                    headers = ["Mã Chi Tiết Live", "Tiêu Đề Livestream", "Mã Sản Phẩm", "Tên Sản Phẩm", "SL Giới Thiệu",
                               "Giá Khuyến Mãi (VND)"]
                    f.write(",".join(headers) + "\n")
                    for item in self.data_details:
                        row_str = f"{item['dt_id']},{item['live_title']},{item['prod_id']},{item['prod_name']},{item['qty']},{item['price']}"
                        f.write(row_str + "\n")
                QMessageBox.information(self, "Thành công", f"Dữ liệu xuất thành công tại:\n{path}")
                self.lblStatus.setText("Trạng thái: Xuất file báo cáo thành công.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể ghi file: {str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LivestreamDetailEx()
    window.show()
    sys.exit(app.exec())