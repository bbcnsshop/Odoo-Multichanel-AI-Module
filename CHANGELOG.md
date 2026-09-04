# Changelog

All notable changes to the Multi-Channel AI Module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### 🏗️ Architecture Restructure - Mixin Pattern

**Breaking Change:** Refactored `channel.config` model to use mixin pattern for better maintainability.

#### ✅ Added
- **Mixin Pattern** - Separated methods into dedicated mixin classes:
  - `channel.sync.actions` - Sync products/orders actions
  - `channel.token.actions` - Token refresh + cron
  - `channel.connection` - Connector factory + test connection
  - `channel.counts` - Computed counts + action views
- **New Directory Structure:**
  ```
  models/
  ├── channel_config.py      # Main model (fields only)
  └── mixins/
      ├── __init__.py
      ├── sync_actions.py    # action_sync_products, action_sync_orders
      ├── connection.py      # get_connector, action_test_connection
      ├── token_actions.py   # action_refresh_token, cron_refresh_expiring_tokens
      └── counts.py          # _compute_counts, action_view_*
  ```

#### ✅ Methods (All Tested)
| Mixin | Method | Status |
|-------|--------|--------|
| sync_actions | `action_sync_products()` | PASS |
| sync_actions | `action_sync_orders()` | PASS |
| connection | `get_connector()` | PASS |
| connection | `action_test_connection()` | PASS |
| connection | `_notification()` | PASS |
| token_actions | `action_refresh_token()` | PASS |
| token_actions | `_do_refresh_token()` | PASS |
| token_actions | `cron_refresh_expiring_tokens()` | PASS |
| counts | `_compute_counts()` | PASS |
| counts | `action_view_products()` | PASS |
| counts | `action_view_orders()` | PASS |

#### ✅ All Syntax Tests Passed
- `channel_config.py` - Syntax OK
- `mixins/sync_actions.py` - Syntax OK
- `mixins/connection.py` - Syntax OK
- `mixins/token_actions.py` - Syntax OK
- `mixins/counts.py` - Syntax OK
- `_inherit` - All 4 mixins registered

---

## [1.2.0] - 2026-09-04

### ✅ Added

#### OAuth + Token Management
- `action_connect_oauth()` - Redirect to platform OAuth
- `action_refresh_token()` - Refresh OAuth token
- `cron_refresh_expiring_tokens()` - Auto refresh expiring tokens

#### API Config Fields
- `partner_id`, `partner_key`, `shop_id` fields
- `api_url` - Sandbox/Production mode selector
- `base_url` - Auto-fill on platform change
- `access_token`, `refresh_token`, `token_expire_date`

#### Connector Base + MOCK
- `models/connectors/base.py` - Abstract base class (12 methods)
- `models/connectors/mock_data.py` - API MOCK + Test Data
- `models/connectors/shopee.py` - Shopee connector (MOCK)
- `models/connectors/lazada.py` - Lazada connector (MOCK)
- `models/connectors/tiktok.py` - TikTok connector (MOCK)

---

## [1.1.0] - 2026-09-02

### ✅ Added

#### Channel List Module
- `channel.list.module` model - Channel management
- `ChannelListAddWizard` - Add new channel wizard
- `action_activate()`, `action_deactivate()` - Toggle channel
- Demo data: Shopee, Lazada, TikTok

#### Platform Fields
- `channel.product.barcode` - For Lazada (required)
- `channel.product.condition` - Product condition (new/used/refurbished)

#### Field Mappings
- `channel.product.field.mapping` - Field mapping model
- **17 default mappings** for Shopee, Lazada, TikTok
- Transform types: Direct, Multiply, Divide, Lookup

#### Web Views
- `/multichannel/field_mappings` - Field Mappings page
- `/multichannel/api/field_mappings` - REST API (CRUD)

---

## [1.0.0] - 2026-09-01

### ✅ Added

#### Core Models (10 หลัก + 3 inherit)
- `channel.config` - Channel configuration
- `channel.product` - Products per channel
- `channel.product.variant` - Variants
- `channel.product.attribute` - Attributes
- `channel.product.image` - Images
- `channel.product.completeness` - Data completeness
- `channel.product.field.mapping` - Field mappings
- `channel.order` - Orders
- `channel.order.line` - Order lines
- `product.category.mapping` - Category mapping
- `price.recommendation` - AI price recommendation

#### AI Auto-Fill
- `ai_suggest_barcode()` - Barcode suggestions
- `ai_suggest_condition()` - Condition suggestions
- `ai_suggest_brand()` - Brand suggestions
- `ai_auto_fill_fields()` - Auto-fill all fields
- `cron_ai_auto_fill_missing()` - Daily auto-fill cron

#### Controllers
- `main_controller` - Dashboard, Products, Orders pages
- `oauth_controller` - OAuth flow
- `webhook_controller` - Order webhooks

#### Security
- `group_multichannel_user` - User permissions
- `group_multichannel_manager` - Manager permissions
- 29 access rules

---

## [0.1.0] - 2026-08-31

### 🚧 Initial Setup
- Project structure
- Basic module skeleton
- Odoo manifest
