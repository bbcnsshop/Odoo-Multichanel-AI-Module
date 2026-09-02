# Changelog

All notable changes to the Multi-Channel AI Module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### 🚧 Planned

#### AI Auto-Fill Functions
- `ai_auto_fill_fields()` - เติมทุก field อัตโนมัติ
- `ai_suggest_barcode()` - แนะนำ barcode จาก SKU
- `ai_suggest_condition()` - แนะนำ condition (new/used)
- `ai_suggest_brand()` - แนะนำ brand จากชื่อสินค้า
- `cron_ai_auto_fill_missing()` - Cron รายวัน auto-fill

#### Images & Videos
- `channel.product.video` - Model สำหรับ video
- `video_controller.py` - Upload video endpoint
- AI Fill Wizard - Wizard สำหรับ manual trigger
- `alt_text`, `image_type` fields - Image metadata

---

## [1.1.0] - 2026-09-02

### ✅ Added

#### Channel List Module
- `channel.list.module` model - จัดการ Channel List
- `ChannelListAddWizard` - Wizard สำหรับเพิ่ม Channel ใหม่
- `action_activate()`, `action_deactivate()` - เปิด/ปิด Channel
- Demo data: Shopee, Lazada, TikTok

#### Platform Fields
- `channel.product.barcode` - สำหรับ Lazada (required)
- `channel.product.condition` - สภาพสินค้า (new/used/refurbished)

#### Field Mappings
- `channel.product.field.mapping` - Model สำหรับจัดการ mappings
- **17 default mappings** สำหรับ Shopee, Lazada, TikTok
- Transform types: Direct, Multiply, Divide, Lookup
- `is_required`, `default_value`, `transform_value` fields

#### Web View
- `/multichannel/field_mappings` - หน้า Field Mappings
- `/multichannel/api/field_mappings` - REST API (CRUD)
- Filter by Channel
- Color coding ตาม Channel

#### Controllers (เพิ่ม)
- `field_mappings_page()` - Web page
- `get_field_mappings()` - GET API
- `create_field_mapping()` - POST API (Manager)
- `update_field_mapping()` - PUT API (Manager)
- `delete_field_mapping()` - DELETE API (Manager)

### 📝 Documentation
- PROGRESS.md - อัปเดตสถานะล่าสุด
- AI_PROFILE.md - บทบาทผู้เชี่ยวชาญ

---

## [1.0.0] - 2026-09-01

### ✅ Added

#### Core Models (10 หลัก + 3 inherit)
- `channel.config` - ตั้งค่า Channel
- `channel.product` - สินค้าในแต่ละ Channel
- `channel.product.variant` - Variants
- `channel.product.attribute` - Attributes
- `channel.product.image` - รูปภาพ
- `channel.product.completeness` - ความสมบูรณ์ของข้อมูล
- `channel.product.field.mapping` - Field Mappings
- `channel.order` - ออร์เดอร์
- `channel.order.line` - รายการในออร์เดอร์
- `product.category.mapping` - Category Mapping
- `price.recommendation` - ราคาแนะนำจาก AI

#### Wizards
- `add.to.channel.bulk.wizard` - เพิ่มสินค้าหลายรายการ
- `profit.calculator.wizard` - คำนวณกำไร

#### API Connectors (Mock)
- `shopee.api` - Shopee API
- `lazada.api` - Lazada API
- `tiktok.api` - TikTok API

#### Controllers
- `main_controller` - Dashboard, Products, Orders pages

#### Security
- `group_multichannel_user` - สิทธิ์ User
- `group_multichannel_manager` - สิทธิ์ Manager
- 29 access rules

#### Cron Jobs (6)
- `cron_refresh_ai_prices` - รีเฟรชราคา AI
- `cron_check_completeness` - ตรวจสอบความสมบูรณ์
- `cron_sync_error_alert` - แจ้งเตือน sync error
- `cron_fetch_channel_orders` - ดึงออร์เดอร์จาก Channel

#### AI Engine
- `ai.engine` - AI Engine model
- Price recommendation logic

---

## [0.1.0] - 2026-08-31

### 🚧 Initial Setup
- Project structure
- Basic module skeleton
- Odoo manifest

---

<!--
## Template

### [Unreleased]

### Added
- New feature

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed feature

### Removed
- Removed feature

### Fixed
- Bug fix

### Security
- Vulnerability fix
-->