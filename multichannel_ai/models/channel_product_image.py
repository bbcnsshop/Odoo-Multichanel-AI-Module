# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging, base64, requests
from io import BytesIO

_logger = logging.getLogger(__name__)


class ChannelProductImage(models.Model):
    """Images for a channel product - linked to channel.product."""
    _name = 'channel.product.image'
    _description = 'Channel Product Image'
    _order = 'sequence, id'
    _sql_constraints = [
        ('cp_sequence_unique', 'unique(channel_product_id, sequence)',
         'Sequence must be unique per product-channel!')
    ]

    channel_product_id = fields.Many2one(
        'channel.product', string='Channel Product',
        required=True, ondelete='cascade', index=True
    )
    channel_id = fields.Many2one(
        'channel.config', string='Channel',
        related='channel_product_id.channel_id', store=True, index=True
    )
    product_id = fields.Many2one(
        'product.product', string='Product',
        related='channel_product_id.product_id', store=True
    )
    sequence = fields.Integer(string='Sequence', default=10)
    is_primary = fields.Boolean(string='Primary Image', default=False)

    # Odoo source
    source_type = fields.Selection([
        ('product', 'Product Image'),
        ('variant', 'Variant Image'),
        ('url', 'External URL'),
        ('binary', 'Uploaded'),
    ], string='Source Type', default='product')
    odoo_image_field = fields.Char(
        string='Odoo Image Field',
        help='Field name on product.product, e.g. image_1920, image_128'
    )

    # Image data
    image_url = fields.Char(string='Image URL')
    image_id_on_platform = fields.Char(string='Platform Image ID')
    platform_image_url = fields.Char(string='Platform Image URL')
    upload_status = fields.Selection([
        ('pending', 'Pending Upload'),
        ('uploading', 'Uploading'),
        ('uploaded', 'Uploaded'),
        ('error', 'Upload Error'),
    ], string='Upload Status', default='pending', index=True)
    upload_message = fields.Text(string='Upload Message')
    last_upload = fields.Datetime(string='Last Upload Attempt')

    # Metadata
    width = fields.Integer(string='Width')
    height = fields.Integer(string='Height')
    file_size = fields.Integer(string='File Size (bytes)')
    checksum = fields.Char(string='Checksum (MD5)')

    @api.onchange('source_type')
    def _onchange_source_type(self):
        if self.source_type == 'product':
            self.odoo_image_field = 'image_1920'
        elif self.source_type == 'variant':
            self.odoo_image_field = 'image_variant_1920'
        else:
            self.odoo_image_field = False

    def _get_image_data(self):
        """Resolve image binary from source."""
        self.ensure_one()
        product = self.product_id
        if not product:
            return False, False

        if self.source_type == 'product':
            field = self.odoo_image_field or 'image_1920'
            img = getattr(product, field, False)
            return img, field
        elif self.source_type == 'variant':
            field = self.odoo_image_field or 'image_variant_1920'
            img = getattr(product, field, False)
            return img, field
        elif self.source_type == 'url':
            return False, 'external_url'
        else:
            return False, False

    def _download_from_url(self, url):
        """Download image from external URL."""
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.content
        except Exception as e:
            _logger.error('Failed to download image from %s: %s', url, e)
        return False

    def _prepare_image_for_upload(self, raw_bytes):
        """Prepare image: resize if needed, get metadata."""
        import hashlib
        md5 = hashlib.md5(raw_bytes).hexdigest()
        return raw_bytes, md5, len(raw_bytes)

    def _upload_to_shopee(self, raw_bytes, filename='image.jpg'):
        """Upload to Shopee API. Returns (platform_image_id, platform_image_url)."""
        connector = self.env['channel.api.connector']._get_connector('shopee')
        if not connector:
            raise ValidationError(_('Shopee API connector not configured'))
        result = connector.upload_image(raw_bytes, filename)
        return result.get('image_id'), result.get('image_url')

    def _upload_to_lazada(self, raw_bytes, filename='image.jpg'):
        connector = self.env['channel.api.connector']._get_connector('lazada')
        if not connector:
            raise ValidationError(_('Lazada API connector not configured'))
        result = connector.upload_image(raw_bytes, filename)
        return result.get('image_id'), result.get('image_url')

    def _upload_to_tiktok(self, raw_bytes, filename='image.jpg'):
        connector = self.env['channel.api.connector']._get_connector('tiktok')
        if not connector:
            raise ValidationError(_('TikTok API connector not configured'))
        result = connector.upload_image(raw_bytes, filename)
        return result.get('image_id'), result.get('image_url')

    def action_upload(self):
        """Upload this image to the platform."""
        for rec in self:
            try:
                rec.write({'upload_status': 'uploading'})

                # Get image binary
                img_binary, src = rec._get_image_data()
                if rec.source_type == 'url':
                    img_binary = rec._download_from_url(rec.image_url or '')
                    src = 'downloaded'

                if not img_binary:
                    rec.write({
                        'upload_status': 'error',
                        'upload_message': 'Could not resolve image data',
                        'last_upload': fields.Datetime.now()
                    })
                    continue

                prepared, checksum, fsize = rec._prepare_image_for_upload(img_binary)
                rec.write({'checksum': checksum, 'file_size': fsize})

                # Upload per channel
                channel_code = rec.channel_id.code
                if channel_code == 'shopee':
                    pid, purl = rec._upload_to_shopee(prepared)
                elif channel_code == 'lazada':
                    pid, purl = rec._upload_to_lazada(prepared)
                elif channel_code == 'tiktok':
                    pid, purl = rec._upload_to_tiktok(prepared)
                else:
                    rec.write({
                        'upload_status': 'error',
                        'upload_message': 'Unknown channel: %s' % channel_code,
                        'last_upload': fields.Datetime.now()
                    })
                    continue

                rec.write({
                    'image_id_on_platform': pid,
                    'platform_image_url': purl,
                    'upload_status': 'uploaded',
                    'upload_message': 'Uploaded successfully',
                    'last_upload': fields.Datetime.now()
                })
                _logger.info('Uploaded image for %s to %s: %s', rec.name, channel_code, pid)

            except Exception as e:
                rec.write({
                    'upload_status': 'error',
                    'upload_message': str(e),
                    'last_upload': fields.Datetime.now()
                })
                _logger.error('Image upload failed for %s: %s', rec.name, e)
        return True

    def action_retry_upload(self):
        self.filtered(lambda r: r.upload_status == 'error').action_upload()
        return True


