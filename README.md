# Odoo Multi-Channel AI Module

> Multi-Channel E-Commerce Integration for Odoo 16 with AI Engine (OpenRouter)

## 📋 สารบัญ
- [โครงสร้างโปรเจค](#-โครงสร้างโปรเจค)
- [Change Log](#-change-log)
- [Function การทำงาน](#-function-การทำงาน)
- [สถานะโปรเจค](#-สถานะโปรเจค)
- [TODO / สิ่งที่ต้องทำ](#-todo--สิ่งที่ต้องทำ)
- [การติดตั้ง](#-การติดตั้ง)

---

## 📁 โครงสร้างโปรเจค

```
Odoo-Multichanel-AI-Module/
├── ai_engine/                    # AI Engine Module
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/ai_engine.py       # AI Engine หลัก
│   └── views/ai_engine_views.xml
│
└── multichannel_ai/              # Multi-Channel Module
    ├── __init__.py / __manifest__.py / README.md
    ├── models/                   # 8 model files
    │   ├── channel_config.py
    │   ├── channel_product.py
    │   ├── channel_product_field_mapping.py
    │   ├── channel_product_image.py
    │   ├── channel_product_attribute.py
    │   ├── channel_order.py
    │   ├── sale_order_channel.py
    │   └── product_product_channel.py
    ├── controllers/              # 2 controller files
    │   ├── main_controller.py    # Dashboard & API
    │   └── webhook_controller.py # Webhook
    ├── wizards/                  # 2 wizard files
    │   ├── add_to_channel_wizard.py
    │   └── profit_calculator_wizard.py
    ├── views/                    # 14 XML view files
    ├── data/                     # Demo Data
    ├── security/                 # Access Control
    ├── reports/                  # Reports
    └── static/                   # JS & CSS
```

---

## 📝 Change Log

### v1.0.0 - 2026-09-02
**Initial Release**

#### ✅ สิ่งที่ทำเสร็จแล้ว:
- [x] สร้างโครงสร้างโมดูล `ai_engine` และ `multichannel_ai`
- [x] รองรับ OpenRouter API (GPT-4o, Claude, Gemini, etc.)
- [x] เปลี่ยน `openrouter_model` เป็น Char field (ใส่ model name เองได้)
- [x] รองรับ Free Models บน OpenRouter
- [x] ระบบจำแนกประเภทสินค้าด้วย AI (`classify_product`)
- [x] ระบบแนะนำราคาด้วย AI (`recommend_price`)
### 🔷 AI Engine Module

| Function | จุดประสงค์ |
|----------|------------|
| `get_default_engine()` | รับ engine ค่าเริ่มต้น หรือสร้างใหม่ |
| `classify_product(data)` | จำแนกประเภทสินค้าด้วย AI |
| `recommend_price(data, channel)` | แนะนำราคาขายที่เหมาะสม |
| `calculate_profit(price, cost, channel)` | คำนวณกำไรสุทธิ |
| `_call_ai(prompt)` | เรียก OpenRouter API |
| `_call_local(prompt)` | เรียก Local LLM (Ollama) |

---

### 🔷 Channel Config

| Function | จุดประสงค์ |
|----------|------------|
| `test_connection()` | ทดสอบการเชื่อมต่อ API |
| `action_view_products()` | เปิดหน้าดูสินค้า |
| `action_view_orders()` | เปิดหน้าดูคำสั่งซื้อ |

---

### 🔷 Channel Product

| Function | จุดประสงค์ |
|----------|------------|
| `action_check_completeness()` | ตรวจสอบข้อมูลก่อนซิงค์ |
| `_validate_for_sync()` | ตรวจสอบฟิลด์ที่จำเป็น |
| `sync_to_channel()` | ซิงค์สินค้าไปยังช่องทาง |
| `_sync_shopee()` | ซิงค์ไป Shopee |
| `_sync_lazada()` | ซิงค์ไป Lazada |
| `_sync_tiktok()` | ซิงค์ไป TikTok |

---

### 🔷 Channel Order

| Function | จุดประสงค์ |
|----------|------------|
| `create_from_webhook(code, data)` | สร้างคำสั่งซื้อจาก Webhook |
| `action_create_sale_order()` | แปลงเป็น Odoo Sale Order |
| `action_confirm()` / `action_cancel()` | เปลี่ยนสถานะ |

---

### 🔷 Product Extension

| Function | จุดประสงค์ |
|----------|------------|
| `_toggle_channel(code, field)` | เพิ่ม/ลบสินค้าออกจากช่องทาง |
| `action_add_all_channels()` | เพิ่มสินค้าลงทุกช่องทาง |
| `action_sync_to_channels()` | ซิงค์ไปยังทุกช่องทาง |

---

### 🔷 Wizards

**AddToChannelBulkWizard:**
- `action_add_to_channel()` - เพิ่มสินค้าจำนวนมาก
- ตัวเลือก: AI Pricing, Fixed Price, Stock Mode

**ProfitCalculatorWizard:**
- `_compute_results()` - คำนวณกำไร Real-time
- แสดง: VAT, Platform Fee, Payment Fee, Shipping, Margin %, Break-even

---

### 🔷 Controllers

**MainController:**
| Route | Method | จุดประสงค์ |
|-------|--------|------------|
| `/multichannel/dashboard` | GET | Dashboard |
| `/multichannel/sync` | GET | หน้า Sync |
| `/multichannel/api/products` | GET | API สินค้า |
| `/multichannel/api/pricing` | POST | API ราคา AI |

**WebhookController:**
| Route | Method | จุดประสงค์ |
|-------|--------|------------|
| `/multichannel/shopee/webhook` | POST | Shopee |
| `/multichannel/lazada/webhook` | POST | Lazada |
| `/multichannel/tiktok/webhook` | POST | TikTok |
- [x] คำนวณกำไรสุทธิรวม VAT และค่าธรรมเนียม
- [x] รองรับ 3 ช่องทาง: Shopee, Lazada, TikTok Shop
- [x] ระบบซิงค์สินค้าไปยังช่องทาง
- [x] ระบบ Webhook รับคำสั่งซื้ออัตโนมัติ
- [x] Wizard เพิ่มสินค้าจำนวนมาก
- [x] Wizard คำนวณกำไร
- [x] ระบบ Field Mapping (Odoo → Platform)
- [x] ระบบ Image Upload
- [x] ระบบ Attribute Mapping
- [x] ระบบ Order Processing
- [x] ระบบ Sale Order Integration
- [x] คำนวณค่าธรรมเนียม
- [x] รองรับ VAT 7% (Thailand)
- [x] Push ขึ้น GitHub
- [x] สร้าง `.gitignore`
- [x] **Wizard Auto-Fill Channel Product Fields**

### 🔷 Wizards

**AddToChannelBulkWizard:**
- `action_add_to_channel()` - เพิ่มสินค้าจำนวนมาก
- ตัวเลือก: AI Pricing, Fixed Price, Stock Mode

**ProfitCalculatorWizard:**
- `_compute_results()` - คำนวณกำไร Real-time
- แสดง: VAT, Platform Fee, Payment Fee, Shipping, Margin %, Break-even

**ChannelProductAIFillWizard:**
- `action_fill()` - เติม barcode, condition, brand อัตโนมัติ
- ตัวเลือก: เลือก Channel, Fill Barcode, Fill Condition, Fill Brand, Limit, Only Incomplete

---

## ⚙️ Function การทำงาน

---

## 📝 Change Log

### 🔷 Channel Product - AI Auto-Fill (2026-09-02)

| Feature | คำอธิบาย | สถานะ |
|---------|-----------|--------|
| `ai_suggest_barcode()` |  Recommendations barcode จาก product.barcode → default_code → CH{channel}{id} | ✅ เสร็จแล้ว |
| `ai_suggest_condition()` |  Recommendations condition (new/used/refurbished) จาก description | ✅ เสร็จแล้ว |
| `ai_suggest_brand()` |  Recommendations brand จากชื่อสินค้า (Apple, Samsung, Xiaomi, ฯลฯ) | ✅ เสร็จแล้ว |
| `ai_auto_fill_fields()` |  เติมทุก field อัตโนมัติ (barcode, condition, brand) | ✅ เสร็จแล้ว |
| `cron_ai_auto_fill_missing()` |  Cron รายวัน auto-fill products ที่ขาดข้อมูล | ✅ เสร็จแล้ว |
| `channel_product_ai_fill_wizard` |  Wizard สำหรับ manual trigger AI auto-fill | ✅ เสร็จแล้ว |
| `channel_product_ai_fill_views.xml` |  View สำหรับ AI Fill Wizard | ✅ เสร็จแล้ว |

**AI Fill Logic:**
```
Barcode: product.barcode → default_code → Generate 'CH{channel}{id}'
Condition: description (used/มือสอง) → default 'new'
Brand: keyword matching (Apple, Samsung, Sony, Xiaomi, etc.)
```

---

### v1.0.0 - 2026-09-02
**Initial Release**

#### ✅ สิ่งที่ทำเสร็จแล้ว:
- [x] สร้างโครงสร้างโมดูล `ai_engine` และ `multichannel_ai`
- [x] รองรับ OpenRouter API (GPT-4o, Claude, Gemini, etc.)
- [x] เปลี่ยน `openrouter_model` เป็น Char field (ใส่ model name เองได้)
- [x] รองรับ Free Models บน OpenRouter
- [x] ระบบจำแนกประเภทสินค้าด้วย AI (`classify_product`)
- [x] ระบบوصาชา price ด้วย AI (`recommend_price`)