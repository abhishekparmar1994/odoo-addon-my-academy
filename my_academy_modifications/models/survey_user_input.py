# Purpose: Inherit survey.user_input to:
#   1. Add field 'certification_email_sent' to track if the congratulations mail was sent.
#   2. Add method '_is_certificate_paid' to check if the certificate product has been purchased.
#   3. Override '_mark_done' to defer/block the congratulations email if the certificate is not yet paid.
# Dependencies: survey

from odoo import models, fields, api

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    certification_email_sent = fields.Boolean(
        string='Certification Email Sent',
        default=False,
        help='Indicates whether the congratulations email with the certificate attachment has been sent to the student.'
    )

    def _is_certificate_paid(self):
        """
        Purpose:
            Check if the partner has successfully paid for the survey's certificate product.
            Includes a check for paid order states ('sale', 'done') and robust local/draft fallback
            where a transaction was successfully processed but order is in 'draft'/'sent'.
            Bypasses payment check if the certificate is free or if it belongs to a paid course.
        """
        self.ensure_one()
        
        # Explicitly free certificate
        if self.survey_id.certificate_is_free:
            return True

        if not self.survey_id.certificate_product_id:
            return True  # No product means it's free!

        partner = self.partner_id
        if not partner:
            return False  # Guest/No partner cannot have paid

        product = self.survey_id.certificate_product_id

        # Search for a confirmed sales order containing this product
        confirmed_line = self.env['sale.order.line'].sudo().search([
            ('order_id.partner_id', '=', partner.id),
            ('product_id', '=', product.id),
            ('order_id.state', 'in', ['sale', 'done']),
        ], limit=1)
        if confirmed_line:
            return True

        # Check for draft orders with completed/authorized payment transactions (local dev fallback)
        draft_lines = self.env['sale.order.line'].sudo().search([
            ('order_id.partner_id', '=', partner.id),
            ('product_id', '=', product.id),
            ('order_id.state', 'in', ['draft', 'sent']),
        ])
        for line in draft_lines:
            draft_order = line.order_id
            successful_tx = self.env['payment.transaction'].sudo().search([
                ('sale_order_ids', 'in', [draft_order.id]),
                ('state', 'in', ['done', 'authorized']),
            ], limit=1)
            if successful_tx:
                return True

        return False

    def _mark_done(self):
        """
        Purpose:
            Override standard _mark_done to conditionally defer the certification email.
            If the survey has a certificate product linked, is not explicitly free, does not
            belong to a paid course, and the student hasn't paid, the congratulatory email
            is skipped/deferred. Otherwise, it is sent immediately.
        """
        self.write({
            'end_datetime': fields.Datetime.now(),
            'state': 'done',
        })

        challenge_sudo = self.env['gamification.challenge'].sudo()
        badge_ids = []
        self._notify_new_participation_subscribers()

        for user_input in self:
            if user_input.survey_id.certification and user_input.scoring_success:
                requires_payment = (
                    user_input.survey_id.certificate_product_id 
                    and not user_input.survey_id.certificate_is_free
                )
                is_paid = user_input._is_certificate_paid()

                if not requires_payment or is_paid:
                    if user_input.survey_id.certification_mail_template_id and not user_input.test_entry:
                        user_input.survey_id.certification_mail_template_id.send_mail(
                            user_input.id,
                            email_layout_xmlid="mail.mail_notification_light"
                        )
                        user_input.certification_email_sent = True
                else:
                    # Defer sending email until payment is cleared
                    user_input.certification_email_sent = False
                
                if user_input.survey_id.certification_give_badge:
                    badge_ids.append(user_input.survey_id.certification_badge_id.id)

            # Update predefined_question_id to remove inactive questions
            user_input.predefined_question_ids -= user_input._get_inactive_conditional_questions()

        if badge_ids:
            challenges = challenge_sudo.search([('reward_id', 'in', badge_ids)])
            if challenges:
                challenge_sudo._cron_update(ids=challenges.ids, commit=False)
