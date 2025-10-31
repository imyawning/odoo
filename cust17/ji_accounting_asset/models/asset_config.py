# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetConfig(models.Model):
    _name = 'asset.config'
    _description = 'Asset Config'

    name = fields.Char('Name', required=True)