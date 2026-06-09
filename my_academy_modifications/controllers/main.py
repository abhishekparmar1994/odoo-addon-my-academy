# Purpose: Custom controller overrides for My Academy Modifications.
# Handles:
#   1. Lesson-completion gate before starting the certification quiz.
#   2. Lesson-completion + payment gate before downloading the certificate PDF.
#   3. A dedicated "pay for certificate" page that flows into Stripe checkout.
# Dependencies: survey, website_slides_survey, website_sale, sale

import werkzeug.exceptions
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.survey.controllers.main import Survey
from odoo.addons.website_slides_survey.controllers.slides import WebsiteSlidesSurvey
from odoo.addons.website_slides.controllers.main import WebsiteSlides, handle_wslide_error


class MyAcademySurvey(Survey):
    """
    Overrides the standard certificate-download route with two gates:

    Gate 1 — Lesson completion:  All course lessons must be finished.
    Gate 2 — Payment:            The student must purchase the certificate product.

    If not yet paid, the student is redirected to a dedicated payment page
    (/academy/certificate/pay/<survey_id>) which adds the product to cart and
    sends the browser straight to /shop/checkout where Stripe is available.
    """

    # ------------------------------------------------------------------
    # Certification PDF download — /survey/<id>/get_certification
    # ------------------------------------------------------------------

    @http.route(
        ['/survey/<int:survey_id>/get_certification'],
        type='http',
        auth='user',
        methods=['GET'],
        website=True,
    )
    def survey_get_certification(self, survey_id, **kwargs):
        """
        Purpose:
            Serve the certification PDF after verifying all gates are cleared.

        Parameters:
            survey_id (int): ID of the survey.survey record.

        Return:
            HTTP file response (PDF) on success.
            Redirect to /academy/certificate/pay/<survey_id> if payment needed.

        Errors:
            UserError — quiz not passed, or lessons not completed.

        Side Effects:
            None at this point (cart is managed in the pay endpoint).
        """
        # Gate 0: Survey must exist and be a certification survey
        survey = request.env['survey.survey'].sudo().browse(survey_id).exists()
        if not survey or not survey.certification:
            return request.redirect('/')

        # Gate 1: Student must have passed the quiz
        succeeded_attempt = request.env['survey.user_input'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('survey_id', '=', survey_id),
            ('scoring_success', '=', True),
        ], limit=1)

        if not succeeded_attempt:
            raise UserError(_("You have not passed the certification quiz yet."))

        # Gate 2: All course lessons must be completed
        cert_slide = request.env['slide.slide'].sudo().search([
            ('survey_id', '=', survey_id),
            ('slide_category', '=', 'certification'),
        ], limit=1)

        if cert_slide:
            uncompleted = cert_slide.get_uncompleted_lessons()
            if uncompleted:
                return request.render('my_academy_modifications.certification_locked_page', {
                    'slide': cert_slide,
                    'channel': cert_slide.channel_id,
                    'uncompleted_lessons': uncompleted,
                })

        # Gate 3: Payment check (if certificate is not free)
        is_free_cert = survey.certificate_is_free

        if not is_free_cert:
            if not survey.certificate_product_id:
                raise UserError(_(
                    "This certificate requires a payment product to be configured. "
                    "Please contact the administrator."
                ))

            if not succeeded_attempt._is_certificate_paid():
                # Not yet paid — redirect to our premium payment page
                return request.redirect('/academy/certificate/pay/%d' % survey_id)

        # All gates cleared → serve the PDF
        return self._generate_report(succeeded_attempt, download=True)

    # ------------------------------------------------------------------
    # Dedicated certificate payment page
    # ------------------------------------------------------------------

    @http.route(
        ['/academy/certificate/pay/<int:survey_id>'],
        type='http',
        auth='user',
        website=True,
    )
    def certificate_payment_page(self, survey_id, **kwargs):
        """
        Purpose:
            Render a dedicated "Purchase Certificate" page that shows the
            product price and a button that adds it to the cart and sends
            the student straight to /shop/checkout (where Stripe appears).

        Parameters:
            survey_id (int): ID of the survey.survey record.

        Return:
            Rendered QWeb template 'my_academy_modifications.certificate_payment_page'.
        """
        survey = request.env['survey.survey'].sudo().browse(survey_id).exists()
        if not survey or not survey.certificate_product_id:
            return request.redirect('/')

        product = survey.certificate_product_id
        currency = request.website.currency_id or product.currency_id

        return request.render(
            'my_academy_modifications.certificate_payment_page',
            {
                'survey': survey,
                'product': product,
                'currency': currency,
                'price': product.lst_price,
            }
        )
    
    # ------------------------------------------------------------------
    # Add certificate to cart and redirect to checkout (Stripe)
    # ------------------------------------------------------------------

    @http.route(
        ['/academy/certificate/add-to-cart/<int:survey_id>'],
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True,
    )
    def certificate_add_to_cart(self, survey_id, **kwargs):
        """
        Purpose:
            Add the certificate product to the student's cart and redirect
            to /shop/checkout so Stripe (or another provider) handles payment.

        Parameters:
            survey_id (int): ID of the survey.survey record.

        Return:
            Redirect to /shop/checkout.

        Side Effects:
            Creates or updates a sale.order (cart) with the certificate product.
        """
        survey = request.env['survey.survey'].sudo().browse(survey_id).exists()
        if not survey or not survey.certificate_product_id:
            return request.redirect('/')

        product = survey.certificate_product_id

        # Get or create the shopping cart
        order = request.cart
        if not order:
            order = request.website._create_cart()

        # Add the certificate product — skip cart verification for server-side adds
        order.with_context(skip_cart_verification=True)._cart_add(
            product_id=product.id,
            quantity=1,
        )

        # Go straight to checkout where Stripe payment options appear
        return request.redirect('/shop/checkout')


