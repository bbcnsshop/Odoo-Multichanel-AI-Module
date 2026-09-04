# -*- coding: utf-8 -*-
"""
Lazada Connector
เรียก MOCK หรือ API จริงตาม api_url mode
"""
from .base import ChannelConnectorBase
from .mock_data import MOCK
import logging
import time

_logger = logging.getLogger(__name__)


class LazadaConnector(ChannelConnectorBase):
    PLATFORM_CODE = 'lazada'
    PLATFORM_NAME = 'Lazada'

    def _is_mock_mode(self):
        return (self.channel.api_url or 'sandbox') == 'sandbox'

    def refresh_access_token(self):
        if self._is_mock_mode():
            result = MOCK.refresh_token(self.PLATFORM_CODE)
        else:
            raise NotImplementedError('Real Lazada API not implemented yet')
        from datetime import timedelta
        from odoo.fields import Datetime
        self.channel.write({'access_token': result['access_token'], 'token_expire_date': Datetime.now() + timedelta(days=30)})
        return result

    def upload_image(self, image_data, filename='image.jpg', product_id=None):
        if self._is_mock_mode():
            return MOCK.upload_image(self.PLATFORM_CODE, image_data, filename, product_id)
        raise NotImplementedError('Real Lazada API not implemented yet')

    def create_item(self, product_data):
        if self._is_mock_mode():
            return MOCK.create_item(self.PLATFORM_CODE, product_data)
        raise NotImplementedError('Real Lazada API not implemented yet')

    def update_item(self, platform_item_id, product_data):
        if self._is_mock_mode():
            return MOCK.update_item(self.PLATFORM_CODE, platform_item_id, product_data)
        raise NotImplementedError('Real Lazada API not implemented yet')

    def delete_item(self, platform_item_id):
        if self._is_mock_mode():
            return MOCK.delete_item(self.PLATFORM_CODE, platform_item_id)
        raise NotImplementedError('Real Lazada API not implemented yet')

    def get_item(self, platform_item_id):
        if self._is_mock_mode():
            return MOCK.get_item(self.PLATFORM_CODE, platform_item_id)
        raise NotImplementedError('Real Lazada API not implemented yet')

    def get_products(self, page=1, limit=50, **kwargs):
        if self._is_mock_mode():
            return MOCK.get_products(self.PLATFORM_CODE, page, limit, **kwargs)
        raise NotImplementedError('Real Lazada API not implemented yet')

    def update_stock(self, platform_item_id, stock):
        if self._is_mock_mode():
            return MOCK.update_stock(self.PLATFORM_CODE, platform_item_id, stock)
        raise NotImplementedError('Real Lazada API not implemented yet')

    def update_price(self, platform_item_id, price):
        if self._is_mock_mode():
            return MOCK.update_price(self.PLATFORM_CODE, platform_item_id, price)
        raise NotImplementedError('Real Lazada API not implemented yet')

    def get_orders(self, since=None, status=None, page=1, limit=50):
        if self._is_mock_mode():
            return MOCK.get_orders(self.PLATFORM_CODE, since, status, page, limit)
        raise NotImplementedError('Real Lazada API not implemented yet')

    def get_order_detail(self, platform_order_id):
        if self._is_mock_mode():
            return MOCK.get_order_detail(self.PLATFORM_CODE, platform_order_id)
        raise NotImplementedError('Real Lazada API not implemented yet')

    def get_logistics(self):
        if self._is_mock_mode():
            return MOCK.get_logistics(self.PLATFORM_CODE)
        raise NotImplementedError('Real Lazada API not implemented yet')

    def create_shipment(self, platform_order_id, logistics_id, tracking_number=None):
        if self._is_mock_mode():
            return MOCK.create_shipment(self.PLATFORM_CODE, platform_order_id, logistics_id, tracking_number)
        raise NotImplementedError('Real Lazada API not implemented yet')
