# ame-*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from datetime import timedelta, date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WebsiteCourierRequest(models.Model):
    _name = 'cm.website.courier.request'
    _inherit = ['mail.thread']
    _description = 'Website Courier Request'
    _order = 'id desc'

    def create_courier_request(self):
        warning_message = '''Please enter detail in below : \n'''
        give_warning = False
        if not self.sender_mobile:
            warning_message += '- Sender Mobile \n'
            give_warning = True
        if not self.sender_email:
            warning_message += '- Sender Email \n'
            give_warning = True
        if not self.sender_name:
            warning_message += '- Sender Name \n'
            give_warning = True
        if not self.sender_street:
            warning_message += '- Sender Street \n'
            give_warning = True
        if not self.sender_street2:
            warning_message += '- Sender Street2 \n'
            give_warning = True
        if not self.sender_city:
            warning_message += '- Sender City \n'
            give_warning = True
        if not self.sender_state_id:
            warning_message += '- Sender State \n'
            give_warning = True
        if not self.sender_zip:
            warning_message += '- Sender Zip \n'
            give_warning = True
        if not self.sender_country_id:
            warning_message += '- Sender Country \n'
            give_warning = True
        if not self.receiver_mobile:
            warning_message += '- Receiver Mobile \n'
            give_warning = True
        if not self.receiver_email:
            warning_message += '- Receiver Email \n'
            give_warning = True
        if not self.receiver_name:
            warning_message += '- Receiver Name \n'
            give_warning = True
        if not self.receiver_street:
            warning_message += '- Receiver Street \n'
            give_warning = True
        if not self.receiver_street2:
            warning_message += '- Receiver Street2 \n'
            give_warning = True
        if not self.receiver_city:
            warning_message += '- Receiver City \n'
            give_warning = True
        if not self.receiver_state_id:
            warning_message += '- Receiver State \n'
            give_warning = True
        if not self.receiver_zip:
            warning_message += '- Receiver Zip \n'
            give_warning = True
        if not self.receiver_country_id:
            warning_message += '- Receiver Country \n'
            give_warning = True
        if give_warning:
            raise ValidationError(_(warning_message))

        sender_partner_id = self.env['res.partner'].search(['|', ('mobile', '=', self.sender_mobile),
                                                            ('phone', '=', self.sender_mobile), ('courier', '=', True)],
                                                           limit=1)
        if not sender_partner_id:
            sender_partner_id = self.env['res.partner'].create(
                {'name': self.sender_name, 'mobile': self.sender_mobile, 'email': self.sender_email, 'courier': True})

        receiver_partner_id = self.env['res.partner'].search(
            ['|', ('mobile', '=', self.receiver_mobile), ('phone', '=', self.receiver_mobile), ('courier', '=', True)],
            limit=1)
        if not receiver_partner_id:
            receiver_partner_id = self.env['res.partner'].create(
                {'name': self.receiver_name, 'mobile': self.receiver_mobile, 'email': self.receiver_mobile,
                 'courier': True})
        vals = {'sender_id': sender_partner_id.id,
                'receiver_id': receiver_partner_id.id,
                'sender_email': self.sender_email,
                'sender_mobile': self.sender_mobile,
                'sender_name': self.sender_name,
                'sender_street': self.sender_street,
                'sender_street2': self.sender_street2,
                'sender_city': self.sender_city,
                'sender_zip': self.sender_zip,
                'receiver_mobile': self.receiver_mobile,
                'receiver_email': self.receiver_email,
                'receiver_name': self.receiver_name,
                'receiver_street': self.receiver_street,
                'receiver_street2': self.receiver_street2,
                'receiver_city': self.receiver_city,
                'receiver_zip': self.receiver_zip,
                'sender_state_id': self.sender_state_id and self.sender_state_id.id or False,
                'sender_country_id': self.sender_country_id and self.sender_country_id.id or False,
                'receiver_state_id': self.receiver_state_id and self.receiver_state_id.id or False,
                'receiver_country_id': self.receiver_country_id and self.receiver_country_id.id or False,
                'wcr_id': self.id
                }
        self.env['dev.courier.request'].create(vals)

    def view_courier_requests(self):
        action = self.env.ref('dev_courier_management.action_dev_courier_request').sudo().read()[0]
        if len(self.courier_request_ids) > 1:
            action['domain'] = [('id', 'in', self.courier_request_ids.ids)]
        elif len(self.courier_request_ids.ids) == 1:
            action['views'] = [(self.env.ref('dev_courier_management.view_dev_courier_request_form').id, 'form')]
            action['res_id'] = self.courier_request_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def done_request(self):
        self.state = 'done'

    def auto_cancel(self):
        expiry_days = self.env.company.cm_website_expiry_days or 0
        cancel_reason = self.env.company.cm_website_expiry_reason or 'Auto cancelled by the system based on expiry date'
        if expiry_days > 0:
            wcr_ids = self.env['cm.website.courier.request'].search(
                [('deadline_date', '!=', False), ('state', '=', 'draft')])
            if wcr_ids:
                for wcr_id in wcr_ids:
                    expiry_date = wcr_id.deadline_date + timedelta(days=expiry_days)
                    print(expiry_date)
                    if expiry_date == date.today():
                        msg = 'Cancel Reason : ' + cancel_reason
                        vals = {'body': msg,
                                'author_id': self.env.user and self.env.user.partner_id and self.env.user.partner_id.id,
                                'email_from': self.env.user and self.env.user.partner_id and self.env.user.partner_id.email or '',
                                'model': 'cm.website.courier.request',
                                'res_id': wcr_id.id,
                                'message_type': 'comment'}
                        self.env['mail.message'].sudo().create(vals)
                        wcr_id.sudo().write({'state': 'cancel', 'cancel_reason': cancel_reason})

    def cancel_request(self):
        action = self.env.ref('dev_courier_management.action_wcr_cancel_reason').read()[0]
        return action

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('cm.website.courier.request') or 'New'
        return super(WebsiteCourierRequest, self).create(vals)

    def _compute_cr_count(self):
        for rec_id in self:
            counter = len(rec_id.courier_request_ids)
            rec_id.cr_count = counter

    name = fields.Char('Number', default='New', copy=False, tracking=1)
    sender_name = fields.Char('Sender Name', tracking=1)
    sender_email = fields.Char('Sender Email', tracking=1)
    sender_mobile = fields.Char('Sender Mobile', tracking=1)
    sender_street = fields.Char('Sender Street', tracking=1)
    sender_street2 = fields.Char('Sender Street2', tracking=1)
    sender_city = fields.Char('Sender City', tracking=1)
    sender_zip = fields.Char('Sender Zip', tracking=1)
    receiver_name = fields.Char('Receiver Name', tracking=1)
    receiver_mobile = fields.Char('Receiver Mobile', tracking=1)
    receiver_email = fields.Char('Receiver Email', tracking=1)
    receiver_street = fields.Char('Receiver Street', tracking=1)
    receiver_street2 = fields.Char('Receiver Street2', tracking=1)
    receiver_city = fields.Char('Receiver City', tracking=1)
    receiver_zip = fields.Char('Receiver Zip', tracking=1)
    sender_state_id = fields.Many2one('res.country.state', string='Sender State', tracking=1)
    sender_country_id = fields.Many2one('res.country', string='Sender Country', tracking=1)
    receiver_state_id = fields.Many2one('res.country.state', string='Receiver State', tracking=1)
    receiver_country_id = fields.Many2one('res.country', string='Receiver Country', tracking=1)
    deadline_date = fields.Date(string='Expiry Date', copy=False, tracking=1)
    cancel_reason = fields.Text(string='Cancel Reason', copy=False)
    state = fields.Selection(selection=[('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], default='draft',
                             string='Status')
    courier_request_ids = fields.One2many('dev.courier.request', 'wcr_id', string='Courier Requests')
    cr_count = fields.Integer(string='Courier Request Count', compute='_compute_cr_count')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
