from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time, timedelta
# import calendar


class HREmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    days_over_5_years = fields.Float(string='Days Over 5 Years', digits=(12, 2), readonly=True)
    days_under_5_years = fields.Float(string='Days Under 5 Years', digits=(12, 2), readonly=True)
    total_service_days = fields.Float(string='Total Service Days', digits=(12, 2), readonly=True)
    total_service_years = fields.Float(string='Total Service Years', digits=(12, 2), readonly=True)

    service_bonus_days = fields.Float(string='End of Service Benefit', digits=(12, 2), readonly=True)
    amount_of_service_bonus_days = fields.Float(digits=(12, 2), string="Amount Of Service Bonus Days", readonly=True)

    custom_hire_date = fields.Date(string="Hire Date", compute='get_hire_date', )
    return_vacation_ids = fields.One2many('return.vacation', 'employee_id')
    return_date_lines_config = fields.Boolean(compute='get_date_lines_config', )


    # thirty_days = fields.Boolean(string="30 Days")
    is_on_vacation = fields.Boolean(string='On Vacation', )
    leave_policy = fields.Selection([
        ('21', '21'), ('30', '30')
    ], tracking=True, string='Leave Days Policy', default='21', required=True)

    leave_days_balance = fields.Float(string='Leave Days Balance', digits=(12, 2), compute='_compute_net_days',
                                      readonly=True)
    amount_of_leave_days_balance = fields.Float(string='Amount Of Leave Days Balance', digits=(12, 2),
                                                compute='_compute_net_days', readonly=True)
    # last_time_off_last_days = fields.Float(string='Last Time Off')

    leave_days_taken = fields.Float(string='Leave Days Taken', readonly=True)
    amount_of_days_taken = fields.Float(compute="_compute_net_days", digits=(12, 2), string="Amount Of Days Taken",
                                        readonly=True)

    net_days = fields.Float(string='Leave Net Days', compute="_compute_net_days", digits=(12, 2), readonly=True)
    amount_of_net_days = fields.Float(compute="_compute_net_days", digits=(12, 2), help="Amount Of Net Days",
                                      readonly=True)

    last_working_date_before_vacation = fields.Date(string="last working date in return vacation", required=False, )
    contract_start_date_or_today = fields.Date(string="today date or first contract date", required=False, )
    vacation_expiration_date = fields.Date(string="more than vacation today date", required=False,
                                         help="Today Date or False")
    return_date_after_vacation = fields.Date(string="return_date for more than vacation or today date", required=False, )
    custom_today_date = fields.Date(string="Today Date", required=False, )
    custom_initial_contract_date = fields.Date(string="First Contract Date", required=False)
    contract_end_date_or_current_date = fields.Date(string="contract end date or today date", required=False, )
    initial_contract_date_or_null = fields.Date(string="first contract date or False", required=False,
                                       help="first contract date or False")

    def get_date_lines_config(self):
        for employee in self:
            config = self.env['ir.config_parameter'].sudo()
            employee.return_date_lines_config = config.get_param('iet_hr_holidays_enhancement.hr_employee_return_date_lines', )


    # def _compute_is_on_vacation(self):
    #     for rec in self:
    #         return_vacation = self.env['return.vacation'].search([('employee_id', '=', rec.id), ('state', '=', 'draft')])
    #         if return_vacation:
    #             rec.is_on_vacation = True
    #         else:
    #             rec.is_on_vacation = False


    @api.onchange('days_under_5_years')
    def _onchange_days_under_5_years(self):
        for rec in self:
            if rec.days_under_5_years == 1800 and rec.leave_policy != '30':
                rec.leave_policy = '30'

    def get_hire_date(self):
        for rec in self:
            first_contract = self.env['hr.contract'].search([('employee_id', '=', rec.id), ('state', '!=', 'cancel')],
                                                            order = 'date_start asc', limit=1)
            if first_contract:
                rec.custom_hire_date = first_contract.date_start
            else:
                rec.custom_hire_date = False


    def get_exceptional_request_departure_resignation(self, id, date_from, date_to):
        # contract = self.env['hr.contract'].search([('employee_id', '=', id)], limit=1)
        the_employee_id = self.env['hr.employee'].search(
            ['|', ('id', '=', id), ('active', '=', True), ('active', '=', False)])
        result = 0
        if the_employee_id:
            total_days = the_employee_id.days_over_5_years + the_employee_id.days_under_5_years
            compensation = the_employee_id.total_salary
            if total_days < 720:
                result = 0
            elif 720 <= total_days <= 1800:
                result = (((compensation / 2) * (total_days / 360))) / 3
            elif 1800 < total_days <= 3600:
                result = ((compensation * (2 / 3)) * (total_days / 360))
            else:
                result = (compensation * (total_days / 360))
        result = self.company_id.currency_id.round(result)
        return result

    def get_termination_of_the_contract_by_the_company(self, id, date_from, date_to):
        contract = self.env['hr.contract'].search([('employee_id', '=', id), ('state', '=', 'open')], limit=1)
        # ('state', 'in', ['close', 'open'])
        result = 0
        if contract:
            start_date = contract.first_contract_date
            end_date = contract.date_end
            difference = relativedelta(end_date, start_date)
            total_days = difference.years * 360 + difference.months * 30 + difference.days
            compensation = contract.wage + contract.l10n_sa_housing_allowance + contract.l10n_sa_transportation_allowance + contract.l10n_sa_other_allowances
            if total_days <= 1800:
                result = (compensation / 2 * total_days / 360)
            else:
                result = (compensation * (total_days / 360))
        result = self.company_id.currency_id.round(result)
        return result

    @api.depends('leave_days_taken', "total_service_days")
    def _compute_net_days(self):
        for rec in self:
            policy_rate = 30 / 360 if rec.leave_policy == '30' else 21 / 360
            rec.leave_days_balance = rec.total_service_days * policy_rate
            rec.net_days = rec.leave_days_balance - rec.leave_days_taken
            if rec.net_days > 0:
                rec.net_days = rec.net_days
            else:
                rec.net_days = 0
            contract = rec.contract_id
            if contract:
                total_salary = contract.total_salary
                p_day = total_salary / 30
                rec.amount_of_leave_days_balance = rec.leave_days_balance * p_day
                rec.amount_of_net_days = rec.net_days * p_day
                rec.amount_of_days_taken = rec.leave_days_taken * p_day
            else:
                rec.amount_of_leave_days_balance = 0
                rec.amount_of_net_days = 0
                rec.amount_of_days_taken = 0


    def compute_custom_accrual_leave(self):
        print('compute_custom_accrual_leave')
        # hr_contract = self.env['hr.employee'].search(['|', ('active','=',True), ('active','=',False)])
        for rec in self:
            # all_return_vacation = self.env['return.vacation'].search([('employee_id', '=', rec.id),
            #                                                           ('time_off_types', '=', 'annual_vacation')])
            # if all_return_vacation:
            #     if len(all_return_vacation) == 1:
            #         if all_return_vacation.leave_id.last_working_date:
            #             # dat1 all_return_vacation.leave_id.last_working_date
            #             print('return_vacation.leave_id.last_working_date',
            #                   all_return_vacation.leave_id.last_working_date)
            #             d1 = all_return_vacation.leave_id.last_working_date
            #             if rec.first_contract_date:
            #                 d2 = rec.first_contract_date
            #             else:
            #                 d2 = date.today()
            #             delta = relativedelta(d1, d2)
            #             rec.last_working_date_before_vacation = d1
            #             rec.contract_start_date_or_today = d2
            #             rec.total_service_days = (delta.years * 360 + delta.months * 30 +
            #                                       (delta.days if delta.days <= 30 else 30))
            #             rec.total_service_years = rec.total_service_days / 360
            #             print("1 : ", rec.total_service_days)
            #             if rec.total_service_years < 0:
            #                 rec.total_service_years = 0
            #             if rec.total_service_days >= 1800:
            #                 rec.days_under_5_years = 1800
            #                 if rec.leave_policy == '30':
            #                     true_days_less_than = (1800 * 30) / 360
            #                 else:
            #                     true_days_less_than = (1800 * 21) / 360
            #                 rec.days_over_5_years = rec.total_service_days - 1800
            #                 if rec.days_over_5_years < 0:
            #                     rec.days_over_5_years = 0
            #                 true_days = (rec.days_over_5_years * 30) / 360
            #                 total_days = true_days_less_than + true_days
            #                 total_years = rec.total_service_days / 360
            #                 rec.service_bonus_days = 75 + (total_years - 5) * 30
            #                 if rec.service_bonus_days < 0:
            #                     rec.service_bonus_days = 0
            #
            #                 hr_contract = rec.contract_id
            #                 if hr_contract:
            #                     p_day = hr_contract.total_salary / 30
            #                     rec.amount_of_service_bonus_days = rec.service_bonus_days * p_day
            #                 else:
            #                     rec.amount_of_service_bonus_days = 0
            #             else:
            #                 rec.days_under_5_years = rec.total_service_days
            #
            #                 if rec.days_under_5_years < 0:
            #                     rec.days_under_5_years = 0
            #                 if rec.leave_policy == '30':
            #                     true_days_less_than = (rec.total_service_days * 30) / 360
            #                 else:
            #                     true_days_less_than = (rec.total_service_days * 21) / 360
            #                 rec.days_over_5_years = 0
            #                 # true_days = (rec.days_over_5_years * 30) / 360
            #                 # total_days = true_days_less_than + true_days
            #                 total_years = rec.total_service_days / 360
            #                 rec.service_bonus_days = total_years * 15
            #                 # rec.service_bonus_days = true_days_less_than
            #                 if rec.service_bonus_days < 0:
            #                     rec.service_bonus_days = 0
            #                 hr_contract = rec.contract_id
            #                 if hr_contract:
            #                     p_day = hr_contract.total_salary / 30
            #                     rec.amount_of_service_bonus_days = rec.service_bonus_days * p_day
            #                 else:
            #                     rec.amount_of_service_bonus_days = 0
            #
            #         # if no last_working_date
            #         else:
            #             rec.days_over_5_years = 0
            #             rec.days_under_5_years = 0
            #             rec.total_service_years = 0
            #             rec.service_bonus_days = 0
            #             rec.amount_of_service_bonus_days = 0
            #     # if user have more than one return
            #     else:
            #         d1 = date.today()
            #         if all_return_vacation[-1].return_date:
            #             d2 = all_return_vacation[-1].return_date
            #         else:
            #             d2 = date.today()
            #         delta = relativedelta(d1, d2)
            #         rec.total_service_days = (delta.years * 360 + delta.months * 30 +
            #                                   (delta.days if delta.days <= 30 else 30))
            #         rec.vacation_expiration_date = d1
            #         rec.return_date_after_vacation = d2
            #         # date
            #         # print('delta=return_vacation=', delta)
            #         # print('delta=return_vacation=', delta.days)
            #         if rec.first_contract_date:
            #             d2 = rec.first_contract_date
            #         else:
            #             d2 = date.today()
            #         the_num = d1 - d2
            #         rec.custom_today_date = d1
            #         rec.custom_initial_contract_date = d2
            #         the_num_days = (the_num.years * 360 + the_num.months * 30 +
            #                                   (the_num.days if the_num.days <= 30 else 30))
            #         the_num_of_year = the_num_days / 360
            #         # print('the_num_of_year', the_num_of_year)
            #         if the_num_of_year <= 5:
            #             rec.days_under_5_years = rec.total_service_days
            #             if rec.days_under_5_years < 0:
            #                 rec.days_under_5_years = 0
            #             if rec.leave_policy == '30':
            #                 true_days_less_than = (rec.total_service_days * 30) / 360
            #             else:
            #                 true_days_less_than = (rec.total_service_days * 21) / 360
            #             rec.days_over_5_years = 0
            #             total_years = rec.total_service_days / 360
            #             rec.service_bonus_days = total_years * 15
            #             if rec.service_bonus_days < 0:
            #                 rec.service_bonus_days = 0
            #             hr_contract = rec.contract_id
            #             if hr_contract:
            #                 p_day = hr_contract.total_salary / 30
            #                 rec.amount_of_service_bonus_days = rec.service_bonus_days * p_day
            #             else:
            #                 rec.amount_of_service_bonus_days = 0
            #         else:
            #             rec.days_under_5_years = 1800
            #             if rec.leave_policy == '30':
            #                 true_days_less_than = (1800 * 30) / 360
            #             else:
            #                 true_days_less_than = (1800 * 21) / 360
            #             rec.days_over_5_years = rec.total_service_days - 1800
            #
            #             if rec.days_over_5_years < 0:
            #                 rec.days_over_5_years = 0
            #
            #             true_days = (rec.days_over_5_years * 30) / 360
            #             total_days = true_days_less_than + true_days
            #             total_years = rec.total_service_days / 360
            #             rec.service_bonus_days = total_years * 15
            #             # rec.service_bonus_days = total_days
            #             if rec.service_bonus_days < 0:
            #                 rec.service_bonus_days = 0
            #             hr_contract = rec.contract_id
            #             if hr_contract:
            #                 p_day = hr_contract.total_salary / 30
            #                 rec.amount_of_service_bonus_days = rec.service_bonus_days * p_day
            #             else:
            #                 rec.amount_of_service_bonus_days = 0
            #         # print('the_num_of_year', the_num_of_year.year)
            #
            #         rec.total_service_years = the_num_of_year
            #         print("2 : ", the_num_of_year)
            #         print("2 : ", the_num_days)
            #         print("2 : ", rec.total_service_days)
            #         if rec.total_service_years < 0:
            #             rec.total_service_years = 0
            #         # print('total_service_years', rec.total_service_years)
            # if no return vaction
            # else:
            if rec.first_contract_date:
                get_date_contract = self.env['hr.contract'].search([('employee_id', '=', rec.id),
                                                                    ('state', 'in', ['close', 'open'])], limit=1)
                # ('state', 'in', ['close', 'open'])], limit=1)
                if rec.active == False:
                    if get_date_contract:
                        d1 = get_date_contract[0].date_end
                    else:
                        if rec.departure_date:
                            d1 = rec.departure_date
                        else:
                            d1 = date.today()
                else:
                    if rec.departure_date:
                        d1 = rec.departure_date
                    else:
                        d1 = date.today()
                # print("rec.first_contract_date =", rec.first_contract_date)
                if rec.custom_hire_date and rec.custom_hire_date < rec.first_contract_date:
                    d2 = rec.custom_hire_date
                else:
                    d2 = rec.first_contract_date
                # d2 = rec.first_contract_date
                delta = relativedelta(d1, d2)
                rec.total_service_days = (delta.years * 360 + delta.months * 30 +
                                          (delta.days if delta.days <= 30 else 30)) + 1
                rec.contract_end_date_or_current_date = d1
                rec.initial_contract_date_or_null = d2
                rec.total_service_years = rec.total_service_days / 360
                if rec.total_service_years < 0:
                    rec.total_service_years = 0
                if rec.total_service_days >= 1800:
                    rec.days_under_5_years = 1800
                    if rec.leave_policy == '30':
                        true_days_less_than = (1800 * 30) / 360
                    else:
                        true_days_less_than = (1800 * 21) / 360
                    rec.days_over_5_years = rec.total_service_days - 1800
                    if rec.days_over_5_years < 0:
                        rec.days_over_5_years = 0
                    true_days = (rec.days_over_5_years * 30) / 360
                    total_days = true_days_less_than + true_days
                    total_years = rec.total_service_days / 360
                    rec.service_bonus_days = 75 + (total_years - 5) * 30
                    if rec.service_bonus_days < 0:
                        rec.service_bonus_days = 0
                    hr_contract = rec.contract_id
                    if hr_contract:
                        p_day = hr_contract.total_salary / 30
                        rec.amount_of_service_bonus_days = rec.service_bonus_days * p_day
                    else:
                        rec.amount_of_service_bonus_days = 0
                else:
                    rec.days_under_5_years = rec.total_service_days
                    if rec.days_under_5_years < 0:
                        rec.days_under_5_years = 0
                    if rec.leave_policy == '30':
                        true_days_less_than = (rec.total_service_days * 30) / 360
                    else:
                        true_days_less_than = (rec.total_service_days * 21) / 360
                    rec.days_over_5_years = 0
                    # true_days = (rec.days_over_5_years * 30) / 360
                    # total_days = true_days_less_than + true_days
                    total_years = rec.total_service_days / 360
                    rec.service_bonus_days = total_years * 15
                    # rec.service_bonus_days = true_days_less_than
                    if rec.service_bonus_days < 0:
                        rec.service_bonus_days = 0
                    hr_contract = rec.contract_id
                    if hr_contract:
                        p_day = hr_contract.total_salary / 30
                        rec.amount_of_service_bonus_days = rec.service_bonus_days * p_day
                    else:
                        rec.amount_of_service_bonus_days = 0
            else:
                rec.days_over_5_years = 0
                rec.days_under_5_years = 0
                rec.total_service_years = 0
                rec.service_bonus_days = 0
                rec.last_working_date_before_vacation = False
                rec.contract_start_date_or_today = False
                rec.vacation_expiration_date = False
                rec.return_date_after_vacation = False
                rec.custom_today_date = False
                rec.custom_initial_contract_date = False
                rec.contract_end_date_or_current_date = False
                rec.initial_contract_date_or_null = False
                # continue
            rec._compute_net_days()
            the_contract = self.env['hr.contract'].search([('employee_id', '=', rec.id), ('state', '=', 'open')],
                                                          limit=1)
            # the_contract.compute_total_salary()
            all_valid_time_off = self.env['hr.leave'].search([('employee_id', '=', rec.id),
                                                              ('holiday_status_id.add_to', '=', True),
                                                              ('state', '=', 'validate')])
            new_num = 0
            if all_valid_time_off:
                for t in all_valid_time_off:
                    new_num += t.number_of_days
                rec.leave_days_taken = new_num
            else:
                rec.leave_days_taken = 0.0