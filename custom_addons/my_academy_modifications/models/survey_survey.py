# Purpose: Extends survey.survey with:
#   1. certificate_product_id field — links a purchasable product to each certification survey.
#   2. _assign_missing_certificate_products — called during module upgrade via data XML
#      to auto-link a fallback product to ALL certification surveys that have none set.
# Dependencies: product, survey

from odoo import api, models, fields


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    certificate_is_free = fields.Boolean(
        string='Is Certificate Free',
        default=False,
        help='If checked, this certificate PDF will be available for download instantly without any payment check.',
    )

    certificate_product_id = fields.Many2one(
        'product.product',
        string='Certificate Product',
        help='Product the student must purchase before downloading this certificate PDF.',
    )

    @api.model
    def _assign_missing_certificate_products(self, fallback_product_tmpl_id):
        """
        Purpose:
            Auto-link a fallback certificate product to every certification survey
            that currently has no certificate_product_id. Called from course_data.xml
            on every module upgrade, covering Odoo built-in demo surveys (e.g. English
            Course) that are not defined in our own XML records.

        Parameters:
            fallback_product_tmpl_id (int): ID of the product.template to use as fallback.

        Return:
            None

        Side Effects:
            Writes certificate_product_id on all unlinked certification survey records.
        """
        # Resolve template → first product variant
        tmpl = self.env['product.template'].browse(fallback_product_tmpl_id).exists()
        if not tmpl:
            return

        product = tmpl.product_variant_ids[:1]
        if not product:
            return

        # Find all certification surveys with no product linked, excluding free certificates
        unlinked_surveys = self.search([
            ('certification', '=', True),
            ('certificate_is_free', '=', False),
            ('certificate_product_id', '=', False),
        ])

        if unlinked_surveys:
            unlinked_surveys.write({'certificate_product_id': product.id})
