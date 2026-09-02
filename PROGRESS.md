# 📊 Multi-Channel AI Module — Progress Report

**อัปเดต:** 2 กันยายน 2569 | **สถานะ:** 🟡 ~90% Complete

---

## 📁 โครงสร้าง
```
multichannel_ai/
├── models/           (13 models + 3 inherit)
├── wizards/          (3)
├── controllers/      (3)
├── security/         (groups + 29 access rules)
├── views/            (Backend + Frontend UI)
├── data/             (demo_data)
├── i18n/             (th.po)
└── tests/            (4 test files)
ai_engine/
└── models/           (AI Engine)
```

---

## 📈 สถานะรวม

| หมวด | % | หมายเหตุ |
|------|---|-----------|
| Models (13 หลัก) | 90% | core 100%, ขาด AI functions |
| Wizards (3) | 100% | |
| Controllers (3) | 100% | |
| API Connectors | 60% | mock, ต้อง implement จริง |
| Security | 100% | Backend/Frontend แยกแล้ว |
| Tests | 80% | ขาด variant tests |
| Crons (6) | 100% | |
| i18n Thai | 100% | |
| Frontend UI | 100% | 6 pages |
| Channel List Module | 100% | ✅ สร้างเสร็จแล้ว |
| Field Mappings | 100% | ✅ 17 default mappings |
| **รวม** | **~90%** | |

---

## 🔗 Field Mappings (17 default mappings)

### Shopee (6 mappings)
| Odoo Field | Platform Field | Transform | Required |
|------------|---------------|-----------|----------|
| name | title | Direct | ✅ |
| list_price | price | Direct | ✅ |
| barcode | item_id | Direct | ❌ |
| condition | condition | Direct | ❌ |
| channel_weight | weight | Direct | ❌ |
| channel_brand | brand | Direct | ❌ |

### Lazada (6 mappings)
| Odoo Field | Platform Field | Transform | Required |
|------------|---------------|-----------|----------|
| name | name | Direct | ✅ |
| list_price | price | Direct | ✅ |
| barcode | item_id | Direct | ✅ |
| condition | condition_type | Lookup | ✅ |
| channel_weight | weight | Direct | ❌ |
| channel_brand | brand_name | Direct | ✅ |

### TikTok (5 mappings)
| Odoo Field | Platform Field | Transform | Required |
|------------|---------------|-----------|----------|
| name | product_title | Direct | ✅ |
| list_price | price | Direct | ✅ |
| barcode | sku_code | Direct | ❌ |
| condition | condition | Direct | ❌ |
| channel_weight | weight | Direct | ❌ |

---

## 🤖 AI Auto-Fill (Plan)

| Function | คำอธิบาย | สถานะ |
|----------|-----------|--------|
| `ai_auto_fill_fields()` | เติมทุก field อัตโนมัติ | 🚧 Plan |
| `ai_suggest_barcode()` | แนะนำ barcode จาก SKU | 🚧 Plan |
| `ai_suggest_condition()` | แนะนำ condition (new/used) | 🚧 Plan |
| `ai_suggest_brand()` | แนะนำ brand จากชื่อสินค้า | 🚧 Plan |
| `cron_ai_auto_fill_missing()` | Cron รายวัน auto-fill | 🚧 Plan |

### AI Fill Logic
```
Barcode: product.barcode → default_code → Generate 'CH{channel}{id}'
Condition: description (used/มือสอง) → default 'new'
Brand: keyword matching (Apple, Samsung, Sony, Xiaomi, etc.)
```

---

## 🖼️ Images & Videos (Plan)

### Image Model (เพิ่ม fields)
- `alt_text` - Alt text สำหรับ SEO
- `image_type` - main/gallery/detail/thumbnail
- `*_image_id` - Platform-specific IDs

### Video Model (ใหม่)
```python
class ChannelProductVideo(models.Model):
    name = fields.Char('Filename')
    video_path = fields.Char('Local Path')
    video_url = fields.Char('Public URL')
    storage_type = fields.Selection(['local', 's3', 'cloudinary'])
    duration = fields.Integer('Duration (s)')
    file_size = fields.Integer('Size (bytes)')
    state = fields.Selection(['draft', 'uploading', 'uploaded', 'error'])
```

### Storage Structure
```
/var/lib/odoo/filestore/multichannel_ai/videos/
└── channel_{id}/product_{id}/video_001.mp4
```

### Platform Limits
| Platform | Max Images | Video |
|----------|-----------|-------|
| Shopee | 50 | ✅ MP4 |
| Lazada | 15 | ✅ MP4 |
| TikTok | 9 | ✅ MP4 |
| LINE | 10 | ❌ |

---

## ❌ ยังขาด

### 🔴 Critical
| Model | Field/Function | สถานะ |
|-------|----------------|--------|
| channel.product | `ai_auto_fill_fields()` | 🚧 Plan |
| channel.product | `ai_suggest_*()` (3 functions) | 🚧 Plan |
| channel.product | `cron_ai_auto_fill_missing()` | 🚧 Plan |
| wizard | `ai_fill_wizard` | 🚧 Plan |
| channel.product.image | `alt_text`, `image_type` | 🚧 Plan |
| channel.product.video | **Model ใหม่** | 🚧 Plan |
| controllers | `video_controller.py` | 🚧 Plan |
| channel.product.variant | action_* functions | ⬜ Plan |
| channel.order | action_create_sale_order | ⬜ Plan |

---

## 📁 ไฟล์ที่ต้องสร้าง

| ประเภท | ไฟล์ | คำอธิบาย |
|--------|------|----------|
| Models | `channel_product_video.py` | Model สำหรับ video |
| Controllers | `video_controller.py` | Upload video endpoint |
| Wizards | `channel_product_ai_fill_wizard.py` | Wizard สำหรับ AI fill |
| Views | `channel_product_video_views.xml` | View สำหรับ video |
| Views | `channel_product_ai_fill_wizard_views.xml` | View สำหรับ wizard |
| Docs | `CHANGELOG.md` | บันทึกการเปลี่ยนแปลง |

---

**Updated:** September 2, 2026 | **Maintainer:** BBCNSShop Team