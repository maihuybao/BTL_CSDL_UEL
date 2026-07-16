import sys
import os
import sqlite3
from PyQt6 import QtWidgets, QtGui, QtCore

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from Login import Ui_LoginDialog
from Dashboard.Dashboard_Ex import DashboardEx as RealDashboardEx


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class IntegratedDashboard(RealDashboardEx):
    def __init__(self, emp_id, login_window=None):
        super().__init__()

        self.emp_id = emp_id
        self.login_window = login_window

        if hasattr(self.ui, 'lblUserScope'):
            # Hiển thị thông tin mã Người bán đăng nhập thành công lên giao diện Dashboard
            self.ui.lblUserScope.setText(f"Xin chào, Người bán ID: {self.emp_id}")

        if hasattr(self.ui, 'btnMenuLogout'):
            self.ui.btnMenuLogout.clicked.connect(self.process_logout)

    def process_logout(self):
        if self.login_window:
            self.login_window.show()
        self.close()


class LoginEx(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)

        self.center_window()
        self.setupSignalAndSlot()

    def center_window(self):
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setupSignalAndSlot(self):
        self.ui.btnLogin.clicked.connect(self.process_login)
        self.ui.btnExit.clicked.connect(self.close)
        # Cho phép nhấn phím Enter trên ô mật khẩu để đăng nhập nhanh
        self.ui.txtPassword.returnPressed.connect(self.process_login)

    def process_login(self):
        username = self.ui.txtUsername.text().strip()
        password = self.ui.txtPassword.text().strip()

        # Kiểm tra dữ liệu rỗng đầu vào
        if not username or not password:
            self.ui.lblStatus.setText("❌ Vui lòng điền đầy đủ tài khoản & mật khẩu!")
            return

        # ---------------------------------------------------------
        # KẾT NỐI DATABASE SQLITE ĐỂ KIỂM TRA ĐĂNG NHẬP
        # ---------------------------------------------------------
        db_path = "customer_db.sqlite"  # Tên file db của bạn

        if not os.path.exists(db_path):
            self.ui.lblStatus.setText("❌ Không tìm thấy file dữ liệu customer_db.sqlite!")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Thực thi câu lệnh SQL tìm kiếm Người bán khớp tài khoản và mật khẩu
            cursor.execute(
                "SELECT MaNguoiBan, HoTen FROM NGUOI_BAN WHERE MaNguoiBan = ? AND MatKhau = ?",
                (username, password)
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                # Đăng nhập thành công
                seller_id = result[0]
                seller_name = result[1]
                self.ui.lblStatus.setText("")  # Xóa dòng báo lỗi

                # Mở trang Dashboard chính và truyền Mã người bán đã đăng nhập vào
                self.open_dashboard_window(seller_id)
            else:
                # Đăng nhập thất bại
                self.ui.lblStatus.setText("❌ Tài khoản hoặc mật khẩu không chính xác!")

        except sqlite3.Error as e:
            self.ui.lblStatus.setText(f"⚠️ Lỗi kết nối CSDL: {str(e)}")

    def open_dashboard_window(self, emp_id):
        self.dashboard_window = IntegratedDashboard(emp_id, login_window=self)
        self.dashboard_window.show()
        self.hide()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginEx()
    login_window.show()
    sys.exit(app.exec())