"""ProductMixin: tab Sản phẩm — CRUD, ảnh, chế độ Sửa/Lưu."""
import os
import sqlite3

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog

from app.config import DB_PATH, PROJECT_ROOT, ASSETS_DIR


class ProductMixin:
    def load_product_image(self, image_path):
        if not image_path:
            self.ui_product.lblImagePreview.setText("Không có ảnh")
            self.ui_product.lblImagePreview.setPixmap(QtGui.QPixmap())
            return

        if not os.path.isabs(image_path):
            for cand in (os.path.join(ASSETS_DIR, image_path),
                         os.path.join(PROJECT_ROOT, image_path)):
                if os.path.exists(cand):
                    image_path = cand
                    break

        if os.path.exists(image_path):
            pixmap = QtGui.QPixmap(image_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.ui_product.lblImagePreview.width(),
                    self.ui_product.lblImagePreview.height(),
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation
                )
                self.ui_product.lblImagePreview.setPixmap(scaled)
            else:
                self.ui_product.lblImagePreview.setText("Lỗi định dạng ảnh")
        else:
            self.ui_product.lblImagePreview.setText(f"Không tìm thấy: {os.path.basename(image_path)}")

    # --- CHI TIẾT SẢN PHẨM ---
    def load_product_data(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT MaSP, TenSP, GiaBan, SoLuongTon, HinhAnh, CASE WHEN SoLuongTon > 0 THEN 'Còn hàng' ELSE 'Hết hàng' END FROM SAN_PHAM")
            self.populate_table(self.ui_product.tblProduct, cursor.fetchall())
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu sản phẩm: {e}")

    def _set_product_form_enabled(self, enabled):
        # Khóa/mở các ô nhập của tab Sản phẩm
        for name in ("txtTenSP", "txtGiaBan", "spinSoLuongTon", "cbTrangThai",
                     "txtImagePath", "btnSelectImage"):
            w = getattr(self.ui_product, name, None)
            if w is not None:
                w.setEnabled(enabled)

    def _set_product_edit_button(self, saving):
        # saving=True -> nút hiển thị "Lưu"; ngược lại "Sửa"
        self.ui_product.btnSua.setText("💾 Lưu lại" if saving else "✏️ Sửa đổi")

    def _product_reset_mode(self):
        self._product_action = None
        self._set_product_form_enabled(False)
        self._set_product_edit_button(False)

    def _on_product_edit_button(self):
        # Nút Sửa/Lưu gộp cho tab Sản phẩm
        if self._product_action == "THEM":
            self._product_do_insert()
        elif self._product_action == "SUA":
            self.product_action_save()
        else:
            if not getattr(self, 'selected_product_id', None):
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một sản phẩm trên bảng để sửa!")
                return
            self._product_action = "SUA"
            self._set_product_form_enabled(True)
            self._set_product_edit_button(True)

    def product_cell_clicked(self, row, column):
        item = self.ui_product.tblProduct.item(row, 0)
        if not item:
            return
        ma_sp = item.text()
        self.selected_product_id = ma_sp

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT TenSP, GiaBan, SoLuongTon, HinhAnh FROM SAN_PHAM WHERE MaSP = ?", (ma_sp,))
            res = cursor.fetchone()
            conn.close()

            if res:
                ten_sp, gia_ban, so_luong, hinh_anh = res
                # Block signals temporarily to prevent infinite recursion during syncing
                self.ui_product.spinSoLuongTon.blockSignals(True)
                self.ui_product.cbTrangThai.blockSignals(True)
                
                self.ui_product.txtTenSP.setText(str(ten_sp or ""))
                self.ui_product.txtGiaBan.setText(str(int(gia_ban) if gia_ban is not None else ""))
                self.ui_product.spinSoLuongTon.setValue(int(so_luong) if so_luong is not None else 0)
                self.ui_product.txtImagePath.setText(str(hinh_anh or ""))
                if so_luong is not None and so_luong > 0:
                    self.ui_product.cbTrangThai.setCurrentIndex(0)
                else:
                    self.ui_product.cbTrangThai.setCurrentIndex(1)

                self.ui_product.spinSoLuongTon.blockSignals(False)
                self.ui_product.cbTrangThai.blockSignals(False)

                self.load_product_image(hinh_anh)
        except Exception as e:
            print(f"Error loading product details: {e}")

    def product_status_changed(self, index):
        self.ui_product.spinSoLuongTon.blockSignals(True)
        if index == 1:  # Hết hàng
            self.ui_product.spinSoLuongTon.setValue(0)
        elif index == 0 and self.ui_product.spinSoLuongTon.value() == 0:
            self.ui_product.spinSoLuongTon.setValue(1)
        self.ui_product.spinSoLuongTon.blockSignals(False)

    def product_spin_changed(self, value):
        self.ui_product.cbTrangThai.blockSignals(True)
        if value == 0:
            self.ui_product.cbTrangThai.setCurrentIndex(1)
        else:
            self.ui_product.cbTrangThai.setCurrentIndex(0)
        self.ui_product.cbTrangThai.blockSignals(False)

    def generate_new_product_id(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT MaSP FROM SAN_PHAM")
            ids = [r[0] for r in cursor.fetchall() if r[0] and r[0].startswith("SP")]
            conn.close()
            max_val = 0
            for i in ids:
                num = i[2:]
                if num.isdigit():
                    max_val = max(max_val, int(num))
            return f"SP{max_val + 1:02d}"
        except Exception as e:
            print(e)
            return "SP99"

    def product_action_them(self):
        # Mở form ở chế độ THÊM: xóa trắng, bật ô nhập, nút Sửa -> Lưu
        self.selected_product_id = None
        self.product_clear_fields()
        self._product_action = "THEM"
        self._set_product_form_enabled(True)
        self._set_product_edit_button(True)

    def _product_do_insert(self):
        ten_sp = self.ui_product.txtTenSP.text().strip()
        gia_ban_str = self.ui_product.txtGiaBan.text().strip()
        so_luong = self.ui_product.spinSoLuongTon.value()
        hinh_anh = self.ui_product.txtImagePath.text().strip()

        if not ten_sp:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Vui lòng nhập Tên sản phẩm!")
            return

        try:
            gia_ban = float(gia_ban_str) if gia_ban_str else 0.0
        except ValueError:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Giá bán phải là số hợp lệ!")
            return

        ma_sp = self.generate_new_product_id()

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO SAN_PHAM (MaSP, TenSP, GiaBan, SoLuongTon, HinhAnh, MoTa) VALUES (?, ?, ?, ?, ?, ?)",
                           (ma_sp, ten_sp, gia_ban, so_luong, hinh_anh, ""))
            conn.commit()
            conn.close()

            self.load_product_data()
            self.product_clear_fields()
            self._product_reset_mode()
            QMessageBox.information(self, "Thành công", f"Đã thêm sản phẩm {ma_sp} thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm sản phẩm: {e}")

    def product_action_save(self):
        if not hasattr(self, 'selected_product_id') or not self.selected_product_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một sản phẩm trên bảng để sửa!")
            return

        ten_sp = self.ui_product.txtTenSP.text().strip()
        gia_ban_str = self.ui_product.txtGiaBan.text().strip()
        so_luong = self.ui_product.spinSoLuongTon.value()
        hinh_anh = self.ui_product.txtImagePath.text().strip()

        if not ten_sp:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Tên sản phẩm không được để trống!")
            return

        try:
            gia_ban = float(gia_ban_str) if gia_ban_str else 0.0
        except ValueError:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Giá bán phải là số hợp lệ!")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE SAN_PHAM SET TenSP = ?, GiaBan = ?, SoLuongTon = ?, HinhAnh = ? WHERE MaSP = ?",
                           (ten_sp, gia_ban, so_luong, hinh_anh, self.selected_product_id))
            conn.commit()
            conn.close()

            self.load_product_data()
            self._product_reset_mode()
            QMessageBox.information(self, "Thành công", f"Cập nhật thành công sản phẩm {self.selected_product_id}.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật sản phẩm: {e}")

    def product_action_xoa(self):
        if not hasattr(self, 'selected_product_id') or not self.selected_product_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một sản phẩm trên bảng để xóa!")
            return

        confirm = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa sản phẩm {self.selected_product_id} không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM SAN_PHAM WHERE MaSP = ?", (self.selected_product_id,))
                conn.commit()
                conn.close()

                self.load_product_data()
                self.product_clear_fields()
                self.selected_product_id = None
                QMessageBox.information(self, "Thành công", "Đã xóa sản phẩm khỏi cơ sở dữ liệu.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa sản phẩm: {e}")

    def product_export_excel(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Lưu file Excel sản phẩm", "", "Excel Files (*.xlsx);;All Files (*)"
        )
        if not path:
            return

        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "SanPham"

            headers = ["Mã SP", "Tên Sản Phẩm", "Giá Bán", "Số Tồn Kho", "Đường Dẫn Ảnh", "Trạng Thái"]
            ws.append(headers)

            for row in range(self.ui_product.tblProduct.rowCount()):
                row_data = []
                for col in range(self.ui_product.tblProduct.columnCount()):
                    item = self.ui_product.tblProduct.item(row, col)
                    row_data.append(item.text() if item else "")
                ws.append(row_data)

            wb.save(path)
            QMessageBox.information(self, "Thành công", f"Đã xuất dữ liệu Excel thành công tại:\n{path}")
        except ImportError:
            QMessageBox.critical(self, "Lỗi", "Vui lòng cài đặt openpyxl bằng lệnh: pip install openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file Excel: {e}")

    def product_action_clear(self):
        self.ui_product.tblProduct.setRowCount(0)
        self.product_clear_fields()
        self.selected_product_id = None
        self._product_reset_mode()
        self.ui_product.lblStatus.setText("Trạng thái: Đã xóa dữ liệu trên bảng hiển thị.")

    def product_clear_fields(self):
        self.ui_product.txtTenSP.clear()
        self.ui_product.txtGiaBan.clear()
        self.ui_product.spinSoLuongTon.setValue(0)
        self.ui_product.txtImagePath.clear()
        self.ui_product.cbTrangThai.setCurrentIndex(0)
        self.ui_product.lblImagePreview.setText("Xem trước hình ảnh")
        self.ui_product.lblImagePreview.setPixmap(QtGui.QPixmap())

    def product_search(self):
        search_text = self.ui_product.txtSearch.text().strip()
        if not search_text:
            self.load_product_data()
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            query = """
                SELECT MaSP, TenSP, GiaBan, SoLuongTon, HinhAnh, 
                       CASE WHEN SoLuongTon > 0 THEN 'Còn hàng' ELSE 'Hết hàng' END 
                FROM SAN_PHAM 
                WHERE TenSP LIKE ?
            """
            cursor.execute(query, (f"%{search_text}%",))
            results = cursor.fetchall()
            conn.close()

            self.populate_table(self.ui_product.tblProduct, results)
            self.ui_product.lblStatus.setText(f"Trạng thái: Tìm thấy {len(results)} sản phẩm.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tìm kiếm sản phẩm: {e}")

    def product_refresh(self):
        self.ui_product.txtSearch.clear()
        self.load_product_data()
        self.ui_product.lblStatus.setText("Trạng thái: Đã làm mới dữ liệu sản phẩm.")

    def product_select_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Chọn hình ảnh sản phẩm", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if path:
            filename = os.path.basename(path)
            self.ui_product.txtImagePath.setText(filename)

            try:
                os.makedirs(ASSETS_DIR, exist_ok=True)
                dest = os.path.join(ASSETS_DIR, filename)
                if not os.path.exists(dest):
                    import shutil
                    shutil.copy(path, dest)
            except Exception as e:
                print(f"Error copying image: {e}")

            self.load_product_image(path)

    # --- PHÂN HỆ NGƯỜI BÁN ---
