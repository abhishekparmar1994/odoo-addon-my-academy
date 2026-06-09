from odoo import models, fields, api

class Slide(models.Model):
    _inherit = 'slide.slide'

    is_sequential_locked = fields.Boolean(
        string="Is Sequential Locked",
        compute="_compute_is_sequential_locked"
    )

    def _compute_is_sequential_locked(self):
        # Batch evaluation to optimize DB queries
        partner_id = self.env.user.partner_id.id
        for slide in self:
            # Administrators, publishers, categories, or public users shouldn't be locked
            if (slide.is_category or 
                self.env.user._is_public() or 
                not slide.channel_id.is_member or 
                slide.channel_id.can_publish):
                slide.is_sequential_locked = False
                continue

            # Get all published content slides in the channel (excluding certifications)
            # which are ordered by Odoo's default sequence/ordering
            ordered_slides = slide.channel_id.slide_content_ids.filtered(
                lambda s: s.is_published and s.slide_category != 'certification'
            )
            
            # Find which of these the current partner has completed
            completed_slide_partners = self.env['slide.slide.partner'].sudo().search([
                ('partner_id', '=', partner_id),
                ('slide_id', 'in', ordered_slides.ids),
                ('completed', '=', True)
            ])
            completed_slide_ids = set(completed_slide_partners.mapped('slide_id.id'))

            is_locked = False
            for s in ordered_slides:
                if s.id == slide.id:
                    break
                if s.id not in completed_slide_ids:
                    is_locked = True
                    break
            
            slide.is_sequential_locked = is_locked

    def get_uncompleted_lessons(self):
        """ Returns all published lessons in the channel that the current user has not completed """
        self.ensure_one()
        # Get all published lessons in the course, excluding certification slides themselves
        lessons = self.channel_id.slide_content_ids.filtered(
            lambda s: s.is_published and s.slide_category != 'certification'
        )
        # Filter for lessons the user has not completed yet
        return lessons.filtered(lambda s: not s.user_has_completed)
