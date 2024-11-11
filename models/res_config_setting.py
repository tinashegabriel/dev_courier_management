# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models


class res_company(models.Model):
    _inherit = 'res.company'

    cur_delete_state_ids = fields.Many2many('dev.courier.stages', string='Courier Delete On')
    courier_product_id = fields.Many2one('product.product', string='Courier Product')
    distance_product_id = fields.Many2one('product.product', string='Distance Product')
    additional_charge_pro_id = fields.Many2one('product.product', string='Additional Charge Product')
    cm_project_id = fields.Many2one('project.project', string='Project')
    cm_website_expiry_days = fields.Integer( string='Expiry Days')
    cm_website_expiry_reason = fields.Text(string='Cancel Reason')


class res_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    cur_delete_state_ids = fields.Many2many('dev.courier.stages',
                                            related='company_id.cur_delete_state_ids',
                                            readonly=False,
                                            string='Courier Delete On')
    courier_product_id = fields.Many2one('product.product',
                                         related='company_id.courier_product_id',
                                         readonly=False,
                                         string='Courier Product')
    distance_product_id = fields.Many2one('product.product',
                                          related='company_id.distance_product_id',
                                          readonly=False,
                                          string='Distance Product')
    additional_charge_pro_id = fields.Many2one('product.product',
                                               related='company_id.additional_charge_pro_id',
                                               readonly=False,
                                               string='Additional Product')
    cm_project_id = fields.Many2one('project.project', string='Project', related='company_id.cm_project_id',
                                    readonly=False)
    cm_website_expiry_days = fields.Integer(related='company_id.cm_website_expiry_days', string='Expiry Days', readonly=False)
    cm_website_expiry_reason = fields.Text(string='Cancel Reason', related='company_id.cm_website_expiry_reason', readonly=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
