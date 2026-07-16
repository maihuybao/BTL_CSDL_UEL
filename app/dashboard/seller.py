"""SellerMixin: tab Người bán — CRUD, chế độ Sửa/Lưu."""
import sqlite3

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox

from app.config import DB_PATH, HAS_QTA
if HAS_QTA:
    from app.config import qta


class SellerMixin:
    def load_seller_data(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT MaNguoiBan, HoTen, SoDienThoai, Email, TenCuaHang FROM NGUOI_BAN")
            self.populate_table(self.ui_seller.tblSeller, cursor.fetchall())
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu người bán: {e}")

    def _set_seller_form_enabled(self, enabled):
        for name in ("txtTenNguoiBan", "txtSoDienThoai", "txtEmail", "txtMatKhau", "txtTenShop"):
            w = getattr(self.ui_seller, name, None)
            if w is not None:
                w.setEnabled(enabled)

    def _set_seller_edit_button(self, saving):
        self.ui_seller.btnSua.setText("Lưu" if saving else "Sửa")
        if HAS_QTA:
            self.ui_seller.btnSua.setIcon(
                qta.icon('fa5s.save' if saving else 'fa5s.edit', color='white'))

    def _seller_reset_mode(self):
        self._seller_action = None
        self._set_seller_form_enabled(False)
        self._set_seller_edit_button(False)

    def _on_seller_edit_button(self):
        if self._seller_action == "THEM":
            self._seller_do_insert()
        elif self._seller_action == "SUA":
            self.seller_action_save()
        else:
            if not getattr(self, 'selected_seller_id', None):
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một người bán trên bảng để sửa!")
                return
            self._seller_action = "SUA"
            self._set_seller_form_enabled(True)
            self._set_seller_edit_button(True)

    def seller_cell_clicked(self, row, column):
        item = self.ui_seller.tblSeller.item(row, 0)
        if not item:
            return
        ma_nb = item.text()
        self.selected_seller_id = ma_nb

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT HoTen, SoDienThoai, Email, MatKhau, TenCuaHang FROM NGUOI_BAN WHERE MaNguoiBan = ?", (ma_nb,))
            res = cursor.fetchone()
            conn.close()

            if res:
                ho_ten, sdt, email, mat_khau, shop = res
                self.ui_seller.txtTenNguoiBan.setText(str(ho_ten or ""))
                self.ui_seller.txtSoDienThoai.setText(str(sdt or ""))
                self.ui_seller.txtEmail.setText(str(email or ""))
                self.ui_seller.txtMatKhau.setText(str(mat_khau or ""))
                self.ui_seller.txtTenShop.setText(str(shop or ""))
        except Exception as e:
            print(f"Error loading seller details: {e}")

    def generate_new_seller_id(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT MaNguoiBan FROM NGUOI_BAN")
            ids = [r[0] for r in cursor.fetchall() if r[0] and r[0].startswith("NB")]
            conn.close()
            max_val = 0
            for i in ids:
                num = i[2:]
                if num.isdigit():
                    max_val = max(max_val, int(num))
            return f"NB{max_val + 1:02d}"
        except Exception as e:
            print(e)
            return "NB99"

    def seller_action_them(self):
        # Mở form ở chế độ THÊM
        self.selected_seller_id = None
        self.seller_clear_fields()
        self._seller_action = "THEM"
        self._set_seller_form_enabled(True)
        self._set_seller_edit_button(True)

    def _seller_do_insert(self):
        ho_ten = self.ui_seller.txtTenNguoiBan.text().strip()
        sdt = self.ui_seller.txtSoDienThoai.text().strip()
        email = self.ui_seller.txtEmail.text().strip()
        mat_khau = self.ui_seller.txtMatKhau.text().strip()
        shop = self.ui_seller.txtTenShop.text().strip()

        if not ho_ten:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Vui lòng nhập Tên người bán!")
            return
        if not mat_khau:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Vui lòng nhập Mật khẩu đăng nhập!")
            return

        ma_nb = self.generate_new_seller_id()

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO NGUOI_BAN (MaNguoiBan, MatKhau, HoTen, SoDienThoai, Email, TenCuaHang, DiaChi) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (ma_nb, mat_khau, ho_ten, sdt, email, shop, ""))
            conn.commit()
            conn.close()

            self.load_seller_data()
            self.seller_clear_fields()
            self._seller_reset_mode()
            QMessageBox.information(self, "Thành công", f"Đã thêm người bán {ma_nb} thành công.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm người bán: {e}")

    def seller_action_save(self):
        if not hasattr(self, 'selected_seller_id') or not self.selected_seller_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một người bán trên bảng để sửa!")
            return

        ho_ten = self.ui_seller.txtTenNguoiBan.text().strip()
        sdt = self.ui_seller.txtSoDienThoai.text().strip()
        email = self.ui_seller.txtEmail.text().strip()
        mat_khau = self.ui_seller.txtMatKhau.text().strip()
        shop = self.ui_seller.txtTenShop.text().strip()

        if not ho_ten:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Tên người bán không được để trống!")
            return
        if not mat_khau:
            QMessageBox.warning(self, "Lỗi dữ liệu", "Mật khẩu không được để trống!")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE NGUOI_BAN SET HoTen = ?, SoDienThoai = ?, Email = ?, MatKhau = ?, TenCuaHang = ? WHERE MaNguoiBan = ?",
                           (ho_ten, sdt, email, mat_khau, shop, self.selected_seller_id))
            conn.commit()
            conn.close()

            self.load_seller_data()
            self._seller_reset_mode()
            QMessageBox.information(self, "Thành công", f"Cập nhật thành công người bán {self.selected_seller_id}.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật người bán: {e}")

    def seller_action_xoa(self):
        if not hasattr(self, 'selected_seller_id') or not self.selected_seller_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một người bán trên bảng để xóa!")
            return

        confirm = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa người bán {self.selected_seller_id} không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM NGUOI_BAN WHERE MaNguoiBan = ?", (self.selected_seller_id,))
                conn.commit()
                conn.close()

                self.load_seller_data()
                self.seller_clear_fields()
                self.selected_seller_id = None
                QMessageBox.information(self, "Thành công", "Đã xóa người bán khỏi cơ sở dữ liệu.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa người bán: {e}")

    def seller_export_excel(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Lưu file Excel người bán", "", "Excel Files (*.xlsx);;All Files (*)"
        )
        if not path:
            return

        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "NguoiBan"

            headers = ["Mã Người Bán", "Tên Người Bán", "Số Điện Thoại", "Email", "Tên Shop"]
            ws.append(headers)

            for row in range(self.ui_seller.tblSeller.rowCount()):
                row_data = []
                for col in range(self.ui_seller.tblSeller.columnCount()):
                    item = self.ui_seller.tblSeller.item(row, col)
                    row_data.append(item.text() if item else "")
                ws.append(row_data)

            wb.save(path)
            QMessageBox.information(self, "Thành công", f"Đã xuất dữ liệu Excel thành công tại:\n{path}")
        except ImportError:
            QMessageBox.critical(self, "Lỗi", "Vui lòng cài đặt openpyxl bằng lệnh: pip install openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file Excel: {e}")

    def seller_action_clear(self):
        self.ui_seller.tblSeller.setRowCount(0)
        self.seller_clear_fields()
        self.selected_seller_id = None
        self._seller_reset_mode()
        self.ui_seller.lblStatus.setText("Trạng thái: Đã xóa dữ liệu trên bảng hiển thị.")

    def seller_clear_fields(self):
        self.ui_seller.txtTenNguoiBan.clear()
        self.ui_seller.txtSoDienThoai.clear()
        self.ui_seller.txtEmail.clear()
        self.ui_seller.txtMatKhau.clear()
        self.ui_seller.txtTenShop.clear()

    def seller_search(self):
        search_text = self.ui_seller.txtSearch.text().strip()
        if not search_text:
            self.load_seller_data()
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            query = """
                SELECT MaNguoiBan, HoTen, SoDienThoai, Email, TenCuaHang 
                FROM NGUOI_BAN 
                WHERE HoTen LIKE ? OR TenCuaHang LIKE ?
            """
            cursor.execute(query, (f"%{search_text}%", f"%{search_text}%"))
            results = cursor.fetchall()
            conn.close()

            self.populate_table(self.ui_seller.tblSeller, results)
            self.ui_seller.lblStatus.setText(f"Trạng thái: Tìm thấy {len(results)} người bán.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tìm kiếm người bán: {e}")

    def seller_refresh(self):
        self.ui_seller.txtSearch.clear()
        self.load_seller_data()
        self.ui_seller.lblStatus.setText("Trạng thái: Đã làm mới dữ liệu người bán.")

