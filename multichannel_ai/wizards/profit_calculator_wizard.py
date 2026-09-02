# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProfitCalculatorWizard(models.TransientModel):
    """Profit Calculator Wizard"""
    _name = 'profit.calculator.wizard'
    _description = 'Profit Calculator Wizard'
    
    product_id = fields.Many2one('product.product', string='Product')
    channel_id = fields.Many2one('channel.config', string='Channel')
    selling_price = fields.Float(string='Selling Price (incl. VAT)', required=True)
    cost = fields.Float(string='Cost', required=True)
    
    # Computed results
    price_excl_vat = fields.Float(string='Price (excl. VAT)', compute='_compute_results', readonly=True)
    vat_collected = fields.Float(string='VAT Collected', compute='_compute_results', readonly=True)
    platform_fee = fields.Float(string='Platform Fee', compute='_compute_results', readonly=True)
    payment_fee = fields.Float(string='Payment Fee', compute='_compute_results', readonly=True)
    shipping_subsidy = fields.Float(string='Shipping Subsidy', compute='_compute_results', readonly=True)
    total_fees = fields.Float(string='Total Fees', compute='_compute_results', readonly=True)
    gross_profit = fields.Float(string='Gross Profit', compute='_compute_results', readonly=True)
    net_profit = fields.Float(string='Net Profit', compute='_compute_results', readonly=True)
    gross_margin = fields.Float(string='Gross Margin %', compute='_compute_results', readonly=True)
    net_margin = fields.Float(string='Net Margin %', compute='_compute_results', readonly=True)
    break_even_price = fields.Float(string='Break-even Price', compute='_compute_results', readonly=True)
    
    target_margin = fields.Float(string='Target Margin %', default=30.0)
    recommended_price = fields.Float(string='AI Recommended Price', compute='_compute_results', readonly=True)
    
    @api.depends('selling_price', 'cost', 'channel_id.code', 'target_margin')
    def _compute_results(self):
        for rec in self:
            if not rec.channel_id:
                continue
            ai_engine = rec.env['ai.engine'].get_default_engine()
            profit = ai_engine.calculate_profit(
                rec.selling_price,
                rec.cost,
                rec.channel_id.code
            )
            rec.price_excl_vat = profit['price_excl_vat']
            rec.vat_collected = profit['vat_collected']
            rec.platform_fee = profit['platform_fee']
            rec.payment_fee = profit['payment_fee']
            rec.shipping_subsidy = profit['shipping_subsidy']
            rec.total_fees = profit['total_fees']
            rec.gross_profit = profit['gross_profit']
            rec.net_profit = profit['net_profit']
            rec.gross_margin = profit['gross_margin']
            rec.net_margin = profit['net_margin']
            rec.break_even_price = profit['break_even_price']
            
            # AI recommended price
            product_data = {
                'name': rec.product_id.name if rec.product_id else 'Product',
                'cost': rec.cost,
                'category': 'IT Equipment'
            }
            ai_rec = ai_engine.recommend_price(
                product_data, 
                rec.channel_id.code, 
                rec.target_margin
            )
            rec.recommended_price = ai_rec.get('selling_price', 0)