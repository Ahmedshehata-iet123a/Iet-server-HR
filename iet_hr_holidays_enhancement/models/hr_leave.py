# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta, date, datetime
from odoo.exceptions import AccessError, UserError, ValidationError


class HRLeaveInherit(models.Model):
    _inherit = 'hr.leave'

    return_date = fields.Date(string="Return Date")
    date_now = fields.Date(string="Date", default=fields.Date.today())
    amount = fields.Float(string='Amount', )
    last_working_date = fields.Date(string='Last Working Date', )
    return_vacation_ids = fields.Many2many('return.vacation', )
    time_off_types = fields.Selection([
        ('annual_vacation', 'Annual Vacation'),
        ('paid_time_off', 'Paid time off'),
        ('sick_time_off', 'Sick time off'),
        ('compensatory_days', 'Compensatory Days'),
        ('unpaid', 'Unpaid'),
    ], string='Time Off Types', )
    vacation_bool = fields.Boolean(default=False)

    net_days = fields.Float(string='Net Days', related='employee_id.net_days')
    identification_id_custom = fields.Char(string='Identification No', related='employee_id.identification_id')
    custom_pin = fields.Char(string="Employee Number", related='employee_id.barcode')
    custom_to = fields.Char(string="To", readonly=False)
    from_custom = fields.Char(string="From", readonly=False)
    related_leave_id = fields.Many2one(comodel_name="hr.leave", string="Related Leave", required=False, )
    employee_number = fields.Char(related='employee_id.employee_number', )

    def action_validate(self, check_state=True):
        self.action_check_vacation()
        super(HRLeaveInherit, self).action_validate(check_state=check_state)

    @api.model
    def create(self, vals):
        print("CREATE")
        employee_id = vals.get('employee_id')
        leave_type = vals.get('holiday_status_id')
        start_date = vals.get('request_date_from')
        end_date = vals.get('request_date_to')
        # Check if the leave type and dates are provided
        if leave_type and start_date and end_date and employee_id:
            # Search for existing leaves of the same type and duration
            existing_leaves = self.search([
                ('employee_id', '=', employee_id),
                ('holiday_status_id', '=', leave_type),
                ('request_date_from', '<=', end_date),
                ('request_date_to', '>=', start_date),
            ], limit=1)
            # Check if there are already two or more leaves
            if existing_leaves:
                raise ValidationError(
                    _("There is already a ") + str(existing_leaves.holiday_status_id.name) + _(" for ") + str(
                        existing_leaves.employee_id.name) + _(" during the same period."))
        res = super(HRLeaveInherit, self).create(vals)
        if res.holiday_status_id.add_to:
            res.employee_id.compute_custom_accrual_leave()
            allowance_rate = 21 / 360 if res.employee_id.leave_policy == '21' else 30 / 360
            # allowance_days calculate the employee accrual net days + 3 months
            allowance_days = res.employee_id.net_days + allowance_rate * 90
            if res.number_of_days > allowance_days:
                raise ValidationError(
                    _(f"The leave cannot be created for this employee, as they only have a leave balance of {int(allowance_days)} days."))
        return res

    def write(self, vals):
        for record in self:
            employee_id = vals.get('employee_id', record.employee_id.id)
            leave_type = vals.get('holiday_status_id', record.holiday_status_id.id)
            start_date = vals.get('request_date_from', record.request_date_from)
            end_date = vals.get('request_date_to', record.request_date_to)

            # Check if the record type and dates are provided
            if leave_type and start_date and end_date and employee_id:
                # Search for existing records of the same type and overlapping duration
                existing_leaves = self.search([
                    ('id', '!=', record.id),  # Exclude the current leave record
                    ('employee_id', '=', employee_id),
                    ('holiday_status_id', '=', leave_type),
                    ('request_date_from', '<=', end_date),
                    ('request_date_to', '>=', start_date),
                ], limit=1)
                # Check if there are overlapping leaves
                if existing_leaves:
                    raise ValidationError(
                        _("There is already a ") + str(existing_leaves.holiday_status_id.name) +
                        _(" for ") + str(existing_leaves.employee_id.name) +
                        _(" during the same period.")
                    )
            # Check if `request_date_from`, `request_date_to`, `holiday_status_id`, or `employee_id` has changed
            if 'request_date_from' in vals or 'request_date_to' in vals or 'holiday_status_id' in vals or 'employee_id' in vals:
                # Get the updated dates, ensuring they are in datetime format
                request_date_from = vals.get('request_date_from', record.request_date_from)
                request_date_to = vals.get('request_date_to', record.request_date_to)
                # Convert string to datetime if necessary
                if isinstance(request_date_from, str):
                    request_date_from = datetime.strptime(request_date_from, "%Y-%m-%d")
                if isinstance(request_date_to, str):
                    request_date_to = datetime.strptime(request_date_to, "%Y-%m-%d")
                # Ensure dates are available for calculation
                if request_date_from and request_date_to:
                    number_of_days = (request_date_to - request_date_from).days + 1
                else:
                    number_of_days = 0  # Handle case where dates are not provided
                # Get employee and holiday status
                employee_id = self.env['hr.employee'].browse(vals.get('employee_id', record.employee_id.id))
                holiday_status_id = self.env['hr.leave.type'].browse(vals.get('holiday_status_id', record.holiday_status_id.id))

                # Check if the leave type adds to the balance
                if holiday_status_id.add_to:
                    employee_id.compute_custom_accrual_leave()
                    # Print or log the computed number of days
                    print(number_of_days)
                    # Validate if the number of days exceeds the employee's leave balance
                    allowance_rate = 21 / 360 if employee_id.leave_policy == '21' else 30 / 360
                    # allowance_days calculate the employee accrual net days + 3 months
                    allowance_days = employee_id.net_days + allowance_rate * 90
                    if number_of_days > allowance_days:
                        raise ValidationError(
                            _(f"The leave cannot be updated for this employee, as they only have a leave balance of {int(allowance_days)} days.")
                        )
        # Call super to perform the actual write operation
        return super(HRLeaveInherit, self).write(vals)

    def _get_leaves_on_public_holiday(self):
        print('_get_leaves_on_public_holiday')
        # var = self.filtered(lambda l: l.employee_id and not l.number_of_days)
        # print('_get_leaves_on_public_holiday==', var)
        return self.filtered(lambda l: l.employee_id and not l.number_of_days)

    def action_create_unpaid(self):
        for rec in self:
            if rec.number_of_days > rec.net_days and rec.holiday_status_id.create_unpaid == True:
                new_days = rec.number_of_days - rec.net_days
                # print('new days==', new_days)
                rec.number_of_days = rec.net_days
                unpaid_id = self.env['hr.leave.type'].sudo().search([('name', '=', 'Unpaid')])
                # print('000', unpaid_id)
                # print('000', rec.employee_ids, rec.employee_ids.ids, rec.employee_ids.id)
                if unpaid_id:
                    rfq_obj = self.env['hr.leave'].sudo().create({
                        'employee_id': rec.employee_ids.id,
                        'holiday_status_id': unpaid_id.id,
                        'number_of_days': new_days,
                        'time_off_types': 'unpaid',
                        'return_date': rec.return_date,
                        'last_working_date': rec.last_working_date,
                        'related_leave_id': rec.id,
                        'state': 'draft',
                    })
                    # print('rfq_obj====', rfq_obj)
                    if rfq_obj:
                        rec.related_leave_id = rfq_obj.id
                        rfq_obj.action_confirm()
                        rfq_obj.action_approve()
                        # rfq_obj.write({'employee_ids': [(6, 0, rec.employee_ids.ids)]})
                        # print('rfq_obj==', rfq_obj)
            else:
                print('Done')

    def _get_duration(self, check_leave_type=True, resource_calendar=None):
        """
        This method calculates the duration of time off, including all days between
        the start and end date of the request, without excluding holidays.
        """
        self.ensure_one()
        resource_calendar = resource_calendar or self.resource_calendar_id

        if not self.date_from or not self.date_to:
            return (0, 0)

        # Calculate the total duration in days and hours
        total_days = (self.date_to - self.date_from).days + 1  # Include the end date
        total_hours = total_days * 24  # Assuming a full day is 24 hours

        # If the leave type is in days, return days and hours directly
        if self.leave_type_request_unit == 'day' and check_leave_type:
            days = total_days
            hours = total_hours
        else:
            # If the leave type is in hours, we might want to adjust accordingly
            days = total_days
            hours = total_hours

        return (days, hours)

    def action_approve(self):
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env.user.employee_id
        self.filtered(lambda hol: hol.validation_type == 'both').write(
            {'state': 'validate1', 'first_approver_id': current_employee.id})

        # Post a second message, more verbose than the tracking message
        for holiday in self.filtered(lambda holiday: holiday.employee_id.user_id):
            holiday.message_post(
                body=_(
                    'Your %(leave_type)s planned on %(date)s has been accepted',
                    leave_type=holiday.holiday_status_id.display_name,
                    date=holiday.date_from
                ),
                partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        if not self.env.context.get('leave_fast_create'):
            self.activity_update()

        self.action_create_unpaid()
        print("action_approve")
        print("action_create_unpaid")
        print("action_create_unpaid done")
        for rec in self:
            if rec.holiday_status_id.add_to == True:
                if len(rec.employee_id) == 1:
                    rec.employee_id.leave_days_taken = rec.employee_id.leave_days_taken + rec.number_of_days
                    # rec.employee_id.last_time_off_last_days = rec.employee_id.time_off_custom_days
                    # rec.employee_id.time_off_custom_days = rec.number_of_days
                    # print('rec.employee_id.leave_days_taken====', rec.employee_id.leave_days_taken)
                # if len(rec.employee_ids) == 1:
                #     rec.employee_ids.leave_days_taken = rec.employee_ids.leave_days_taken + rec.number_of_days
        return True

    @api.constrains('date_from', 'date_to', 'employee_id')
    def _check_date(self):
        if self.env.context.get('leave_skip_date_check', False):
            return
        for holiday in self.filtered('employee_id'):
            if holiday.date_to and holiday.date_from:
                domain = [
                    ('date_from', '<', holiday.date_to),
                    ('date_to', '>', holiday.date_from),
                    ('employee_id', '=', holiday.employee_id.id),
                    ('id', '!=', holiday.id),
                    ('state', 'not in', ['cancel', 'refuse']),
                ]
                nholidays = self.search_count(domain)
                if nholidays:
                    print('hi')
                    # raise ValidationError(
                    #     _('You can not set 2 time off that overlaps on the same day for the same employee.') + '\n- %s' % (holiday.display_name))

    def action_vacation(self):
        for rec in self:
            for emp in rec.employee_ids:
                vals = {
                    'employee_id': emp.id,
                    'leave_id': rec.id,
                    'return_date': rec.return_date,
                    'state': 'draft',
                    'time_off_types': rec.time_off_types,
                }
                return_vacation = rec.env['return.vacation'].create(vals)
                rec.return_vacation_ids = [(4, return_vacation.id)]
                rec.vacation_bool = True
                rec.is_on_vacation = True

    def action_check_vacation(self):
        for leave in self:
            if leave.holiday_status_id.name.lower() == 'annual leave':
                return_vacation_data = {
                    'employee_id': leave.employee_id.id,
                    'leave_id': leave.id,
                    'return_date': leave.request_date_to,
                    'time_off_type_id': leave.holiday_status_id.id,
                }
                return_vacation = leave.env['return.vacation'].create(return_vacation_data)
                leave.return_vacation_ids = [(4, return_vacation.id)]
                leave.vacation_bool = True

    return_vacation_count = fields.Integer(compute='open_return_vacation_count', store=True)

    def open_return_vacation(self):
        return {
            'name': _('Return From Vacation'),
            'domain': [('id', 'in', self.return_vacation_ids.ids)],
            'view_type': 'form',
            'res_model': 'return.vacation',
            'view_id': False,
            'view_mode': 'list,form',
            'type': 'ir.actions.act_window',
        }

    @api.depends('return_vacation_ids')
    def open_return_vacation_count(self):
        for rec in self:
            count = rec.env['return.vacation'].search_count([('id', 'in', rec.return_vacation_ids.ids)])
            rec.return_vacation_count = count
        # if rec.return_vacation_ids:
        #     count = 1
        # else:
        #     count = 0
        # rec.return_vacation_count = count

    # @api.depends('request_date_from', 'request_date_to')
    # def _compute_number_of_days_display(self):
    #     for holiday in self:
    #         if holiday.request_date_from and holiday.request_date_to:
    #
    #             resource_leave = self.env['resource.calendar.leaves'].search([
    #                 ('date_from', '<=', datetime.combine(holiday.request_date_to, datetime.min.time())),
    #                 ('date_to', '>=', datetime.combine(holiday.request_date_from, datetime.min.time())),
    #                 ('resource_id', '=', False),
    #             ])
    #             adding_days = 0
    #             if resource_leave:
    #                 for leave in resource_leave:
    #                     print(leave)
    #                     if leave.date_from >= datetime.combine(holiday.request_date_from,
    #                                                            datetime.min.time()) and leave.date_to <= datetime.combine(
    #                         holiday.request_date_to, datetime.min.time()):
    #                         adding_days += 1
    #                         adding_days -= (leave.date_to.date() - leave.date_from.date()).days
    #
    #                     elif leave.date_from <= datetime.combine(holiday.request_date_from,
    #                                                              datetime.min.time()) and leave.date_to >= datetime.combine(
    #                         holiday.request_date_to, datetime.min.time()):
    #                         adding_days += 1
    #                         adding_days -= (holiday.request_date_to - holiday.request_date_from).days
    #                     elif leave.date_from <= datetime.combine(holiday.request_date_from,
    #                                                              datetime.min.time()) and leave.date_to <= datetime.combine(
    #                         holiday.request_date_to, datetime.min.time()):
    #                         adding_days += 1
    #                         adding_days -= (leave.date_to.date() - holiday.request_date_from).days
    #                     elif leave.date_from > datetime.combine(holiday.request_date_from,
    #                                                             datetime.min.time()) and leave.date_to >= datetime.combine(
    #                         holiday.request_date_to, datetime.min.time()):
    #                         adding_days += 1
    #                         adding_days -= (holiday.request_date_to - leave.date_from.date()).days
    #             else:
    #                 adding_days += 1
    #                 print(adding_days)
    #
    #             holiday.number_of_days_display = (
    #                                                      holiday.request_date_to - holiday.request_date_from).days + adding_days
    #         else:
    #             holiday.number_of_days_display = 0.0


class HrLeaveTypeInherit(models.Model):
    _inherit = 'hr.leave.type'

    add_to = fields.Boolean(string="Add To Days Taken")
    create_unpaid = fields.Boolean(string="Create Unpaid")
