# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    channel_id = fields.Many2one(
        'channel.config', string='Channel', index=True, readonly=True,
        states={'draft': [('readonly', False)]}
    )
    channel_order_id = fields.Many2one(
        'channel.order', string='Channel Order', index=True, readonly=True
    )
    channel_order_code = fields.Char(
        string='Channel Order Code', readonly=True, copy=False
    )
    channel_shipping_fee = fields.Float(
        string='Channel Shipping Fee', readonly=True
    )
    channel_discount = fields.Float(
        string='Channel Discount', readonly=True
    )
    
    @api.onchange('channel_id')
    def _onchange_channel_id(self):
        if self.channel_id and self.channel_id.default_warehouse_id:
            self.warehouse_id = self.channel_id.default_warehouse_id
        if self.channel_id and self.channel_id.default_pricelist_id:
            self.pricelist_id = self.channel_id.default_pricelist_id
    
    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()
        if self.channel_id:
            vals['invoice_origin'] = '%s - %s' % (vals.get('invoice_origin', ''), self.channel_order_code or '')
        return vals