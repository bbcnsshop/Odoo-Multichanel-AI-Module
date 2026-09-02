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
    
    @http.route('/multichannel', type='http', auth='user')
    def index(self, **kwargs):
        """Redirect to dashboard"""
        return request.redirect('/multichannel/dashboard')

    @http.route('/multichannel/channels', type='http', auth='user')
    def channels_page(self, **kwargs):
        """Channels management page"""
        channels = request.env['channel.config'].search([])
        return request.render('multichannel_ai.channels_template', {
            'channels': channels,
        })

    @http.route('/multichannel/products', type='http', auth='user',
                methods=['GET', 'POST'])
    def products_page(self, channel=None, state=None, search=None, page=1, **kwargs):
        """Channel products list page with filters and pagination"""
        page = int(page) if page else 1
        per_page = 25

        domain = []
        if channel:
            domain.append(('channel_id', '=', int(channel)))
        if state:
            domain.append(('state', '=', state))
        if search:
            domain.append(('product_id.name', 'ilike', search))

        total = request.env['channel.product'].search_count(domain)
        total_pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page

        products = request.env['channel.product'].search(
            domain, limit=per_page, offset=offset, order='id desc'
        )
        channels = request.env['channel.config'].search([])

        return request.render('multichannel_ai.channel_products_template', {
            'products': products,
            'channels': channels,
            'channel_id': channel,
            'state': state,
            'search': search,
            'page': page,
            'total_pages': total_pages,
        })

    @http.route('/multichannel/sync', type='http', auth='user')
    def sync_page(self, **kwargs):
        """Manual sync page"""
        channels = request.env['channel.config'].search([])
        ch_stats = {}
        for ch in channels:
            ch_stats[ch.id] = {
                'total': request.env['channel.product'].search_count(
                    [('channel_id', '=', ch.id)]
                ),
                'synced': request.env['channel.product'].search_count([
                    ('channel_id', '=', ch.id),
                    ('sync_status', '=', 'synced'),
                ]),
                'pending': request.env['channel.product'].search_count([
                    ('channel_id', '=', ch.id),
                    ('sync_status', '=', 'pending'),
                ]),
                'error': request.env['channel.product'].search_count([
                    ('channel_id', '=', ch.id),
                    ('sync_status', '=', 'error'),
                ]),
            }
        return request.render('multichannel_ai.sync_template', {
            'channels': channels,
            'ch_stats': ch_stats,
        })

    @http.route('/multichannel/orders', type='http', auth='user')
    def orders_page(self, **kwargs):
        """Orders list page"""
        orders = request.env['channel.order'].search(
            [], limit=50, order='create_date desc'
        )
        return request.render('multichannel_ai.dashboard_template', {
            'summary_data': [],
            'orders': orders,
        })

    @http.route('/multichannel/api/sync_product', type='json', auth='user')
    def api_sync_product(self, product_id=None, **kwargs):
        """API: Sync single channel product"""
        if not product_id:
            return {'success': False, 'error': 'Missing product_id'}
        try:
            cp = request.env['channel.product'].browse(int(product_id))
            if not cp.exists():
                return {'success': False, 'error': 'Product not found'}
            cp.sync_to_channel()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/multichannel/api/sync_channel', type='json', auth='user')
    def api_sync_channel(self, channel_id=None, **kwargs):
        """API: Sync all products in a channel"""
        if not channel_id:
            return {'success': False, 'error': 'Missing channel_id'}
        try:
            products = request.env['channel.product'].search([
                ('channel_id', '=', int(channel_id)),
                ('state', 'in', ('active', 'draft')),
            ])
            synced = 0
            errors = 0
            for cp in products:
                try:
                    cp.sync_to_channel()
                    synced += 1
                except Exception:
                    errors += 1
            return {
                'success': True,
                'count': synced,
                'errors': errors,
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
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