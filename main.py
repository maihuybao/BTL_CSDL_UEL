"""Entry point chính (shim).

Logic thật đã tách vào package app/. File này giữ để:
  - `python Main_Controller.py` vẫn chạy ứng dụng như cũ.
  - `from Main_Controller import apply_order_status_effects, recalc_order_total`
    (test_order_sync.py) vẫn hoạt động.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Re-export cho test và mã cũ tham chiếu qua Main_Controller
from app.config import DB_PATH  # noqa: F401
from app.db_logic import apply_order_status_effects, recalc_order_total  # noqa: F401
from app.dashboard import DashboardEx  # noqa: F401
from app.login import LoginEx  # noqa: F401
from app.app_main import main, force_light_theme  # noqa: F401

if __name__ == "__main__":
    main()
