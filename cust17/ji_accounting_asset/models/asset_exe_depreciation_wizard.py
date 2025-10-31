# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetExeDepreciationWizard(models.TransientModel):
    _name = 'asset.exe.depreciation.wizard'
    _description = 'Execute Depreciation Wizard'

    name = fields.Char('Name', default='Default') # 僅為佔位符
    # 精靈通常用於接收用戶輸入的欄位