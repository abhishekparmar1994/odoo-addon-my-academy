{
    'name': 'My Academy Webmyne',
    'version': '19.0.1.0.0',
    'summary': 'Custom eLearning - lesson gates, paid certificates, Stripe payment.',
    'category': 'Website/eLearning',
    'author': 'Abhishek Parmar - Webmyne',
    'depends': [
        'website_slides',
        'website_slides_survey',
        'website_sale',
        'sale',
        'website_sale_slides',
        'payment_stripe',
    ],
    'data': [
        'data/course_data.xml',
        # Website → Configuration → Payment Providers → Stripe
        'views/survey_survey_views.xml',
        'views/certificate_payment_templates.xml',
        'views/slides_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'my_academy_modifications/static/src/js/slides_course_page_override.js',
        ],
    },
    'installable': True,
    'application': False,
    'currency': 'USD',
    'license': 'OPL-1',
    # Changed 'license' to 'OPL-1': Changing the license from 'LGPL-3' (open source) to 'OPL-1' (Odoo Proprietary License v1.0) is a mandatory requirement by Odoo to sell proprietary/paid modules. 
    #This license prevents buyers from copying or redistributing your code to others for free.
}
