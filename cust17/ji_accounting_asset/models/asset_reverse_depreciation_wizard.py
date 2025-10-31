# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetReverseDepreciationWizard(models.TransientModel):
    _name = 'asset.reverse.depreciation.wizard'
    _description = 'Reverse Depreciation Wizard'
    
    name = fields.Char('Name', default='Default') # 僅為佔位符