class MyAcademyWebsiteSlidesSurvey(WebsiteSlidesSurvey):
    """
    Overrides the certification URL endpoint to enforce lesson-completion
    before the student is allowed to start the certification quiz.
    """

    @http.route(
        ['/slides_survey/slide/get_certification_url'],
        type='http',
        auth='user',
        website=True,
    )
    def slide_get_certification_url(self, slide_id, **kw):
        """
        Purpose: Block quiz access until all prerequisite lessons are done.

        Parameters:
            slide_id (int|str): ID of the certification slide.

        Return:
            Redirect to the survey start URL, or raises UserError listing
            remaining lessons.

        Errors:
            UserError — if the student has not completed all course lessons.
            NotFound  — if the slide does not exist or is inaccessible.
        """
        fetch_res = self._fetch_slide(slide_id)
        if fetch_res.get('error'):
            raise werkzeug.exceptions.NotFound()

        slide = fetch_res['slide']

        # Block quiz start if any lesson is not yet completed
        uncompleted = slide.get_uncompleted_lessons()
        if uncompleted:
            return request.render('my_academy_modifications.certification_locked_page', {
                'slide': slide,
                'channel': slide.channel_id,
                'uncompleted_lessons': uncompleted,
            })

        return super().slide_get_certification_url(slide_id, **kw)


class MyAcademyWebsiteSlides(WebsiteSlides):
    """
    Overrides core eLearning website routes to enforce sequential lesson gating:
    - Blocks viewing a slide/lesson if a preceding lesson is not yet completed.
    - Blocks completion actions and fetching HTML content for locked slides.
    """

    @http.route('/slides/slide/<model("slide.slide"):slide>', type='http', auth="public",
                website=True, sitemap=True, handle_params_access_error=handle_wslide_error)
    def slide_view(self, slide, **kwargs):
        if slide.is_sequential_locked:
            # Find the first uncompleted slide in the channel to redirect the student to
            uncompleted = slide.channel_id.slide_content_ids.filtered(
                lambda s: s.is_published and s.slide_category != 'certification' and not s.user_has_completed
            )
            if uncompleted:
                return request.redirect(f"/slides/slide/{uncompleted[0].id}?sequential_lock=1")
            else:
                return request.redirect(f"/slides/{slide.channel_id.id}")

        return super().slide_view(slide, **kwargs)

    @http.route('/slides/slide/<model("slide.slide"):slide>/set_completed',
                website=True, type="http", auth="user", handle_params_access_error=handle_wslide_error)
    def slide_set_completed_and_redirect(self, slide, next_slide_id=None):
        if slide.is_sequential_locked:
            return request.redirect(f'/slides/slide/{slide.id}')
        return super().slide_set_completed_and_redirect(slide, next_slide_id=next_slide_id)

    @http.route('/slides/slide/set_completed', website=True, type="jsonrpc", auth="public")
    def slide_set_completed(self, slide_id):
        slide = request.env['slide.slide'].browse(int(slide_id)).exists()
        if slide and slide.is_sequential_locked:
            return {'error': 'lesson_locked'}
        return super().slide_set_completed(slide_id)

    @http.route('/slides/slide/get_html_content', type="jsonrpc", auth="public", website=True)
    def get_html_content(self, slide_id):
        slide = request.env['slide.slide'].browse(int(slide_id)).exists()
        if slide and slide.is_sequential_locked:
            return {'error': 'lesson_locked', 'html_content': ''}
        return super().get_html_content(slide_id)
