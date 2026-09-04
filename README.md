# Odoo Multi-Channel AI Module

> Multi-Channel E-Commerce Integration for Odoo 17 with AI Engine (OpenRouter)

รองรับ Shopee, Lazada, TikTok Shop - รวม Sync, OAuth, AI Auto-Fill

**🧪 Tested:** 72/72 files (32 XML + 40 Python) — Dry-Run Validation 4 ก.ย. 2569

---

## 📋 Features

### 🛒 Multi-Channel Support
- Shopee, Lazada, TikTok Shop
- Sandbox (MOCK) / Production mode
- OAuth token management

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

### 1. Install Module
```bash
# Copy to Odoo addons path
cp -r multichannel_ai /path/to/odoo/addons/

# Update apps list in Odoo
# Install "Multi-Channel AI"
```

### 2. Configure Channel
1. Go to **Sales > Channels > Channels**
2. Click **Create**
3. Select **Platform** (Shopee/Lazada/TikTok)
4. Choose **API Mode** (Sandbox for testing)
5. Click **Test Connection** to verify

### 3. Sync Products
1. Select channel
2. Click **Sync Products**
3. Products will be imported as `channel.product`

### 4. Sync Orders
1. Click **Sync Orders**
2. Orders will appear in **Sales > Channels > Orders**
3. Click **Create Sale Order** to convert

---

## 🔧 Configuration

### API Credentials
| Field | Description |
|-------|-------------|
| Partner ID | API Partner ID from platform |
| Partner Key | API Partner Key |
| Shop ID | Your Shop ID |

### API Mode
- **Sandbox (MOCK)**: Testing mode with mock data
- **Production**: Real API calls (requires credentials)

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for full history.

### Latest (Unreleased)
- **Dry-Run Validation Pipeline** - validate 72 files บน production server
- Bug fixes: channel_config_views.xml, __manifest__.py, channel_product_field_mapping.py

### v1.2.0
- Architecture: Mixin pattern for channel.config
- Methods split into 4 mixins
- OAuth + Token management
- Connector base class + MOCK

---

## 📊 Progress

See [PROGRESS.md](PROGRESS.md) for detailed status.

| Phase | Status |
|-------|--------|
| Core Models | ✅ 100% |
| AI Auto-Fill | ✅ 100% |
| Media Fields | ✅ 95% |
| OAuth + Token | ✅ 100% |
| Architecture Refactor | ✅ 100% |
| Dry-Run Validation | ✅ 100% (72/72 files) |
| Real API Integration | 🟡 30% |

---

## 🧪 Testing

### Local Syntax Check
```bash
# Python syntax
python3 -m py_compile models/channel_config.py
python3 -m py_compile models/mixins/*.py

# XML syntax
python3 -c "import xml.etree.ElementTree; ET.parse('views/channel_config_views.xml')"
```

### Remote Dry-Run Validation (แนะนำ)
```bash
# 1. Upload module ไป server
scp -r -P 2206 multichannel_ai root@server:/tmp/test_module/

# 2. Validate
ssh -p 2206 root@server 'python3 /tmp/validate_xml.py && python3 /tmp/validate_python.py'
```

### Upgrade Module in Odoo
```bash
odoo -d your_db -u multichannel_ai --stop-after-init
```

---

## 📄 License

MIT License

---

**Version:** 1.3.0 (Unreleased) | **Updated:** September 4, 2026
