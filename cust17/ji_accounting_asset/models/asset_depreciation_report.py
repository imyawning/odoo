# -*- coding: utf-8 -*-
from odoo import models, fields, api

# VVVV 這是 'model_asset_depreciation_report' VVVV
class AssetDepreciationReport(models.Model):
    _name = 'asset.depreciation.report'
    _description = 'Asset Depreciation Report Data'
    _auto = False  # 這通常是一個 SQL 視圖或臨時模型

    name = fields.Char('Name')
    # ... 其他報表欄位 ...

# VVVV 這是 'model_asset_depreciation_report_wizard' VVVV
class AssetDepreciationReportWizard(models.TransientModel):
    _name = 'asset.depreciation.report.wizard'
    _description = 'Asset Depreciation Report Wizard'

    name = fields.Char('Name', default='Default')
    # ... 查詢條件欄位 ...

# 這是 QWeb 報表解析器，保留它
class AssetDepreciationReportQWeb(models.AbstractModel):
    _name = 'report.ji_accounting_asset.report_asset_depreciation'
    _description = 'Asset Depreciation Report (QWeb)'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['asset.depreciation.report.wizard'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'asset.depreciation.report.wizard',
            'data': data,
            'docs': docs,
        }