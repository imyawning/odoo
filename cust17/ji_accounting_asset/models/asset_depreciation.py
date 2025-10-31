# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetDepreciation(models.Model):
    _name = 'asset.depreciation'
    _description = 'Asset Depreciation'

    name = fields.Char('Name', required=True)
    # 您未來會在這裡添加折舊相關的欄位