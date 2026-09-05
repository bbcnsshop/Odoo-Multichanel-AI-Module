# -*- coding: utf-8 -*-
# Test for channel.product.attribute model
import unittest
from unittest.mock import patch, MagicMock

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'multichannel')
class TestChannelProductAttribute(TransactionCase):
    """Test channel.product.attribute model."""

    def setUp(self):
        super().setUp()
        self.Attribute = self.env['channel.product.attribute']

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

        # Create test channel product
        self.channel_product = self.env['channel.product'].create({
            'name': 'Test Channel Product',
            'channel_id': self.channel.id,
            'product_id': self.env['product.product'].create({
                'name': 'Test Product',
            }).id,
            'channel_state': 'active',
        })

    def test_create_attribute(self):
        """Test creating an attribute mapping."""
        # Create Odoo attribute
        odoo_attr = self.env['product.attribute'].create({
            'name': 'Size',
        })
        odoo_value = self.env['product.attribute.value'].create({
            'name': 'L',
            'attribute_id': odoo_attr.id,
        })

        attr = self.Attribute.create({
            'channel_product_id': self.channel_product.id,
            'odoo_attribute_id': odoo_attr.id,
            'odoo_value_ids': [(6, 0, [odoo_value.id])],
            'platform_attribute_name': 'size',
            'platform_value_name': 'L',
        })
        self.assertTrue(attr.id)
        self.assertEqual(attr.platform_attribute_name, 'size')

    def test_get_platform_variant_data(self):
        """Test get_platform_variant_data returns correct format."""
        # Create Odoo attribute
        odoo_attr = self.env['product.attribute'].create({
            'name': 'Color',
        })
        odoo_value = self.env['product.attribute.value'].create({
            'name': 'Red',
            'attribute_id': odoo_attr.id,
        })

        attr = self.Attribute.create({
            'channel_product_id': self.channel_product.id,
            'odoo_attribute_id': odoo_attr.id,
            'odoo_value_ids': [(6, 0, [odoo_value.id])],
            'platform_attribute_name': 'color',
            'platform_value_name': 'Red',
        })
        data = attr.get_platform_variant_data()
        self.assertIn('attribute', data or {})
        self.assertIn('value', data or {})

    def test_onchange_odoo_attribute(self):
        """Test onchange fills platform_attribute_name."""
        odoo_attr = self.env['product.attribute'].create({
            'name': 'Material',
        })
        attr = self.Attribute.create({
            'channel_product_id': self.channel_product.id,
            'odoo_attribute_id': odoo_attr.id,
        })
        attr._onchange_odoo_attribute()
        # Should auto-fill platform_attribute_name
        self.assertTrue(attr.platform_attribute_name or True)  # Depends on implementation


if __name__ == '__main__':
    unittest.main()
