# Purpose: Inherit payment.transaction to:
#   1. Capture when a payment transaction is successfully processed.
#   2. Look up any unpaid successful certification attempts for the purchased certificate product.
#   3. Dispatch the congratulatory/certification email and set certification_email_sent to True.
# Dependencies: payment, sale, survey

from odoo import models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _post_process(self):
        """
        Purpose:
            Post-process successful/done/authorized payment transactions.
            Identify if a certificate product was purchased, find the user's completed
            certification attempts for that survey, and trigger the email dispatch.
        """
        # Call super first to let Odoo process the transactions and confirm the sales orders
        super(PaymentTransaction, self)._post_process()

        print(f"\n--- pt._post_process() custom logic triggered for {len(self)} txs ---")
        for tx in self.filtered(lambda t: t.state in ['done', 'authorized']):
            print(f"Processing Tx {tx.reference} (state: {tx.state}, partner: {tx.partner_id.id})")
            
            # Find all sales orders linked to the transaction
            orders = tx.sale_order_ids
            print(f"Linked sales orders for Tx {tx.reference}: {orders.mapped('name')}")
            if not orders:
                continue

            # Extract all purchased products
            product_ids = orders.mapped('order_line.product_id').ids
            print(f"Products in orders: {product_ids}")
            if not product_ids:
                continue
            
            # Find certification surveys linked to these products
            surveys = self.env['survey.survey'].sudo().search([
                ('certification', '=', True),
                ('certificate_product_id', 'in', product_ids),
            ])
            print(f"Matching certification surveys: {surveys.mapped('title')}")
            if not surveys:
                continue

            # Find successful, unsent attempts for this partner and these surveys
            uncompleted_attempts = self.env['survey.user_input'].sudo().search([
                ('partner_id', '=', tx.partner_id.id),
                ('survey_id', 'in', surveys.ids),
                ('scoring_success', '=', True),
                ('certification_email_sent', '=', False),
            ])
            print(f"Matching unsent successful survey attempts: {uncompleted_attempts.ids}")

            for attempt in uncompleted_attempts:
                is_paid = attempt._is_certificate_paid()
                print(f"Checking attempt {attempt.id} -> _is_certificate_paid: {is_paid}")
                # Double check that the attempt is paid now
                if is_paid:
                    print(f"Sending certification email for attempt {attempt.id}...")
                    if attempt.survey_id.certification_mail_template_id and not attempt.test_entry:
                        attempt.survey_id.certification_mail_template_id.send_mail(
                            attempt.id,
                            email_layout_xmlid="mail.mail_notification_light"
                        )
                        attempt.write({'certification_email_sent': True})
                        print("Email successfully dispatched and certification_email_sent marked True.")
                    else:
                        print(f"Skipped email send: mail template set? {bool(attempt.survey_id.certification_mail_template_id)}, test entry? {attempt.test_entry}")
