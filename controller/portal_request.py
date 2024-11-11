# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import werkzeug


class CustomerPortal(CustomerPortal):

     def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        request_courier = request.env['dev.courier.request'].sudo()
        request_count = request_courier.search_count([('sender_id', '=', partner.id)])
        values['request_count'] = request_count
        return values
    
    
#    LISTVIEW OR SORTING
        
     @http.route(['/my/request', '/my/request/page/<int:page>'], type='http', auth="user", website='True')
     def portal_my_loan(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        request_pool = request.env['dev.courier.request'].sudo()

        domain = [('sender_id', '=', partner.id)]
        
        searchbar_sortings = {
            'name': {'label': _('number'), 'order': 'name desc'},
            'date': {'label': _('Date'), 'order': 'registration_date desc'},

        }

        # default sortby order
        if not sortby:
            sortby = 'name'

        sort_request= searchbar_sortings[sortby]['order']


        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        
        request_count = request_pool.search_count(domain)
        
        pager = portal_pager(
            url="/my/request",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=request_count,
            page=page,
            step=self._items_per_page
        )
        
        request_courier = request_pool.search(domain, order=sort_request, limit=self._items_per_page, offset=pager['offset'])
#        request_courier.session['my_request_history'] = request_courier.ids[:100]

        values.update({
            'date': date_begin,
            'requests': request_courier.sudo(),
            'page_name': 'request_courier',
            'pager': pager,
            'default_url': '/my/request',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("dev_courier_management.portal_my_request", values)
        
        
#     FORMVIEW   
    
     @http.route(['/my/request/<int:order_id>'], type='http', auth="public", website=True)
     def portal_request_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            request_sudo = self._document_check_access('dev.courier.request', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=request_sudo, report_type=report_type,
                                     report_ref='dev_courier_management.menu_dev_courier_request_report',
                                     download=download)

        now = fields.Date.today()
       
        if request_sudo and request.session.get('view_request_%s' % request_sudo.id) != now and request.env.user.share and access_token:
            request.session['view_request_%s' % request_sudo.id] = now
            body = _('Request viewed by customer')
        values = {
            'request_courier': request_sudo,
            'message': message,
            'token': access_token,
            'return_url': '/my/request',
            'bootstrap_formatting': True,
            'partner_id': request_sudo.sender_id.id,
            'report_type': 'html',
        }
        if request_sudo.company_id:
            values['res_company'] = request_sudo.company_id
            history = request.session.get('my_request_history', [])
        else:
            history = request.session.get('my_request_history', [])
            
        values.update(get_records_pager(history, request_sudo))
        return request.render('dev_courier_management.request_portal_template', values)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
