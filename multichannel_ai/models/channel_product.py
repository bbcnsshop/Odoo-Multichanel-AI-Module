# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ChannelProduct(models.Model):
    _name = 'channel.product'
    _description = 'Channel Product'
    _order = 'id desc'

    name = fields.Char(string='Display Name', compute='_compute_name', store=True)
    product_id = fields.Many2one('product.product', string='Product', required=True, index=True)
    channel_id = fields.Many2one('channel.config', string='Channel', required=True, index=True)
    product_category = fields.Char(related='product_id.categ_id.name', string='Category', store=True)
    product_cost = fields.Float(related='product_id.standard_price', string='Cost', store=True)
    odoo_qty = fields.Float(related='product_id.qty_available', string='Odoo Stock', store=True)

    channel_product_id = fields.Char(string='Channel Product ID')
    channel_price = fields.Float(string='Channel Price', required=True)
    channel_qty = fields.Integer(string='Channel Stock', default=0)
    channel_url = fields.Char(string='Channel URL')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='Status', default='draft', index=True)

    sync_status = fields.Selection([
        ('synced', 'Synced'),
        ('pending', 'Pending'),
        ('error', 'Error'),
        ('never', 'Never Synced'),
    ], string='Sync', default='never', index=True)
    sync_message = fields.Text(string='Sync Message')
    last_sync = fields.Datetime(string='Last Sync')

    ai_recommended_price = fields.Float(string='AI Recommended Price')
    ai_confidence = fields.Float(string='AI Confidence')

    # Per-channel overrides
    channel_weight = fields.Float(string='Weight (kg)', digits=(8, 3), help='Weight override')
    channel_length = fields.Float(string='Length (cm)', digits=(8, 2))
    channel_width = fields.Float(string='Width (cm)', digits=(8, 2))
    channel_height = fields.Float(string='Height (cm)', digits=(8, 2))
    channel_brand = fields.Char(string='Brand', help='Platform-specific brand (Lazada requires this)')
    
    # ============================================================
    # Platform-Specific Fields (Priority 1 - Critical)
    # ============================================================
    barcode = fields.Char(
        string='Barcode',
        help='สำหรับ Lazada (required) - รหัสสินค้า/Barcode ของ Platform'
    )
    condition = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ], string='Condition', default='new',
        help='สภาพสินค้า - Shopee และ Lazada ต้องการ field นี้'
    )
    channel_description = fields.Text(string='Description', help='Channel-specific description override')
    channel_video_url = fields.Char(string='Video URL', help='Video URL for TikTok or Shopee')
    channel_completeness_ids = fields.One2many(
        'channel.product.completeness', 'channel_product_id', string='Completeness'
    )
    image_ids = fields.One2many(
        'channel.product.image', 'channel_product_id', string='Images'
    )
    variant_ids = fields.One2many(
        'channel.product.variant', 'channel_product_id', string='Variants'
    )
    attribute_mapping_ids = fields.One2many(
        'channel.product.attribute', 'channel_product_id', string='Attribute Mappings'
    )
    completeness_pct = fields.Float(string='% Complete', digits=(5, 1),
                                    compute='_compute_completeness', store=True)
    has_missing_required = fields.Boolean(string='Missing Required',
                                          compute='_compute_completeness', store=True)

    @api.depends('product_id.name', 'channel_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = '%s (%s)' % (rec.product_id.name, rec.channel_id.name)

    @api.depends('channel_completeness_ids.completeness_pct',
                 'channel_completeness_ids.status',
                 'channel_completeness_ids.channel_id')
    def _compute_completeness(self):
        for rec in self:
            if not rec.channel_id:
                rec.completeness_pct = 100.0
                rec.has_missing_required = False
                continue
            cp = rec.channel_completeness_ids.filtered(lambda c: c.channel_id == rec.channel_id)
            if cp:
                rec.completeness_pct = cp[0].completeness_pct
                rec.has_missing_required = (cp[0].status == 'incomplete')
            else:
                rec.completeness_pct = 100.0
                rec.has_missing_required = False

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.channel_price = self.product_id.list_price or 0
            self.channel_qty = int(self.product_id.qty_available or 0)

    @api.onchange('channel_id')
    def _onchange_channel(self):
        if self.channel_id and self.product_id:
            try:
                ai = self.env['ai.engine'].get_default_engine()
                result = ai.recommend_price(
                    {'name': self.product_id.name, 'cost': self.product_id.standard_price or 0},
                    self.channel_id.code
                )
                self.ai_recommended_price = result.get('selling_price', 0)
            except Exception:
                pass

    def action_check_completeness(self):
        for rec in self:
            if rec.channel_id:
                self.env['channel.product.completeness'].upsert(rec.id, rec.channel_id.id)
            # Auto-create variant records if this is a variant product
            product = rec.product_id
            if product and product.product_template_attribute_value_ids:
                for variant in product.product_tmpl_id.product_variant_ids:
                    existing = self.env['channel.product.variant'].search([
                        ('channel_product_id', '=', rec.id),
                        ('product_variant_id', '=', variant.id)
                    ], limit=1)
                    if not existing:
                        self.env['channel.product.variant'].create({
                            'channel_product_id': rec.id,
                            'product_variant_id': variant.id,
                            'channel_price': rec.channel_price,
                            'channel_qty': int(variant.qty_available or 0),
                            'channel_weight': rec.channel_weight,
                        })
        return True

    def toggle_active(self):
        for rec in self:
            rec.state = 'active' if rec.state == 'draft' else 'draft'

    def _validate_for_sync(self):
        self.ensure_one()
        if not self.channel_id:
            raise ValidationError(_('No channel selected.'))
        missing = []
        for mapping in self.env['channel.product.field.mapping'].search([
            ('channel_id', '=', self.channel_id.id),
            ('active', '=', True),
            ('is_required', '=', True),
        ]):
            val = mapping.get_platform_value(self)
            if val is False or val == '' or val is None:
                missing.append(mapping.description or mapping.platform_field)
        if missing:
            lines = '\n'.join('- %s' % m for m in missing)
            raise ValidationError(
                _('Cannot sync to %s. Missing required fields:\n%s') %
                (self.channel_id.name, lines)
            )
        return True

    def sync_to_channel(self):
        for rec in self:
            try:
                rec.action_check_completeness()
                rec._validate_for_sync()
                if rec.channel_id.code == 'shopee':
                    rec._sync_shopee()
                elif rec.channel_id.code == 'lazada':
                    rec._sync_lazada()
                elif rec.channel_id.code == 'tiktok':
                    rec._sync_tiktok()
                rec.write({
                    'sync_status': 'synced',
                    'last_sync': fields.Datetime.now(),
                    'state': 'active',
                })
            except ValidationError:
                rec.write({
                    'sync_status': 'error',
                    'sync_message': 'Missing required fields',
                })
                raise
            except Exception as e:
                rec.write({
                    'sync_status': 'error',
                    'sync_message': str(e),
                })
                raise ValidationError(_('Sync failed: %s') % str(e))

    def _sync_shopee(self):
        _logger.info('Syncing %s to Shopee' % self.name)
        # Upload images first
        for img in self.image_ids.filtered(lambda i: i.upload_status != 'uploaded'):
            img.action_upload()

    def _sync_lazada(self):
        _logger.info('Syncing %s to Lazada' % self.name)
        for img in self.image_ids.filtered(lambda i: i.upload_status != 'uploaded'):
            img.action_upload()

    def _sync_tiktok(self):
        _logger.info('Syncing %s to TikTok' % self.name)
        for img in self.image_ids.filtered(lambda i: i.upload_status != 'uploaded'):
            img.action_upload()

    def unlink(self):
        for rec in self:
            if rec.sync_status == 'synced':
                _logger.warning('Deleting synced product %s from %s' % (rec.name, rec.channel_id.name))
        return super().unlink()

    # ============================================================
    # Cron Job Methods
    # ============================================================
    @api.model
    def cron_sync_pending_products(self):
        """Auto sync all products in pending state."""
        pending = self.search([
            ('sync_status', '=', 'pending'),
            ('state', 'in', ('active', 'draft')),
        ], limit=100)
        synced = 0
        errors = 0
        for cp in pending:
            try:
                cp.sync_to_channel()
                synced += 1
            except Exception as e:
                errors += 1
                _logger.error('Cron sync error for %s: %s' % (cp.name, str(e)))
        _logger.info('Auto sync: %d synced, %d errors' % (synced, errors))
        return True

    @api.model
    def cron_sync_channel_stock(self):
        """Sync stock from Odoo to channels for all active products."""
        active_cps = self.search([
            ('state', '=', 'active'),
        ])
        updated = 0
        for cp in active_cps:
            new_qty = int(cp.product_id.qty_available or 0)
            if new_qty != cp.channel_qty:
                cp.write({'channel_qty': new_qty})
                updated += 1
        _logger.info('Stock sync: %d products updated' % updated)
        return True

    @api.model
    def cron_refresh_ai_prices(self):
        """Refresh AI-recommended prices for all channel products."""
        cps = self.search([('state', 'in', ('active', 'draft'))], limit=200)
        refreshed = 0
        errors = 0
        for cp in cps:
            try:
                ai = self.env['ai.engine'].get_default_engine()
                result = ai.recommend_price(
                    {
                        'name': cp.product_id.name,
                        'cost': cp.product_id.standard_price or 0,
                    },
                    cp.channel_id.code,
                )
                if result.get('selling_price'):
                    cp.write({
                        'ai_recommended_price': result.get('selling_price', 0),
                    })
                    refreshed += 1
            except Exception as e:
                errors += 1
                _logger.error('AI price refresh error for %s: %s' % (cp.name, str(e)))
        _logger.info('AI price refresh: %d updated, %d errors' % (refreshed, errors))
        return True

    @api.model
    def cron_check_completeness(self):
        """Run completeness check on all channel products."""
        cps = self.search([])
        for cp in cps:
            try:
                cp._compute_completeness()
            except Exception as e:
                _logger.error('Completeness check error for %s: %s' % (cp.name, str(e)))
        return True

    @api.model
    def cron_sync_error_alert(self):
        """Log alerts for products with sync errors."""
        errored = self.search([('sync_status', '=', 'error')])
        if errored:
            _logger.warning(
                'Channel Products with sync errors (%d): %s' % (
                    len(errored),
                    ', '.join(errored.mapped('name')[:10]),
                )
            )
        return True

    @api.model
    def cron_fetch_channel_orders(self):
        """Fetch new orders from channels (placeholder)."""
        # In production, call Shopee/Lazada/TikTok APIs
        _logger.info('Cron: Fetch channel orders (placeholder)')
        return True


class ProductCategoryMapping(models.Model):
    _name = 'product.category.mapping'
    _description = 'Category Mapping'

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
    recommended_reasoning = fields.Text(string='Reasoning')
    cost_price = fields.Float(string='Cost Price')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('applied', 'Applied'),
    ], string='Status', default='pending')
    create_date = fields.Datetime(string='Created', default=fields.Datetime.now)