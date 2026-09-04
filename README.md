# Odoo Multi-Channel AI Module

> Multi-Channel E-Commerce Integration for Odoo 16 with AI Engine (OpenRouter)

รองรับ Shopee, Lazada, TikTok Shop - รวม Sync, OAuth, AI Auto-Fill

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

### Latest (v1.2.0)
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
| Real API Integration | 🟡 30% |

---

## 🧪 Testing

```bash
# Syntax check
python3 -m py_compile models/channel_config.py
python3 -m py_compile models/mixins/*.py

# Upgrade module in Odoo
odoo -d your_db -u multichannel_ai --stop-after-init
```

---

## 📄 License

MIT License

---

**Version:** 1.2.0 | **Updated:** September 4, 2026
