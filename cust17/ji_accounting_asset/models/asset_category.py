# 位於 models/asset_category.py
from odoo import models, fields
# 移除頂部的 "from . import asset_master"

class AssetCategory(models.Model):
    _name = 'asset.category'

    def some_function(self):
        from . import asset_master  # <--- 將導入移至函數內部
        # ...
        self.env['asset.master'].search(...)