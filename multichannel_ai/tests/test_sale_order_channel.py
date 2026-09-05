# -*- coding: utf-8 -*-
# Test for sale.order (with channel integration via _inherit)
import unittest
from unittest.mock import patch, MagicMock

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'multichannel')
class TestSaleOrderChannel(TransactionCase):
    """Test sale.order with channel extension."""

    def setUp(self):
        super().setUp()
        self.SaleOrder = self.env['sale.order']

        # Create test channel
        channel_module = self.env.ref(
            'multichannel_ai.channel_module_shopee',
            raise_if_not_found=False,
        ) or self.env['channel.list.module'].create({
            'name': 'Shopee',
            'code': 'shopee',
            'active': True,
        })
        self.channel = self.env['channel.config'].create({
            'name': 'Test Shopee',
            'code': 'shopee',
            'channel_module_id': channel_module.id,
            'active': True,
            'api_url': 'sandbox',
        })

    def test_create_sale_order(self):
        """Test creating a sale order."""
        order = self.SaleOrder.create({
            'partner_id': self.env.ref('base.partner_demo').id,
            'order_line': [(0, 0, {
                'name': 'Test Product',
                'product_id': self.env.ref('product.product_product_1').id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
            })],
        })
        self.assertTrue(order.id)
        self.assertEqual(order.state, 'draft')

    def test_channel_order_creation(self):
        """Test linking sale order to channel order."""
        # Create channel order
        channel_order = self.env['channel.order'].create({
            'platform_order_id': 'SHOPEE-001',
            'channel_id': self.channel.id,
            'buyer_username': 'test_buyer',
            'total_amount': 500.0,
            'state': 'pending',
        })

        # Create sale order linked to channel
        order = self.SaleOrder.create({
            'partner_id': self.env.ref('base.partner_demo').id,
            'channel_order_id': channel_order.id,  # If field exists
        })
        self.assertTrue(order.id)

    def test_sale_order_pricelist(self):
        """Test sale order with channel-specific pricelist."""
        # Create pricelist
        pricelist = self.env['product.pricelist'].create({
            'name': 'Shopee THB',
            'currency_id': self.env.ref('base.THB').id,
        })
        order = self.SaleOrder.create({
            'partner_id': self.env.ref('base.partner_demo').id,
            'pricelist_id': pricelist.id,
            'order_line': [(0, 0, {
                'name': 'Test',
                'product_id': self.env.ref('product.product_product_1').id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
            })],
        })
        self.assertEqual(order.pricelist_id.currency_id.name, 'THB')


if __name__ == '__main__':
    unittest.main()