"""DashboardEx: cửa sổ chính, lắp ráp từ 5 mixin theo domain.

Thứ tự kế thừa đặt các mixin trước QMainWindow để super().__init__() trong
BaseMixin.__init__ đi tới QMainWindow qua MRO.
"""
from PyQt6.QtWidgets import QMainWindow

from app.dashboard.base import BaseMixin
from app.dashboard.statistics import StatisticsMixin
from app.dashboard.charts import ChartsMixin
from app.dashboard.product import ProductMixin
from app.dashboard.seller import SellerMixin


class DashboardEx(BaseMixin, StatisticsMixin, ChartsMixin, ProductMixin, SellerMixin, QMainWindow):
    pass
