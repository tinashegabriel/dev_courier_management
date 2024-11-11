# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##########################################################################

from odoo import fields, models


class WcrCancelReason(models.TransientModel):
    _name = "wcr.cancel.reason"

    def cancel_website_courier_request(self):
        msg = 'Cancel Reason : ' + self.cancel_reason
        vals = {'body': msg,
                'author_id': self.env.user and self.env.user.partner_id and self.env.user.partner_id.id,
                'email_from': self.env.user and self.env.user.partner_id and self.env.user.partner_id.email or '',
                'model': 'cm.website.courier.request',
                'res_id': self.wcr_id.id,
                'message_type': 'comment'}
        self.env['mail.message'].sudo().create(vals)
        self.wcr_id.sudo().write({'state': 'cancel', 'cancel_reason': self.cancel_reason})

    cancel_reason = fields.Text(string='Cancel Reason', required=True)
    wcr_id = fields.Many2one('cm.website.courier.request', string='Website Courier Request')
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: