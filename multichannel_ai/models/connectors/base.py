# -*- coding: utf-8 -*-
"""
Base Connector Class for Multi-Channel Integration
Abstract interface สำหรับทุก platform
"""
from abc import ABC, abstractmethod
from odoo import _
from odoo.exceptions import ValidationError
import logging
import time
import hashlib
import hmac
import json

_logger = logging.getLogger(__name__)


class ChannelConnectorBase(ABC):
    """Abstract base class สำหรับทุก platform connector"""

    PLATFORM_CODE = 'base'
    PLATFORM_NAME = 'Base Platform'

    def __init__(self, channel_config):
        self.channel = channel_config
        self.api_key = channel_config.api_key
        self.api_secret = channel_config.api_secret
        self.access_token = channel_config.access_token
        self.refresh_token = channel_config.refresh_token

    def refresh_access_token(self):
        """Refresh OAuth token - Override in subclass"""
        _logger.warning(f'{self.PLATFORM_NAME}: refresh_access_token() not implemented')
        return {'access_token': f'{self.PLATFORM_CODE}_token_{time.time()}'}

    def ensure_valid_token(self):
        """ตรวจสอบ token valid ไหม ถ้าไม่ refresh"""
        if self.channel.is_token_expired and self.refresh_token:
            try:
                self.refresh_access_token()
            except Exception as e:
                raise ValidationError(_('Token expired: %s') % str(e))

    # ===========================
    # Image Upload
    # ===========================
    @abstractmethod
    def upload_image(self, image_data, filename='image.jpg', product_id=None):
        """อัปโหลดรูปไป platform"""
        pass

    # ===========================
    # Product Management
    # ===========================
    @abstractmethod
    def create_item(self, product_data):
        """สร้างสินค้าใหม่"""
        pass

    @abstractmethod
    def update_item(self, platform_item_id, product_data):
        """แก้ไขสินค้า"""
        pass

    @abstractmethod
    def delete_item(self, platform_item_id):
        """ลบสินค้า"""
        pass

    @abstractmethod
    def get_item(self, platform_item_id):
        """ดึงสินค้า 1 ตัว"""
        pass

    @abstractmethod
    def get_products(self, page=1, limit=50, **kwargs):
        """ดึงรายการสินค้า"""
        pass

    # ===========================
    # Stock & Price
    # ===========================
    @abstractmethod
    def update_stock(self, platform_item_id, stock):
        """อัปเดตสต็อก"""
        pass

    @abstractmethod
    def update_price(self, platform_item_id, price):
        """อัปเดตราคา"""
        pass

    # ===========================
    # Order Management
    # ===========================
    @abstractmethod
    def get_orders(self, since=None, status=None, page=1, limit=50):
        """ดึงรายการ orders"""
        pass

    @abstractmethod
    def get_order_detail(self, platform_order_id):
        """ดึงรายละเอียด order"""
        pass

    # ===========================
    # Logistics
    # ===========================
    @abstractmethod
    def get_logistics(self):
        """ดึงรายการ logistics options"""
        pass

    @abstractmethod
    def create_shipment(self, platform_order_id, logistics_id, tracking_number=None):
        """สร้าง shipment"""
        pass

    # ===========================
    # Helper Methods
    # ===========================
    def _mock_response(self, data=None, message='Success', success=True):
        return {'success': success, 'message': message, **(data or {})}

    def _generate_signature(self, data, secret=None):
        secret = secret or self.api_secret or ''
        if isinstance(data, dict):
            data = json.dumps(data, separators=(',', ':'))
        return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