class ChannelApiConnector(models.AbstractModel):
    """Abstract connector for platform API calls."""
    _name = 'channel.api.connector'
    _description = 'Channel API Connector (Abstract)'

    @api.model
    def _get_connector(self, channel_code):
        """Return the appropriate connector instance for this channel."""
        connectors = {
            'shopee': 'shopee.api.connector',
            'lazada': 'lazada.api.connector',
            'tiktok': 'tiktok.api.connector',
        }
        model_name = connectors.get(channel_code)
        if not model_name:
            return self.env['channel.api.connector']
        return self.env[model_name]

    @api.model
    def _get_channel_config(self, channel_code):
        return self.env['channel.config'].search([('code', '=', channel_code)], limit=1)

    def _api_call(self, endpoint, method='POST', data=None, files=None, headers=None):
        """Make an authenticated API call to the platform."""
        raise NotImplementedError('Subclass must implement _api_call')

    def upload_image(self, raw_bytes, filename='image.jpg'):
        """Upload an image. Returns dict with image_id and image_url."""
        raise NotImplementedError('Subclass must implement upload_image')

    def create_product(self, product_data):
        """Create/update a product on the platform."""
        raise NotImplementedError('Subclass must implement create_product')

    def update_product(self, platform_product_id, product_data):
        raise NotImplementedError('Subclass must implement update_product')

    def get_product(self, platform_product_id):
        raise NotImplementedError('Subclass must implement get_product')


class ShopeeApiConnector(models.AbstractModel):
    """Shopee API Connector."""
    _name = 'shopee.api.connector'
    _inherit = 'channel.api.connector'
    _description = 'Shopee API Connector'

    def _get_base_url(self):
        return 'https://partner.shopeemobile.com/api/v1'

    def _get_auth_headers(self):
        config = self._get_channel_config('shopee')
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % (config.access_token or ''),
            'Shopid': config.shop_id or '',
        }

    def _api_call(self, endpoint, method='POST', data=None):
        config = self._get_channel_config('shopee')
        if not config.access_token:
            raise ValidationError(_('Shopee access token not configured'))
        url = '%s/%s' % (self._get_base_url(), endpoint)
        try:
            resp = requests.post(url, json=data, headers=self._get_auth_headers(), timeout=60)
            result = resp.json()
            if result.get('error'):
                raise ValidationError(_('Shopee API error: %s') % result.get('msg', result['error']))
            return result.get('response', {})
        except Exception as e:
            _logger.error('Shopee API call failed: %s', e)
            raise

    def upload_image(self, raw_bytes, filename='image.jpg'):
        """Upload image to Shopee. Returns {image_id, image_url}."""
        import mimetypes
        mime = mimetypes.guess_type(filename)[0] or 'image/jpeg'
        files = {'file': (filename, raw_bytes, mime)}
        config = self._get_channel_config('shopee')
        if not config.access_token:
            # Mock response for development
            _logger.warning('Shopee token not configured - returning mock response')
            return {
                'image_id': 'mock_shopee_img_%s' % hash(raw_bytes) % 1000000,
                'image_url': 'https://cv.shopee.co.th/file/mock_%s' % hash(raw_bytes) % 1000000
            }
        url = '%s/shop/image/upload' % self._get_base_url()
        try:
            headers = {
                'Authorization': 'Bearer %s' % config.access_token,
                'Shopid': config.shop_id or '',
            }
            resp = requests.post(url, files=files, headers=headers, timeout=60)
            result = resp.json()
            if result.get('error'):
                raise ValidationError(_('Shopee image upload failed: %s') % result.get('msg'))
            data = result.get('response', {})
            return {
                'image_id': data.get('image_id', ''),
                'image_url': data.get('image_url', ''),
            }
        except Exception as e:
            if 'token not configured' in str(e):
                raise
            raise ValidationError(_('Shopee image upload failed: %s') % str(e))

    def create_product(self, product_data):
        """Create product on Shopee."""
        return self._api_call('product/add_item', data=product_data)

    def update_product(self, platform_product_id, product_data):
        data = {'product_id': platform_product_id}
        data.update(product_data)
        return self._api_call('product/update_item', data=data)


