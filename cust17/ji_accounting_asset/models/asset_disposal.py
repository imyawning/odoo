from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta

class AssetDisposal(models.Model):
    _name = 'asset.disposal'
    _description = '資產報廢單'

    name = fields.Char(string='處置單號', required=True, copy=False, default='New')
    date = fields.Date(string='異動日期', required=True, default=fields.Date.context_today)
    applicant_id = fields.Many2one('res.users', string='申請人', required=True, default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', '草稿'),
        ('confirm', '已確認')
    ], string='狀態', default='draft', required=True, readonly=True)
    move_id = fields.Many2one('account.move', string='傳票', readonly=True)
    line_ids = fields.One2many('asset.disposal.line', 'disposal_id', string='報廢明細')
    

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('asset.disposal') or 'New'
        return super().create(vals)

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise models.ValidationError('只有草稿狀態的報廢單可以刪除！')
        return super().unlink()

    def action_confirm(self):
        config = self.env['asset.config'].search([], limit=1)
        for disposal in self:
            if config and config.asset_close_date and disposal.date <= config.asset_close_date:
                raise UserError('異動日期不得早於或等於關帳日期（%s）！' % config.asset_close_date)
            if disposal.state != 'draft':
                raise UserError('只有草稿狀態才能拋轉傳票！')
            if not config or not config.loss_account_id or not config.asset_journal_id:
                raise UserError('請先在固定資產設定中設定「資產處分損失科目」與「預設帳別」！')
            # 新增：檢查是否需先提列折舊
            if config.depreciate_in_disposal:
                for line in disposal.line_ids:
                    asset = line.asset_id
                    if not asset:
                        continue
                    disposal_month = disposal.date.replace(day=1)
                    next_month = (disposal_month + relativedelta(months=1))
                    depreciation_count = self.env['asset.depreciation'].search_count([
                        ('asset_id', '=', asset.id),
                        ('date', '>=', disposal_month),
                        ('date', '<', next_month)
                    ])
                    if depreciation_count == 0:
                        raise UserError(f'資產「{asset.name}」{asset.code if hasattr(asset, "code") else ""} 本月尚未提列折舊，請先提列折舊再進行報廢作業！')
            move_lines = []
            total_asset = total_depr = total_loss = 0.0
            asset_account = None
            depr_account = None
            for line in disposal.line_ids:
                total_asset += line.amount
                total_depr += line.accumulated_depreciation
                total_loss += line.value
                asset_account = line.asset_id.asset_account_id.id
                depr_account = line.asset_id.asset_account_acc_id.id
            if not asset_account or not depr_account:
                raise UserError('資產主檔未設定科目！')
            # 借：處分損失
            move_lines.append((0, 0, {
                'account_id': config.loss_account_id.id,
                'debit': total_loss,
                'credit': 0.0,
                'name': '資產處分損失',
            }))
            # 借：累積折舊
            move_lines.append((0, 0, {
                'account_id': depr_account,
                'debit': total_depr,
                'credit': 0.0,
                'name': '累積折舊',
            }))
            # 貸：固定資產
            move_lines.append((0, 0, {
                'account_id': asset_account,
                'debit': 0.0,
                'credit': total_asset,
                'name': '固定資產',
            }))
            move = self.env['account.move'].create({
                'date': disposal.date,
                'journal_id': config.asset_journal_id.id,
                'ref': disposal.name,
                'line_ids': move_lines,
            })
            disposal.move_id = move.id
            disposal.state = 'confirm'
            # 更新所有明細的資產狀態為 written_off
            for line in disposal.line_ids:
                if line.asset_id:
                    line.asset_id.state = 'written_off'

    def action_draft(self):
        config = self.env['asset.config'].search([], limit=1)
        for disposal in self:
            if config and config.asset_close_date and disposal.date <= config.asset_close_date:
                raise UserError('異動日期不得早於或等於關帳日期（%s）！' % config.asset_close_date)
            if disposal.state != 'confirm':
                raise UserError('只有已確認狀態才能還原為草稿！')
            if disposal.move_id:
                if disposal.move_id.state == 'posted':
                    raise UserError('傳票已過帳，不可還原！')
                disposal.move_id.button_cancel()
                disposal.move_id.unlink()
                disposal.move_id = False
            disposal.state = 'draft'
            # 還原所有明細的資產狀態：累積折舊>0為depreciation，否則confirm
            for line in disposal.line_ids:
                if line.asset_id:
                    if line.asset_id.accumulated_depreciation > 0:
                        line.asset_id.state = 'depreciation'
                    else:
                        line.asset_id.state = 'confirm'

