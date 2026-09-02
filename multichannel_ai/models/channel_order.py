# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ChannelOrder(models.Model):
    _name = 'channel.order'
    _description = 'Channel Order'
    _order = 'order_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(string='Order Reference', required=True, tracking=True)
    channel_id = fields.Many2one('channel.config', string='Channel', required=True, tracking=True)
    channel_order_id = fields.Char(string='Channel Order ID', required=True, tracking=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    customer_name = fields.Char(string='Customer Name')
    customer_email = fields.Char(string='Customer Email')
    customer_phone = fields.Char(string='Customer Phone')
    shipping_address = fields.Text(string='Shipping Address')
    billing_address = fields.Text(string='Billing Address')
    order_date = fields.Datetime(string='Order Date', default=fields.Datetime.now, tracking=True)
    notes = fields.Text(string='Notes')
    state = fields.Selection([('pending', 'Pending'), ('confirmed', 'Confirmed'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded')], string='Status', default='pending', tracking=True)
    channel_state = fields.Char(string='Channel State')
    subtotal = fields.Float(string='Subtotal', compute='_compute_totals', store=True)
    shipping_cost = fields.Float(string='Shipping Cost')
    platform_fee = fields.Float(string='Platform Fee')
    payment_fee = fields.Float(string='Payment Fee')
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_totals', store=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_totals', store=True)
    line_ids = fields.One2many('channel.order.line', 'order_id', string='Order Lines')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', copy=False)
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_delivery_count')
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')
    
    @api.depends('line_ids.subtotal', 'line_ids.tax_amount', 'line_ids.total_amount', 'shipping_cost', 'platform_fee', 'payment_fee')
    def _compute_totals(self):
        for order in self:
            order.subtotal = sum(line.subtotal for line in order.line_ids)
            order.tax_amount = sum(line.tax_amount for line in order.line_ids)
            order.total_amount = order.subtotal + order.tax_amount + order.shipping_cost + order.platform_fee + order.payment_fee
    
    @api.depends('sale_order_id')
    def _compute_delivery_count(self):
        for order in self:
            if order.sale_order_id:
                order.delivery_count = self.env['stock.picking'].search_count([('origin', '=', order.sale_order_id.name)])
            else:
                order.delivery_count = 0
    
    @api.depends('sale_order_id')
    def _compute_invoice_count(self):
        for order in self:
            if order.sale_order_id:
                order.invoice_count = self.env['account.move'].search_count([('invoice_origin', '=', order.sale_order_id.name), ('move_type', '=', 'out_invoice')])
            else:
                order.invoice_count = 0
    
    @api.model
    def create_from_webhook(self, channel_code, channel_data):
        channel = self.env['channel.config'].search([('code', '=', channel_code)], limit=1)
        if not channel:
            raise ValidationError(_('Channel %s not found') % channel_code)
        existing = self.search([('channel_order_id', '=', channel_data.get('order_id', '')), ('channel_id', '=', channel.id)])
        if existing:
            return existing
        order = self.create({'name': 'New', 'channel_id': channel.id, 'channel_order_id': channel_data.get('order_id', ''), 'customer_name': channel_data.get('customer_name', ''), 'customer_email': channel_data.get('customer_email', ''), 'customer_phone': channel_data.get('customer_phone', ''), 'shipping_address': channel_data.get('shipping_address', ''), 'order_date': channel_data.get('order_date', fields.Datetime.now()), 'state': 'pending'})
        for item in channel_data.get('items', []):
            self.env['channel.order.line'].create({'order_id': order.id, 'name': item.get('name', ''), 'product_id': item.get('product_id', False), 'channel_product_id': item.get('channel_product_id', ''), 'quantity': item.get('quantity', 1), 'unit_price': item.get('unit_price', 0), 'subtotal': item.get('subtotal', 0)})
        return order
    
    def action_create_sale_order(self):
        self.ensure_one()
        if self.sale_order_id:
            return {'type': 'ir.actions.act_window', 'res_model': 'sale.order', 'res_id': self.sale_order_id.id, 'view_mode': 'form'}
        sale_obj = self.env['sale.order']
        partner = self.partner_id or self.env['res.partner'].create({'name': self.customer_name or 'Channel Customer', 'email': self.customer_email, 'phone': self.customer_phone})
        sale_order = sale_obj.create({'partner_id': partner.id, 'partner_shipping_id': partner.id, 'partner_invoice_id': partner.id, 'channel_id': self.channel_id.id, 'channel_order_id': self.id, 'channel_order_code': self.channel_order_id, 'channel_shipping_fee': self.shipping_cost, 'channel_discount': self.platform_fee, 'origin': self.name, 'note': self.notes, 'order_line': [(0, 0, {'product_id': line.product_id.id if line.product_id else False, 'name': line.name, 'product_uom_qty': line.quantity, 'price_unit': line.unit_price}) for line in self.line_ids]})
        self.write({'sale_order_id': sale_order.id, 'state': 'confirmed'})
        return {'type': 'ir.actions.act_window', 'res_model': 'sale.order', 'res_id': sale_order.id, 'view_mode': 'form'}
    
    def action_create_delivery(self):
        self.ensure_one()
        if not self.sale_order_id:
            raise ValidationError(_('Create Sale Order first'))
        return self.sale_order_id.action_view_delivery()
    
    def action_create_invoice(self):
        self.ensure_one()
        if not self.sale_order_id:
            raise ValidationError(_('Create Sale Order first'))
        return self.sale_order_id.action_invoice_create()
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})


class ChannelOrderLine(models.Model):
    _name = 'channel.order.line'
    _description = 'Channel Order Line'
    _order = 'id'
    order_id = fields.Many2one('channel.order', string='Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Odoo Product')
    channel_product_id = fields.Char(string='Channel Product ID')
    name = fields.Char(string='Product Name', required=True)
    quantity = fields.Float(string='Quantity', default=1)
    unit_price = fields.Float(string='Unit Price')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_subtotal', store=True)
    total_amount = fields.Float(string='Total', compute='_compute_subtotal', store=True)
    
    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
            line.tax_amount = line.subtotal * 0.07
            line.total_amount = line.subtotal + line.tax_amount


class ProductCategoryMapping(models.Model):
    _name = 'product.category.mapping'
    _description = 'Product Category Mapping'
    channel_id = fields.Many2one('channel.config', string='Channel', required=True)
    channel_category_id = fields.Char(string='Channel Category ID', required=True)
    channel_category_name = fields.Char(string='Channel Category Name')
    odoo_category_id = fields.Many2one('product.category', string='Odoo Category', required=True)
    auto_map = fields.Boolean(string='Auto Map', default=True)


class PriceRecommendation(models.Model):
    _name = 'price.recommendation'
    _description = 'Price Recommendation'
    _order = 'create_date desc'
    product_id = fields.Many2one('product.product', string='Product', required=True)
    channel_id = fields.Many2one('channel.config', string='Channel', required=True)
    ai_recommended_price = fields.Float(string='AI Recommended Price')
    recommended_reasoning = fields.Text(string='Recommendation Reasoning')
    cost_price = fields.Float(string='Cost Price')
    gross_profit = fields.Float(string='Gross Profit', compute='_compute_profit', store=True)
    gross_margin = fields.Float(string='Gross Margin %', compute='_compute_margin', store=True)
    platform_fee = fields.Float(string='Platform Fee')
    payment_fee = fields.Float(string='Payment Fee')
    shipping_fee = fields.Float(string='Shipping Fee')
    vat_amount = fields.Float(string='VAT Amount')
    net_profit = fields.Float(string='Net Profit', compute='_compute_net_profit', store=True)
    status = fields.Selection([('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('applied', 'Applied')], string='Status', default='pending')
    
    @api.depends('ai_recommended_price', 'cost_price')
    def _compute_profit(self):
        for rec in self: rec.gross_profit = rec.ai_recommended_price - rec.cost_price
    
    @api.depends('gross_profit', 'ai_recommended_price')
    def _compute_margin(self):
        for rec in self: rec.gross_margin = (rec.gross_profit / rec.ai_recommended_price * 100) if rec.ai_recommended_price else 0.0
    
    @api.depends('platform_fee', 'payment_fee', 'shipping_fee', 'vat_amount', 'gross_profit')
    def _compute_net_profit(self):
        for rec in self: rec.net_profit = rec.gross_profit - rec.platform_fee - rec.payment_fee - rec.shipping_fee - rec.vat_amount