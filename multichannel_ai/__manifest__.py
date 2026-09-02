{
    "name": "Multi-Channel E-Commerce Integration",
    "version": "16.0.1.0",
    "category": "Sales",
    "summary": "Multi-channel e-commerce integration (Shopee, Lazada, TikTok Shop) with AI engine",
    "description": "Multi-Channel E-Commerce Integration for Odoo 16. Integrates with Shopee, Lazada, TikTok Shop via OpenRouter AI engine. Features: Channel product management with AI-powered pricing, Bulk add/remove products to channels, Bidirectional sync, Channel order webhook ingestion, Profit margin calculator, Sale order channel tracking, Data completeness validation.",
    "author": "Your Company",
    "website": "https://yourcompany.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "sale",
        "sale_management",
        "stock",
        "account",
        "product",
        "uom",
        "web",
        "ai_engine"
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        "data/channel_data.xml",
        "data/category_mapping.xml",
        "data/cron.xml",
        "views/channel_menus.xml",
        "views/channel_config_views.xml",
        "views/channel_product_views.xml",
        "views/channel_field_mapping_views.xml",
        "views/product_channel_views.xml",
        "views/add_to_channel_wizard_views.xml",
        "views/channel_order_views.xml",
        "views/sale_order_channel_views.xml",
        "views/product_channel_search_views.xml",
        "views/profit_calculator_views.xml",
        "views/channel_product_image_views.xml",
        "views/channel_product_attribute_views.xml",
        "views/product_template_views.xml",
        "views/templates/layout.xml",
        "views/templates/dashboard.xml",
        "views/templates/channel_products.xml",
        "views/templates/sync.xml",
        "views/templates/channels.xml"
    ],
    "demo": [
        "demo/demo.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "multichannel_ai/static/src/js/multichannel_widget.js",
            "multichannel_ai/static/src/css/multichannel.css"
        ]
    },
    "installable": true,
    "application": true,
    "auto_install": false
}