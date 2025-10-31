# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    # 在這裡添加您需要客製化的欄位
    # example_field = fields.Char('Example')