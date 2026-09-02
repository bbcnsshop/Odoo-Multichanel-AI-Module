# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ChannelProductAttribute(models.Model):
    """Map Odoo product attribute values to channel-specific attribute names.

    Example: Odoo "Color/Red" -> Shopee "Color/แดง"
    """
    _name = 'channel.product.attribute'
    _description = 'Channel Product Attribute Mapping'
    _order = 'channel_id, sequence, id'
    _sql_constraints = [
        ('channel_attr_value_unique',
         'unique(channel_id, odoo_attribute_id, odoo_value_id, platform_attr_name)',
         'This attribute mapping already exists!')
    ]

    active = fields.Boolean(string='Active', default=True)
    channel_id = fields.Many2one(
        'channel.config', string='Channel', required=True, index=True, ondelete='cascade'
    )
    sequence = fields.Integer(string='Sequence', default=10)
    channel_product_id = fields.Many2one(
        'channel.product', string='Channel Product', ondelete='cascade', index=True
    )
    odoo_attribute_id = fields.Many2one(
        'product.attribute', string='Odoo Attribute', required=True,
        help='Source attribute (e.g. Color, Size)'
    )
    odoo_value_id = fields.Many2one(
        'product.attribute.value', string='Odoo Value', required=True,
        domain="[('attribute_id', '=', odoo_attribute_id)]"
    )
    platform_attr_name = fields.Char(
        string='Platform Attribute Name', required=True,
        help='Attribute name as it should appear on the platform (e.g. Color, สี)'
    )
    platform_attr_value = fields.Char(
        string='Platform Attribute Value', required=True,
        help='Value as it should appear on the platform (e.g. Red, แดง)'
    )
    is_mandatory = fields.Boolean(string='Mandatory', default=True)
    is_custom = fields.Boolean(
        string='Custom Attribute',
        help='True if this is a custom attribute (not part of variant)'
    )

    @api.onchange('odoo_attribute_id')
    def _onchange_attribute(self):
        if self.odoo_attribute_id:
            self.platform_attr_name = self.odoo_attribute_id.name

    @api.onchange('odoo_value_id')
    def _onchange_value(self):
        if self.odoo_value_id:
            self.platform_attr_value = self.odoo_value_id.name

    def get_platform_variant_data(self):
        """Return dict suitable for Shopee/Lazada/TikTok variant API."""
        return {
            'attr_name': self.platform_attr_name,
            'attr_value': self.platform_attr_value,
            'is_mandatory': self.is_mandatory,
        }


class ChannelProductVariant(models.Model):
    """Track variants (product.product records) per channel product."""
    _name = 'channel.product.variant'
    _description = 'Channel Product Variant'
    _rec_name = 'product_variant_id'
    _sql_constraints = [
        ('cp_variant_unique',
         'unique(channel_product_id, product_variant_id)',
         'Variant already mapped to this channel product!')
    ]

    channel_product_id = fields.Many2one(
        'channel.product', string='Channel Product',
        required=True, ondelete='cascade', index=True
    )
    channel_id = fields.Many2one(
        'channel.config', string='Channel',
        related='channel_product_id.channel_id', store=True
    )
    product_variant_id = fields.Many2one(
        'product.product', string='Odoo Variant', required=True,
        domain="[('product_tmpl_id', '=', parent.product_id.product_tmpl_id)]"
    )
    product_tmpl_id = fields.Many2one(
        'product.template', string='Template',
        related='product_variant_id.product_tmpl_id', store=True
    )
    variant_sku = fields.Char(
        string='Variant SKU', related='product_variant_id.default_code', store=True
    )
    platform_variant_id = fields.Char(
        string='Platform Variant ID',
        help='ID returned by platform after variant creation'
    )
    platform_variant_url = fields.Char(string='Platform Variant URL')
    channel_price = fields.Float(string='Variant Price')
    channel_qty = fields.Integer(string='Variant Stock', default=0)
    channel_weight = fields.Float(string='Variant Weight (kg)')
    attribute_mapping_ids = fields.One2many(
        'channel.product.attribute', 'channel_product_id',
        string='Attribute Mappings',
        domain=lambda self: [('channel_id', '=', self.channel_id.id)]
    )
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error'),
    ], string='Sync Status', default='pending')

    def _variant_attr_display(self):
        """Return variant attribute display like: Color: Red, Size: L."""
        self.ensure_one()
        attrs = []
        for line in self.product_variant_id.product_template_attribute_value_ids:
            attr = line.attribute_id
            value = line.product_attribute_value_id
            platform_attr = self.attribute_mapping_ids.filtered(
                lambda a: a.odoo_attribute_id == attr and a.odoo_value_id == value
            )
            if platform_attr:
                attrs.append('%s: %s' % (platform_attr.platform_attr_name, platform_attr.platform_attr_value))
            else:
                attrs.append('%s: %s' % (attr.name, value.name))
        return ', '.join(attrs)

    def name_get(self):
        result = []
        for rec in self:
            name = rec.product_variant_id.display_name
            attrs = rec._variant_attr_display()
            if attrs:
                name = '%s (%s)' % (name, attrs)
            result.append((rec.id, name))
        return result

    def action_sync_variant(self):
        for rec in self:
            try:
                _logger.info('Syncing variant %s to %s', rec.product_variant_id.display_name, rec.channel_id.code)
                rec.write({'sync_status': 'synced'})
            except Exception as e:
                rec.write({'sync_status': 'error'})
                _logger.error('Variant sync failed: %s', e)
        return True


class ChannelProductAttributeWizard(models.TransientModel):
    """Bulk auto-generate attribute mappings based on Odoo attribute values."""
    _name = 'channel.product.attribute.wizard'
    _description = 'Auto-generate Attribute Mappings'

    channel_product_id = fields.Many2one(
        'channel.product', string='Channel Product', required=True
    )
    use_default_name = fields.Boolean(
        string='Use Odoo Names', default=True,
        help='If checked, platform_attr_name = odoo_attribute.name'
    )
    override_platform_name = fields.Char(
        string='Override Attribute Name',
        help='If set, all platform_attr_name will use this value'
    )

    def action_generate(self):
        self.ensure_one()
        cp = self.channel_product_id
        product = cp.product_id
        AttributeMapping = self.env['channel.product.attribute']

        existing = AttributeMapping.search([('channel_product_id', '=', cp.id)])
        existing.unlink()

        created = 0
        seen = set()
        for line in product.product_template_attribute_value_ids:
            attr = line.attribute_id
            value = line.product_attribute_value_id
            key = (attr.id, value.id)
            if key in seen:
                continue
            seen.add(key)

            vals = {
                'channel_id': cp.channel_id.id,
                'channel_product_id': cp.id,
                'odoo_attribute_id': attr.id,
                'odoo_value_id': value.id,
                'platform_attr_name': self.override_platform_name if self.override_platform_name else attr.name,
                'platform_attr_value': value.name,
                'is_mandatory': True,
            }
            AttributeMapping.create(vals)
            created += 1
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Attribute Mappings Created'),
                'message': _('Created %d attribute mappings') % created,
                'type': 'success',
            }
        }
