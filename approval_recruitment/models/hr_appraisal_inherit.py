from odoo import models, fields, api
from datetime import timedelta

from odoo.exceptions import UserError


class HrAppraisalInherit(models.Model):
    _inherit = 'hr.appraisal'

    manager_decision = fields.Selection([
        ('extension', 'Extension of Probation'),
        ('confirmation', 'Confirmation'),
    ], string="Manager Decision", tracking=True)

    probation_reason = fields.Text(string="Reason for Extension", help="Reason for probation extension", tracking=True)

    @api.onchange('manager_decision')
    def _onchange_manager_decision(self):
        if self.manager_decision == 'extension':
            self.probation_reason = ''  # Ensure reason field available

    @api.model
    def write(self, vals):
        res = super(HrAppraisalInherit, self).write(vals)
        for record in self:
            if vals.get('state') == 'done':
                record.action_apply_decision()
        return res

    def action_apply_decision(self):
        for record in self:
            contract = self.env['hr.employee'].search([
                ('employee_id', '=', record.employee_id.id),
            ], limit=1)
            if not contract:
                print(f"[Probation] No contract found for employee: {record.employee_id.name}")
                continue

            today = fields.Date.today()
            employee_email = record.employee_id.work_email or False
            if not employee_email:
                print(f"[Probation] No email set for employee: {record.employee_id.name}")
                continue

            print(f"[Probation] Preparing email for employee: {record.employee_id.name} ({employee_email})")
            print(f"[Probation] Manager decision: {record.manager_decision}")

            if record.manager_decision == 'extension':
                probation_start = fields.Date.today()
                probation_end = probation_start + timedelta(days=30)

                contract.probation_date_start = probation_start
                contract.date_end = probation_end

                contract.contract_type_id = self.env.ref('approval_man_power.contract_type_probation')
                contract.probation_reason = record.probation_reason
                contract.probation_status = 'extended'

                body = f"""
                Dear {record.employee_id.name},

                Your probation period has been extended for 1 month.
                Reason: {record.probation_reason}

                New contract end date: {contract.date_end}
                """
                print(f"[Probation] Sending probation extension email to {employee_email} with body:\n{body}")
                self.env['mail.mail'].sudo().create({
                    'subject': "Probation Extended",
                    'body_html': body,
                    'email_to': employee_email,
                    'auto_delete': True,
                }).send()

            elif record.manager_decision == 'confirmation':
                contract.contract_type_id = self.env.ref('hr.contract_type_permanent')
                contract.probation_date_start = today
                contract.date_end = False
                contract.probation_status = 'confirmed'
                contract.probation_reason = record.probation_reason

                body = f"""
                Dear {record.employee_id.name},

                Congratulations! You have been confirmed as a permanent employee.
                Your contract start date: {contract.probation_date_start}
                """
                print(f"[Probation] Sending confirmation email to {employee_email} with body:\n{body}")
                self.env['mail.mail'].sudo().create({
                    'subject': "Employee Confirmed",
                    'body_html': body,
                    'email_to': employee_email,
                    'auto_delete': True,
                }).send()