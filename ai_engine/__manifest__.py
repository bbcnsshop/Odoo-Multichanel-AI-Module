{
    'name': 'AI Engine - OpenRouter Integration',
    'version': '16.0.1.0',
    'category': 'Artificial Intelligence',
    'summary': 'AI Engine with OpenRouter, OpenAI, Claude support for product classification and pricing',
    'description': """
AI Engine - OpenRouter Integration
====================================
AI-powered product classification and pricing recommendations.

Features:
- OpenRouter API integration (GPT-4, Claude, Gemini, Llama, etc.)
- Local LLM support (Ollama)
- AI product classification
- AI pricing recommendations
- Profit and fee calculations (Thailand market)

Thailand Fee Configuration:
- Shopee: 5% commission, 2% payment fee, 2.5% shipping
- Lazada: 5% commission, 2% payment fee, 3% shipping
- TikTok Shop: 3.5% commission, 1.5% payment fee, 2% shipping

All calculations include Thai VAT 7%.
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'requests',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ai_engine_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}