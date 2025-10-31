# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    # 在這裡添加您需要客製化的欄位
    # example_field = fields.Char('Example')