class AssetDisposalLine(models.Model):
    _name = 'asset.disposal.line'
    _description = '資產報廢明細'

    disposal_id = fields.Many2one('asset.disposal', string='報廢單', required=True, ondelete='cascade')
    sequence = fields.Integer(string='項次', default=1)
    asset_id = fields.Many2one('asset.master', string='財產編號', required=True)
    asset_name = fields.Char(string='名稱')
    unit = fields.Char(string='單位')
    quantity = fields.Float(string='數量', default=1.0, readonly=True)
    amount = fields.Float(string='金額')
    accumulated_depreciation = fields.Float(string='累計折舊')
    value = fields.Float(string='帳面價值')
    reason = fields.Char(string='原因')

    @api.model
    def create(self, vals):
        asset = self.env['asset.master'].browse(vals.get('asset_id'))
        vals['asset_name'] = asset.name or ''
        vals['unit'] = asset.unit.name if asset.unit else ''
        vals['amount'] = asset.amount
        vals['accumulated_depreciation'] = asset.accumulated_depreciation
        vals['value'] = asset.value
        if not vals.get('sequence'):
            disposal_id = vals.get('disposal_id')
            if disposal_id:
                lines = self.env['asset.disposal.line'].search([('disposal_id', '=', disposal_id)])
                vals['sequence'] = (max(lines.mapped('sequence')) if lines else 0) + 1
            else:
                vals['sequence'] = 1
        return super().create(vals)

    def write(self, vals):
        if 'asset_id' in vals:
            asset = self.env['asset.master'].browse(vals['asset_id'])
            vals['asset_name'] = asset.name or ''
            vals['unit'] = asset.unit.name if asset.unit else ''
            vals['amount'] = asset.amount
            vals['accumulated_depreciation'] = asset.accumulated_depreciation
            vals['value'] = asset.value
        return super().write(vals)

    @api.onchange('disposal_id')
    def _onchange_sequence(self):
        if self.disposal_id:
            exist_seqs = [line.sequence for line in self.disposal_id.line_ids if line != self and line.sequence]
            self.sequence = max(exist_seqs, default=0) + 1

    @api.constrains('asset_id')
    def _check_duplicate_asset_id_global(self):
        for rec in self:
            if not rec.asset_id:
                continue
            # 查詢全系統草稿或已確認狀態下，是否有相同財產編號（排除自己）
            domain = [
                ('id', '!=', rec.id),
                ('asset_id', '=', rec.asset_id.id),
                ('disposal_id.state', 'in', ['draft', 'confirm'])
            ]
            exists = self.search_count(domain)
            if exists:
                raise ValidationError('該財產編號已存在其他草稿或已確認的報廢明細，不可重複選擇！')

    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        if self.asset_id:
            self.asset_name = self.asset_id.name or ''
            self.unit = self.asset_id.unit.name if self.asset_id.unit else ''
            self.amount = self.asset_id.amount
            self.accumulated_depreciation = self.asset_id.accumulated_depreciation
            self.value = self.asset_id.value
            # 檢查全系統唯一
            domain = [
                ('asset_id', '=', self.asset_id.id),
                ('disposal_id.state', 'in', ['draft', 'confirm'])
            ]
            if self.id and isinstance(self.id, int):
                domain.insert(0, ('id', '!=', self.id))
            exists = self.env['asset.disposal.line'].search_count(domain)
            if exists:
                return {
                    'warning': {
                        'title': '重複財產編號',
                        'message': '該財產編號已存在其他草稿或已確認的報廢明細，不可重複選擇！',
                    }
                }
        else:
            self.asset_name = ''
            self.unit = ''
            self.amount = 0.0
            self.accumulated_depreciation = 0.0
            self.value = 0.0
