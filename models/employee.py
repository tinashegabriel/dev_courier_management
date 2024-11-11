# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields


class Employee(models.Model):
    _inherit = 'hr.employee'

    cm_delivery_boy = fields.Boolean(string='Courier Delivery Boy')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: