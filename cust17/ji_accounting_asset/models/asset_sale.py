# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetSale(models.Model):
    _name = 'asset.sale'
    _description = 'Asset Sale'

    name = fields.Char('Name', required=True)
    # 未來您會在這裡添加一個 One2many 欄位
    # line_ids = fields.One2many('asset.sale.line', 'sale_id', string='Lines')

# VVVV 這是新增的類別 VVVV
class AssetSaleLine(models.Model):
    _name = 'asset.sale.line'
    _description = 'Asset Sale Line'

    sale_id = fields.Many2one('asset.sale', string='Sale')
    name = fields.Char('Name')