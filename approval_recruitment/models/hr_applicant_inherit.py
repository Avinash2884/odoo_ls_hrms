from odoo import models, fields, api , _

class HrApplicantInherit(models.Model):
    _inherit = 'hr.applicant'
    _description = 'HR Applicant'

    mark = fields.Float(string="Overall Rating", compute="_compute_mark", store=True)
    evaluation_ids = fields.One2many("hr.applicant.evaluation", "applicant_id", string="Evaluations")
    is_suitable = fields.Selection([("yes", "Yes"), ("no", "No")], string="Suitability")
    application_status = fields.Selection(
        selection_add=[('hold', 'Hold')]
    )

    # @api.depends('refuse_reason_id', 'date_closed', 'stage_id', 'active')
    # def _compute_application_status(self):
    #     super(HrApplicantInherit, self)._compute_application_status()
    #     for applicant in self:
    #         if applicant.stage_id and applicant.stage_id.name == 'Hold':
    #             applicant.application_status = 'hold'

    @api.depends("evaluation_ids.education", "evaluation_ids.professional", "evaluation_ids.personality",
                 "evaluation_ids.communication", "evaluation_ids.knowledge", "evaluation_ids.experience")
    def _compute_mark(self):
        for rec in self:
            if rec.evaluation_ids:
                total = 0
                for ev in rec.evaluation_ids:
                    total += (ev.education + ev.professional + ev.personality +
                              ev.communication + ev.knowledge + ev.experience)
                rec.mark = total / len(rec.evaluation_ids)
            else:
                rec.mark = 0.0

    def _send_stage_change_email(self, message):
        """Send a professional notification email to applicant when stage changes"""
        for applicant in self:
            if applicant.email_from:
                body = f"""
                    <p>Dear {applicant.partner_name or 'Candidate'},</p>
                    <p>{message}</p>
                    <p>We appreciate your time and interest in joining our team.</p>
                    <p>Our HR department will keep you informed about further updates.</p>
                    <p>Best regards,<br/>HR Team</p>
                """
                print(f"[Recruitment] Sending stage change email to {applicant.email_from} with body:\n{body}")

                self.env['mail.mail'].sudo().create({
                    'subject': "Update on Your Recruitment Process",
                    'body_html': body,
                    'email_to': applicant.email_from,
                    'auto_delete': True,
                }).send()

    def _update_stage_based_on_mark(self):
        """Move applicant from stage_job2 → stage_job4 based on overall evaluation mark"""
        if self.env.context.get('skip_stage_update'):
            return

        stage_job2 = self.env.ref("hr_recruitment.stage_job2", raise_if_not_found=False)
        stage_job3 = self.env.ref("hr_recruitment.stage_job3", raise_if_not_found=False)

        if stage_job2 and stage_job3 and self.stage_id == stage_job2:
            if self.mark >= 40:
                # use context to avoid recursion
                self.with_context(skip_stage_update=True).write({'stage_id': stage_job3.id})
                # Send email to candidate
                self._send_stage_change_email(
                    f"Congratulations! You have been moved to the stage <b>{stage_job3.name}</b>."
                )
                self._reorder_contract_proposal_stage()

    def write(self, vals):
        res = super().write(vals)
        for applicant in self:
            applicant._update_stage_based_on_mark()
        self._reorder_contract_proposal_stage()
        return res

    def _reorder_contract_proposal_stage(self):
        """Reorder applicants in Contract Proposal stage by highest mark first without recursion"""
        contract_stage = self.env.ref("hr_recruitment.stage_job4", raise_if_not_found=False)
        if not contract_stage:
            return

        # Use sudo() and update without triggering write() hooks
        applicants = self.env['hr.applicant'].sudo().search(
            [('stage_id', '=', contract_stage.id)], order="mark desc"
        )
        seq = 1
        for applicant in applicants:
            # direct SQL write to avoid triggering write() hooks
            self.env.cr.execute(
                "UPDATE hr_applicant SET sequence=%s WHERE id=%s",
                (seq, applicant.id)
            )
            seq += 1

    def action_select_applicant(self):
        """Move applicant to stage_job4 when Select is clicked"""
        stage = self.env.ref('hr_recruitment.stage_job4', raise_if_not_found=False)
        if stage:
            self.write({'stage_id': stage.id})
        else:
            # Optional: fallback if stage not found
            raise ValueError("Stage 'hr_recruitment.stage_job4' not found in database.")
        return True

    def action_approval_applicant(self):
        """Move applicant to stage_job4 when Select is clicked"""
        stage = self.env.ref('approval_man_power.stage_job6', raise_if_not_found=False)
        if stage:
            self.write({'stage_id': stage.id})
        else:
            # Optional: fallback if stage not found
            raise ValueError("Stage 'approval_man_power.stage_job6' not found in database.")
        return True

    def action_document_validation_applicant(self):
        """Move applicant to stage_job4 when Select is clicked"""
        stage = self.env.ref('approval_man_power.stage_job7', raise_if_not_found=False)
        if stage:
            self.write({'stage_id': stage.id})
        else:
            # Optional: fallback if stage not found
            raise ValueError("Stage 'approval_man_power.stage_job7' not found in database.")
        return True

    def action_hold_applicant(self):
        pass