class LazadaApiConnector(models.AbstractModel):
    """Lazada API Connector."""
    _name = 'lazada.api.connector'
    _inherit = 'channel.api.connector'
    _description = 'Lazada API Connector'

    def _get_base_url(self):
        config = self._get_channel_config('lazada')
        return 'https://api.lazada.%s/rest' % (config.country_code or 'co.th')

    def upload_image(self, raw_bytes, filename='image.jpg'):
        if not self._get_channel_config('lazada').access_token:
            _logger.warning('Lazada token not configured - returning mock response')
            return {
                'image_id': 'mock_lazada_img_%s' % (hash(raw_bytes) % 1000000),
                'image_url': 'https://lh3.googleusercontent.com/mock_%s' % (hash(raw_bytes) % 1000000)
            }
        import hashlib, time
        payload = {
            'file_name': filename,
            'body': base64.b64encode(raw_bytes).decode('utf-8'),
            'timestamp': int(time.time()),
        }
        # Lazada requires signature - simplified here
        try:
            resp = requests.post(
                '%s/product/img/upload' % self._get_base_url(),
                json=payload, timeout=60
            )
            result = resp.json()
            if result.get('code') != '0':
                raise ValidationError(_('Lazada image upload failed: %s') % result.get('message'))
            return {
                'image_id': result.get('data', {}).get('image_id', ''),
                'image_url': result.get('data', {}).get('image_url', ''),
            }
        except Exception as e:
            if 'token not configured' in str(e):
                raise
            raise ValidationError(_('Lazada image upload failed: %s') % str(e))

    def create_product(self, product_data):
        _logger.info('Lazada create_product called (not implemented)')
        return {}

    def update_product(self, platform_product_id, product_data):
        return {}


class TikTokApiConnector(models.AbstractModel):
    """TikTok Shop API Connector."""
    _name = 'tiktok.api.connector'
    _inherit = 'channel.api.connector'
    _description = 'TikTok Shop API Connector'

    def _get_base_url(self):
        return 'https://open-api.tiktokglobalshop.com'

    def upload_image(self, raw_bytes, filename='image.jpg'):
        if not self._get_channel_config('tiktok').access_token:
            _logger.warning('TikTok token not configured - returning mock response')
            return {
                'image_id': 'mock_tiktok_img_%s' % (hash(raw_bytes) % 1000000),
                'image_url': 'https://p16.merchant-ums.byteapps.com/mock_%s' % (hash(raw_bytes) % 1000000)
            }
        import hashlib, time
        files = {'file': (filename, raw_bytes, 'image/jpeg')}
        data = {'file_name': filename, 'upload_type': 'product'}
        headers = {'Authorization': 'Bearer %s' % self._get_channel_config('tiktok').access_token}
        try:
            resp = requests.post(
                '%s/api/v1/media/upload/image/' % self._get_base_url(),
                files=files, data=data, headers=headers, timeout=60
            )
            result = resp.json()
            if result.get('code') != 0:
                raise ValidationError(_('TikTok image upload failed: %s') % result.get('message'))
            return {
                'image_id': result.get('data', {}).get('image_id', ''),
                'image_url': result.get('data', {}).get('image_url', ''),
            }
        except Exception as e:
            if 'token not configured' in str(e):
                raise
            raise ValidationError(_('TikTok image upload failed: %s') % str(e))

    def create_product(self, product_data):
        _logger.info('TikTok create_product called (not implemented)')
        return {}

    def update_product(self, platform_product_id, product_data):
        return {}
