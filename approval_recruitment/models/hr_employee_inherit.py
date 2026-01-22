from odoo import models, fields, api, _
from datetime import timedelta, date


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    _description = 'HR Employee'

    joining_date_recruit = fields.Date(string="Joining Date", copy=False, tracking=True)
    hr_id = fields.Many2one('res.users', 'HR')

    probation_status = fields.Selection([
        ('extended', 'Extension of Probation'),
        ('confirmed', 'Confirmed Employee'),
    ], string="Probation Status", tracking=True)

    probation_reason = fields.Text(string="Probation Reason", tracking=True)
    probation_date_start = fields.Date(string="Probation Start Date")
    probation_date_end = fields.Date(string="Probation End Date")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if res.get('joining_date_recruit'):
            res['probation_date_start'] = res['joining_date_recruit']
        return res

    @api.onchange('probation_date_start')
    def _onchange_probation_date_start(self):
        """Auto calculate probation end date as 30 days after start"""
        for record in self:
            if record.probation_date_start:
                record.probation_date_end = record.probation_date_start + timedelta(days=30)
            else:
                record.probation_date_end = False

    @api.model
    def _cron_probation_expiry_reminder(self):
        """Send reminder email 2 days before probation end date"""
        today = date.today()
        target_date = today + timedelta(days=1)  # reminder 2 days before expiry
        employees = self.env['hr.employee'].search([])
        print(employees, "Employees with probation expiring soon")

        for emp in employees:
            if emp.work_email:
                # Get base URL of Odoo
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

                # Fetch appraisal record (pending/new)
                appraisal = self.env['hr.appraisal'].search(
                    [('employee_id', '=', emp.id), ('state', 'in', ['new', 'pending'])],
                    limit=1
                )

                if appraisal:
                    action_id = self.env.ref('hr_appraisal.open_view_hr_appraisal_tree2').id
                    appraisal_url = f"{base_url}/web#id={appraisal.id}&model=hr.appraisal&view_type=form&action={action_id}"
                else:
                    action_id = self.env.ref('hr_appraisal.open_view_hr_appraisal_tree').id
                    appraisal_url = f"{base_url}/web#action={action_id}"

                print(f"Sending probation expiry mail to: {emp.work_email} for probation ending on {emp.probation_date_end}")
                mail_values = {
                    'subject': f"Your Probation Period is Ending on {emp.contract_date_end}",
                    'body_html': f"""
                        <p>Dear {emp.name},</p>
                        <p>Your probation period is set to end on <b>{emp.contract_date_end}</b>.</p>
                        <p>Please contact HR for confirmation or extension discussion.</p>
                        <p>
                        <a href="{appraisal_url}" style="
                            display:inline-block;
                            padding:10px 20px;
                            background-color:#0a6ebd;
                            color:white;
                            text-decoration:none;
                            border-radius:5px;">
                            Fill Appraisal Form
                        </a>
                        </p>
                        <p>Regards,<br/>HR Department</p>
                    """,
                    'email_from': emp.company_id.email or 'info@yourcompany.com',
                    'email_to': emp.work_email,
                    'email_cc': emp.hr_id.login if emp.hr_id else False,  # CC to HR user
                }
                self.env['mail.mail'].create(mail_values).send()
