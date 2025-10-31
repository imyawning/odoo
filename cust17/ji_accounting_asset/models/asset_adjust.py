# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetAdjust(models.Model):
    _name = 'asset.adjust'
    _description = 'Asset Adjust'

    name = fields.Char('Name', required=True)
    # 未來您會在這裡添加一個 One2many 欄位
    # line_ids = fields.One2many('asset.adjust.line', 'adjust_id', string='Lines')

# VVVV 這是新增的類別 VVVV
class AssetAdjustLine(models.Model):
    _name = 'asset.adjust.line'
    _description = 'Asset Adjust Line'

    adjust_id = fields.Many2one('asset.adjust', string='Adjust')
    name = fields.Char('Name')