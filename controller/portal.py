# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http
from odoo.http import request


class CustomerPortal(CustomerPortal):

    @http.route(['/courier/tracking'], type='http', auth="public", website=True)
    def courier_tracking(self, **post):
        return request.render("dev_courier_management.courier_tracking_page")

    @http.route(['/dev_courier_track'], type='json', methods=['POST'], website=True, auth="public")
    def dev_track_courier_order(self, do_no, **kw):
        courier_id = request.env['dev.courier.request'].sudo().search([('name', '=', do_no)], limit=1)
        status = False
        if courier_id:
            status = courier_id.state_id.name
            name = courier_id.name or ''
            sender_name = courier_id.sender_name
            receiver_name = courier_id.receiver_name
            delivery_date = courier_id.delivery_date
            if delivery_date:
                delivery_date = delivery_date.strftime("%d-%m-%Y")
            res = {
                'status': status or '',
                'name': name or '',
                'sender_name': sender_name or '',
                'receiver_name': receiver_name or '',
                'delivery_date': delivery_date,
            }
            return res
        else:
            return False


    @http.route(['/web_make_new_courier_request'], type='http', auth="public", website=True)
    def courier_submit_page_redirect(self, **post):
        default_values = {}
        state_ids = request.env['res.country.state'].sudo().search([])
        country_ids = request.env['res.country'].sudo().search([])
        if state_ids:
            default_values['state_ids'] = state_ids
        if country_ids:
            default_values['country_ids'] = country_ids
        return request.render("dev_courier_management.web_courier_request_template", default_values)


    @http.route(['/guest_user_courier_submit'], type='json', methods=['POST'], website=True, auth="public")
    def process_guest_user_courier_submit(self, input_data, **kw):
        vals = {'sender_name': input_data.get('sender_name') or '',
                'sender_mobile': input_data.get('sender_mobile') or '',
                'sender_email': input_data.get('sender_email') or '',
                'sender_street': input_data.get('sender_street') or '',
                'sender_street2': input_data.get('sender_street2') or '',
                'sender_city': input_data.get('sender_city') or '',
                'sender_state_id': input_data.get('sender_state_id') and int(input_data.get('sender_state_id')) or False,
                'sender_zip': input_data.get('sender_zip') or '',
                'sender_country_id': input_data.get('sender_country_id') and int(input_data.get('sender_country_id')) or '',
                'receiver_name': input_data.get('receiver_name') or '',
                'receiver_mobile': input_data.get('receiver_mobile') or '',
                'receiver_email': input_data.get('receiver_email') or '',
                'receiver_street': input_data.get('receiver_street') or '',
                'receiver_street2': input_data.get('receiver_street2') or '',
                'receiver_city': input_data.get('receiver_city') or '',
                'receiver_state_id': input_data.get('receiver_state_id') and int(input_data.get('receiver_state_id')) or False,
                'receiver_zip': input_data.get('receiver_zip') or '',
                'receiver_country_id': input_data.get('receiver_country_id') and int(input_data.get('receiver_country_id')) or False,
                }
        create_request = True
        for key, value in vals.items():
            if value == '' or value is False:
                create_request = False
        if create_request:
            web_courier_request_id = request.env['cm.website.courier.request'].sudo().create(vals)
            return web_courier_request_id.name
        else:
            return False

    @http.route(['/guest_thanks_page_web_courier'], type='json', methods=['POST'], website=True, auth="public")
    def thanks_page_web_courier(self, input_data, **kw):
        return request.render("dev_courier_management.web_courier_request_thanks_page",
                              {'courier_tracking_number': input_data})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
