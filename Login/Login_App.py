import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt6.QtWidgets import QApplication

import Login_Ex as login_mod
from Dashboard.Dashboard_Ex import IntegratedDashboard as RealDashboardEx


class IntegratedDashboard(RealDashboardEx):
    def __init__(self, emp_id, login_window=None):
        super().__init__()

        self.emp_id = emp_id
        self.login_window = login_window

        if hasattr(self.ui, 'lblUserScope'):
            self.ui.lblUserScope.setText(f"Xin chào, Nhân viên ID: {self.emp_id} (Admin)")

        if hasattr(self.ui, 'btnMenuLogout'):
            self.ui.btnMenuLogout.clicked.connect(self.process_logout)

    def process_logout(self):
        if self.login_window:
            self.login_window.show()
        self.close()


login_mod.IntegratedDashboard = IntegratedDashboard


def main():
    app = QApplication(sys.argv)

    login_window = login_mod.LoginEx()
    login_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()