from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class LoansAndAdvancesReportWizard(models.TransientModel):
    _name = 'loans_advances_report.wizard'
    _description = 'Loans and Advances Report Wizard'

    date_from = fields.Datetime(string="Date From", required=True)
    date_to = fields.Datetime(string="Date To", required=True)
    department_id = fields.Many2one(
        comodel_name="hr.department", string="Department"
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee",
        tracking=True
    )
    # loan_id = fields.Many2one(
    #     comodel_name='loans',
    #     string='Loan',
    #     domain=[('state', '=', 'paid')]
    # )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError(_("End date cannot be before start date."))

    def action_generate_loans_report(self):
        self.ensure_one()

        data = {
            'employee_id': self.employee_id.id,
            'department_id': self.department_id.id if self.department_id else False,
            # 'loan_id': self.loan_id.id if self.loan_id else False,
            'date_from': str(self.date_from),
            'date_to': str(self.date_to),
        }
        return self.env.ref(
            'iet_hr_report_loans_and_advances.loans_report_excel_action'
        ).report_action(self, data=data)

