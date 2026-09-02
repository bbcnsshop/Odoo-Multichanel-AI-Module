# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class MainController(http.Controller):
    """Main Controller for Multi-Channel E-Commerce"""
    
    @http.route('/multichannel/dashboard', type='http', auth='user')
    def dashboard(self, **kwargs):
        """Dashboard showing all channel summaries"""
        channels = request.env['channel.config'].search([])
        
        # Get summary data for each channel
        summary_data = []
        for channel in channels:
            product_count = request.env['channel.product'].search_count([
                ('channel_id', '=', channel.id),
                ('state', '=', 'active')
            ])
            order_count = request.env['channel.order'].search_count([
                ('channel_id', '=', channel.id)
            ])
            pending_order = request.env['channel.order'].search_count([
                ('channel_id', '=', channel.id),
                ('state', '=', 'pending')
            ])
            
            summary_data.append({
                'channel': channel,
                'product_count': product_count,
                'order_count': order_count,
                'pending_order': pending_order,
            })
        
        return request.render('multichannel_ai.dashboard_template', {
            'summary_data': summary_data,
        })
    
    @http.route('/multichannel/sync', type='http', auth='user')
    def sync_page(self, **kwargs):
        """Manual sync page"""
        return request.render('multichannel_ai.sync_template', {})
    
    @http.route('/multichannel/api/products', type='json', auth='user', methods=['GET'])
    def get_products(self, channel_id=None, **kwargs):
        """API to get products for a channel"""
        domain = [('state', '=', 'active')]
        if channel_id:
            domain.append(('channel_id', '=', int(channel_id)))
        
        products = request.env['channel.product'].search_read(domain, [
            'name', 'channel_id', 'channel_price', 'qty_available', 'state'
        ])
        
        return products
    
    @http.route('/multichannel/api/pricing', type='json', auth='user', methods=['POST'])
    def calculate_pricing(self, **kwargs):
        """API to calculate pricing with AI"""
        product_id = kwargs.get('product_id')
        channel_code = kwargs.get('channel_code')
        
        if not product_id or not channel_code:
            return {'error': 'Missing product_id or channel_code'}
        
        product = request.env['product.product'].browse(int(product_id))
        ai_engine = request.env['ai.engine'].get_default_engine()
        
        product_data = {
            'name': product.display_name,
            'cost': product.standard_price,
            'category': product.categ_id.name if product.categ_id else 'IT Equipment'
        }
        
        result = ai_engine.recommend_price(product_data, channel_code)
        return result