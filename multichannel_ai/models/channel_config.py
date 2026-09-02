# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ChannelConfig(models.Model):
    _name = 'channel.config'
    _description = 'E-Commerce Channel'
    _order = 'sequence, name'
    
    name = fields.Char(string='Channel Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', default=10)
    icon = fields.Char(string='Icon', default='🛒')
    color = fields.Integer(string='Color Index', default=0)
    
    api_key = fields.Char(string='API Key', groups='base.group_system')
    api_secret = fields.Char(string='API Secret', groups='base.group_system')
    shop_id = fields.Char(string='Shop ID')
    access_token = fields.Char(string='Access Token', groups='base.group_system')
    
    commission_rate = fields.Float(string='Commission (%)', default=5.0)
    payment_fee_rate = fields.Float(string='Payment Fee (%)', default=2.0)
    shipping_fee_rate = fields.Float(string='Shipping Subsidy (%)', default=2.5)
    
    default_warehouse_id = fields.Many2one('stock.warehouse', string='Default Warehouse')
    default_pricelist_id = fields.Many2one('product.pricelist', string='Default Pricelist')
    
    product_count = fields.Integer(string='Products', compute='_compute_counts')
    order_count = fields.Integer(string='Orders', compute='_compute_counts')
    last_sync = fields.Datetime(string='Last Sync')
    
    _sql_constraints = [('code_unique', 'unique(code)', 'Code must be unique!')]
    
    @api.depends()
    def _compute_counts(self):
        for rec in self:
            rec.product_count = self.env['channel.product'].search_count([('channel_id', '=', rec.id)])
            rec.order_count = self.env['channel.order'].search_count([('channel_id', '=', rec.id)])
    
    def test_connection(self):
        self.ensure_one()
        try:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'title': _('Connection Test'), 'message': _('Connection to %s successful' % self.name), 'type': 'success'}
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'title': _('Connection Failed'), 'message': str(e), 'type': 'danger'}
            }
    
    def action_view_products(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Products - %s' % self.name),
            'res_model': 'channel.product',
            'view_mode': 'tree,form',
            'domain': [('channel_id', '=', self.id)],
        }
    
    def action_view_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Orders - %s' % self.name),
            'res_model': 'channel.order',
            'view_mode': 'tree,form',
            'domain': [('channel_id', '=', self.id)],
        }