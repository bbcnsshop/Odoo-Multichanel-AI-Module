# Odoo Multi-Channel AI Module

> Multi-Channel E-Commerce Integration for Odoo 16 with AI Engine (OpenRouter)

รองรับ Shopee, Lazada, TikTok Shop - รวม Sync, OAuth, AI Auto-Fill

**🧪 Tested:** ~370 tests across 30+ test files — 5 ก.ย. 2569

**📊 Coverage:** 16/20 models at 100% + Wizards + Mixins + Connectors (Shopee/Lazada/TikTok) + Cron + OAuth + i18n

**✅ Phases 14-30 Complete:** More Tests, Order Implementation, Connector Implementation, View Buttons, Connector Tests, Cron Tests, OAuth Tests, Wizard Tests, Mixin Tests, Code Quality Check, Model Enhancement, i18n Check

---

## 📋 Features

### 🛒 Multi-Channel Support
- Shopee, Lazada, TikTok Shop
- Sandbox (MOCK) / Production mode (`api_url='sandbox'` / `api_url='production'`)
- OAuth token management with auto-refresh
- 39 connector methods (13 per platform × 3 platforms)

### 🛒 Order Management (Enhanced)
- Channel Order Line with margin tracking
- Sale Order Channel integration
- Order sync from platforms
- Create Delivery/Invoice from Channel Order
- Cancel/Refund on platform

### 🧙 Wizards (5 wizards)
- **Add to Channel Wizard** - Add products to channel with preview
- **Channel List Add Wizard** - Add new platform channel
- **Channel Product AI Fill Wizard** - Bulk AI auto-fill
- **Channel Product Attribute Wizard** - Generate attribute mappings
- **Profit Calculator Wizard** - Calculate profit with fees

### 🔧 Mixins (4 mixins)
- **ConnectionMixin** - Connector factory + test connection
- **CountsMixin** - Computed counts + navigation actions
- **SyncActionsMixin** - Bulk sync actions
- **TokenActionsMixin** - Token refresh + cron job

### 🤖 AI Engine (OpenRouter)
- Auto-fill product fields (barcode, condition, brand)
- Price recommendation
- Product classification

### 📸 Image & Video Management
- Channel Product Image with multi-source (product/variant/URL)
- Channel Product Video with S3 integration
- Platform-specific image IDs (Shopee/Lazada/TikTok)
- Auto alt text generation

### 📊 Order Management
- Webhook integration
- Create Sale Order from Channel Order
- Order status tracking

### 🧪 Quality Assurance
- **Remote Dry-Run Validation** - validate XML + Python บน production server ก่อน deploy
- ตรวจ 72 ไฟล์ (32 XML + 40 Python) ใช้เวลา < 1 วินาที
- Bug detection: mismatched tag, orphan entry, indentation, duplicated code

---

## 📁 Structure

```
multichannel_ai/
├── models/
│   ├── channel_config.py           # Channel settings
│   ├── channel_product.py         # Channel product management
│   ├── channel_product_image.py   # Product images
│   ├── channel_product_video.py   # Product videos
│   ├── channel_product_attribute.py # Attribute mappings
│   ├── channel_product_field_mapping.py # Field mappings + completeness
│   ├── channel_order.py           # Order management
│   ├── sale_order_channel.py      # Sale order integration
│   ├── price_recommendation.py    # AI pricing
│   ├── category_mapping.py         # Category mapping
│   ├── channel_list_module.py     # Platform list
│   ├── mixins/                    # Method mixins
│   │   ├── sync_actions.py        # Sync products/orders
│   │   ├── connection.py          # Connector factory
│   │   ├── token_actions.py       # Token refresh
│   │   └── counts.py              # Computed counts
│   └── connectors/                # API connectors
│       ├── base.py                # Abstract base
│       ├── shopee.py              # Shopee API
│       ├── lazada.py              # Lazada API
│       ├── tiktok.py              # TikTok API
│       └── mock_data.py           # Mock data
├── controllers/
│   ├── main_controller.py         # Dashboard & API
│   ├── oauth_controller.py        # OAuth flow
│   ├── webhook_controller.py      # Webhooks
│   └── video_controller.py        # Video serving
├── wizards/
├── views/
└── i18n/                          # Translations (POT/TH)

ai_engine/
├── models/
│   ├── ai_engine.py               # AI Engine (OpenRouter)
│   └── ai_category_mapping.py     # Category mappings
└── tests/                         # AI tests
```

---

## 🚀 Quick Start
# Odoo Multi-Channel AI Module

> Multi-Channel E-Commerce Integration for Odoo 17 with AI Engine (OpenRouter)

รองรับ Shopee, Lazada, TikTok Shop - รวม Sync, OAuth, AI Auto-Fill

**🧪 Tested:** 235/235 unit tests across 24 test files — 5 ก.ย. 2569

**📊 Coverage:** All models + Wizards + Mixins + Connectors (Shopee/Lazada/TikTok) + Cron + OAuth

**✅ Phases 14-25 Complete:** More Tests, Order Implementation, Connector Implementation, View Buttons, Connector Tests, Cron Tests, OAuth Tests, Wizard Tests, Mixin Tests, Code Quality Check

---

## 📋 Features

### 🛒 Multi-Channel Support
- Shopee, Lazada, TikTok Shop
- Sandbox (MOCK) / Production mode (`api_url='sandbox'` / `api_url='production'`)
- OAuth token management with auto-refresh
- 39 connector methods (13 per platform × 3 platforms)

### 🧙 Wizards (5 wizards)
- **Add to Channel Wizard** - Add products to channel with preview
- **Channel List Add Wizard** - Add new platform channel
- **Channel Product AI Fill Wizard** - Bulk AI auto-fill
- **Channel Product Attribute Wizard** - Generate attribute mappings
- **Profit Calculator Wizard** - Calculate profit with fees

### 🔧 Mixins (4 mixins)
- **ConnectionMixin** - Connector factory + test connection
- **CountsMixin** - Computed counts + navigation actions
- **SyncActionsMixin** - Bulk sync actions
- **TokenActionsMixin** - Token refresh + cron job

### 🤖 AI Engine (OpenRouter)
- Auto-fill product fields (barcode, condition, brand)
- Price recommendation
- Product classification

### 🔄 Sync Features
- Sync products to channel
- Sync orders from channel
- Automatic token refresh
- Field mapping (Odoo → Platform)

### 📊 Order Management
- Webhook integration
- Create Sale Order from Channel Order
- Order status tracking

### 🧪 Quality Assurance
- **Remote Dry-Run Validation** - validate XML + Python บน production server ก่อน deploy
- ตรวจ 72 ไฟล์ (32 XML + 40 Python) ใช้เวลา < 1 วินาที
- Bug detection: mismatched tag, orphan entry, indentation, duplicated code

---

## 📁 Structure

```
multichannel_ai/
├── models/
│   ├── channel_config.py           # Channel settings
│   ├── mixins/                    # Method mixins
│   │   ├── sync_actions.py        # Sync products/orders
│   │   ├── connection.py          # Connector factory
│   │   ├── token_actions.py       # Token refresh
│   │   └── counts.py              # Computed counts
│   ├── channel_product.py
│   ├── channel_order.py
│   └── connectors/                # API connectors
├── controllers/
├── wizards/
└── views/
```

---

## 🚀 Quick Start
