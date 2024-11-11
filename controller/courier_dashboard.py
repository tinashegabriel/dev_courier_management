# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Mruthul Raj @cybrosys(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import datetime
from odoo import http
from odoo.http import request
from odoo import models, fields, api, _
from operator import itemgetter
import itertools
import operator
from datetime import date, timedelta


class ProjectFilter(http.Controller):
    """The ProjectFilter class provides the filter option to the js.
    When applying the filter returns the corresponding data."""


    @http.route('/courier/chart/data', auth='public', type='json')
    def get_courier_chart_data(self, **kw):
        
        all_color_list = ['#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
                          '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad']     
    
        today = date.today()

        courier_domain = []
        invoice_domain = [("courier_request_id", '!=', False)]
        data=kw['data']
        delivery_state_range_selection = data['delivery_state_range_selection']
        delivery_country_range_selection=data['delivery_country_range_selection']
        delivery_type_range_selection = data['delivery_type_range_selection']
        
        if not data.get('duration'):
            courier_domain = [('registration_date', '=', today)]
            invoice_domain = []
        
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    courier_domain += [('user_id','=',user_id)]
                    invoice_domain += [('user_id', '=', user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    courier_domain += [('sender_id','=',partner_id)]
                    invoice_domain += [('partner_id','=', partner_id)]
            if data['priority_id']:
                if data['priority_id'] != 'all':
                    priority_id = int(data['priority_id'])
                    courier_domain += [('priority_id.id','=',priority_id)]
                    invoice_domain += [(('partner_id.id','=', priority_id))]
            
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    courier_domain += [('registration_date', '>=', filter_date), ('registration_date', '<=', today)]
                    invoice_domain +=[('invoice_date', '>=', filter_date), ('invoice_date', '<=', today)]

    
    # ----------------   Delivery Status   ------------------- 
        new_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'New')] +courier_domain)
        
        collected_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Collected')] +courier_domain)
        
        dispatched_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Dispatched')] +courier_domain)

        intransit_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'In Transit')] +courier_domain)

        out_of_delivery_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Out Of Delivery')] +courier_domain)
        
        delivered_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Delivered')] +courier_domain)

        cancel_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Cancelled')] +courier_domain)
        
        all_invoice_ids = request.env['account.move'].search([('courier_request_id', '!=', False)] +invoice_domain)
        
        all_stage_chart_labels = ['New', 'Collected','Dispatched','In Transit','Out Of Delivery','Delivered','Cancelled']
        all_stage_chart_value = [len(new_data), len(collected_data), len(dispatched_data), len(intransit_data), 
                                 len(out_of_delivery_data), len(delivered_data), len(cancel_data), 
                                 ]

        all_stage_chart_data = {
            'labels': all_stage_chart_labels,
            'datasets': [{
                'label' : "All Status",
                'backgroundColor': all_color_list[:len(all_stage_chart_labels)],
                'data': all_stage_chart_value
            }]
        }

        # Deivery By State 2-----------------------------

        delivery_order_state_label=[]
        delivery_order_state_values=[]

        delivery_state_data = request.env['dev.courier.request'].search_read(courier_domain, fields=['sender_state_id', 'name'])

        n_lines = sorted(delivery_state_data, key=itemgetter('sender_state_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('sender_state_id'))
        lines = [{'sender_state_id': k, 'values': [x for x in v]} for k, v in groups]
               
        state_counting = 0
        for line in lines:
            delivery_order_state_label.append(line.get('sender_state_id')[1])
            delivery_order_state_values.append(len(line.get('values')))
            state_counting += 1
        
        delivery_state_chart_data = {
            'labels': delivery_order_state_label[:int(delivery_state_range_selection)],
            'datasets': [{
                'label': "Courier State",
                'backgroundColor': all_color_list[:state_counting],
                'data': delivery_order_state_values
            }]
        }


        # Deivery By country 3-----------------------------

        delivery_order_country_label=[]
        delivery_order_country_values=[]

        delivery_country_data = request.env['dev.courier.request'].search_read(courier_domain, fields=['sender_country_id', 'name'])

        n_lines = sorted(delivery_country_data, key=itemgetter('sender_country_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('sender_country_id'))
        lines = [{'sender_country_id': k, 'values': [x for x in v]} for k, v in groups]
               
        country_counting = 0
        for line in lines:
            delivery_order_country_label.append(line.get('sender_country_id')[1])
            delivery_order_country_values.append(len(line.get('values')))
            country_counting += 1
        
        delivery_country_chart_data = {
            'labels': delivery_order_country_label[:int(delivery_country_range_selection)],
            'datasets': [{
                'label': "Courier Country",
                'backgroundColor': all_color_list[:country_counting],
                'data': delivery_order_country_values
            }]
        }

        #    Delivered By Type Chart 4   -------------------

        delivery_order_type_label=[]
        delivery_order_type_values=[]


        delivery_type_data = request.env['dev.courier.request'].search_read(courier_domain, fields=['courier_type_id', 'name'])

        n_lines = sorted(delivery_type_data, key=itemgetter('courier_type_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('courier_type_id'))
        lines = [{'courier_type_id': k, 'values': [x for x in v]} for k, v in groups]
               
        type_counting = 0
        for line in lines:
            delivery_order_type_label.append(line.get('courier_type_id')[1])
            delivery_order_type_values.append(len(line.get('values')))
            type_counting += 1
        
        delivery_type_chart_data = {
            'labels': delivery_order_type_label[:int(delivery_type_range_selection)],
            'datasets': [{
                'label': "Courier Type",
                'backgroundColor': all_color_list[:int(delivery_type_range_selection)],
                'data': delivery_order_type_values[:int(delivery_type_range_selection)]
            }]
        }

        # List View-----------------------

        all_collected_list = request.env['dev.courier.request'].search_read( [('state_id', '=', 'Collected')] +courier_domain,
                                                            fields=['name', 'sender_id', 'sender_mobile','registration_date','delivery_date'],
                                                            order="id desc", limit=10)

        all_transit_list = request.env['dev.courier.request'].search_read( [('state_id', '=', 'In Transit')] + courier_domain,
                                                            fields=['name', 'sender_id', 'sender_mobile','registration_date','delivery_date'],
                                                            order="id desc", limit=10)

        all_delivered_list = request.env['dev.courier.request'].search_read( [('state_id', '=', 'Delivered')] + courier_domain,
                                                            fields=['name', 'sender_id', 'sender_mobile','registration_date','delivery_date'],
                                                            order="id desc", limit=10)

        all_cancel_list = request.env['dev.courier.request'].search_read( [('state_id', '=', 'Cancelled')] + courier_domain,
                                                            fields=['name', 'sender_id', 'sender_mobile','registration_date','delivery_date'],
                                                            order="id desc", limit=10)

        # Return-----------------

        return {
            'all_stage_chart_data': all_stage_chart_data,
            'delivery_state_chart_data': delivery_state_chart_data,
            'delivery_country_chart_data': delivery_country_chart_data,
            'delivery_type_chart_data': delivery_type_chart_data,
            'all_collected_list': all_collected_list,
            'all_transit_list': all_transit_list,
            'all_delivered_list': all_delivered_list,
            'all_cancel_list': all_cancel_list,
        }


        # ---------Seperate method of chart 1------------

    @http.route('/courier/status/chart/data', auth='public', type='json')
    def get_all_stage_chart_data(self, **kw):
        all_color_list = ['#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
                          '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad']

        today = date.today()
        courier_domain = []
        invoice_domain = [("courier_request_id", '!=', False)]
        data = kw['data']

        if not data.get('duration'):
            courier_domain = [('registration_date', '=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    courier_domain += [('user_id','=',user_id)]
                    invoice_domain += [('user_id', '=', user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    courier_domain += [('sender_id','=',partner_id)]
                    invoice_domain += [('partner_id','=', partner_id)]
            if data['priority_id']:
                if data['priority_id'] != 'all':
                    priority_id = int(data['priority_id'])
                    courier_domain += [('priority_id.id','=',priority_id)]
                    invoice_domain += [(('partner_id.id','=', priority_id))]
            
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    courier_domain += [('registration_date', '>=', filter_date), ('registration_date', '<=', today)]
                    invoice_domain +=[('invoice_date', '>=', filter_date), ('invoice_date', '<=', today)]

    
    # ----------------   Delivery Status   ------------------- 
        new_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'New')] +courier_domain)
        
        collected_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Collected')] +courier_domain)
        
        dispatched_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Dispatched')] +courier_domain)

        intransit_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'In Transit')] +courier_domain)

        out_of_delivery_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Out Of Delivery')] +courier_domain)
        
        delivered_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Delivered')] +courier_domain)

        cancel_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Cancelled')] +courier_domain)
        
        all_invoice_ids = request.env['account.move'].search([('courier_request_id', '!=', False)] +invoice_domain)
        
        all_stage_chart_labels = ['New', 'Collected','Dispatched','In Transit','Out Of Delivery','Delivered','Cancelled']
        all_stage_chart_value = [len(new_data), len(collected_data), len(dispatched_data), len(intransit_data), 
                                 len(out_of_delivery_data), len(delivered_data), len(cancel_data), 
                                 ]

        all_order_ids = [new_data.ids, collected_data.ids, dispatched_data.ids, intransit_data.ids, 
                                 out_of_delivery_data.ids, delivered_data.ids, cancel_data.ids]

        all_stage_chart_data = {
            'labels': all_stage_chart_labels,
            'datasets': [{
                'label' : "All Status",
                'backgroundColor': all_color_list[:len(all_stage_chart_labels)],
                'data': all_stage_chart_value,
                'detail': all_order_ids
            }]
        }

        return {
            'all_stage_chart_data': all_stage_chart_data,
        }

        # ---------Seperate method of chart 2------------

    @http.route('/courier/state/chart/data', auth='public', type='json')
    def get_delivery_state_chart_data(self, **kw):
        all_color_list = ['#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
                          '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad']

        today = date.today()
        courier_domain = []
        invoice_domain = [("courier_request_id", '!=', False)]
        data = kw['data']
        delivery_state_range_selection = data['delivery_state_range_selection']
        if not data.get('duration'):
            courier_domain = [('registration_date', '=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    courier_domain += [('user_id','=',user_id)]
                    invoice_domain += [('user_id', '=', user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    courier_domain += [('sender_id','=',partner_id)]
                    invoice_domain += [('partner_id','=', partner_id)]
            if data['priority_id']:
                if data['priority_id'] != 'all':
                    priority_id = int(data['priority_id'])
                    courier_domain += [('priority_id.id','=',priority_id)]
                    invoice_domain += [(('partner_id.id','=', priority_id))]
            
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    courier_domain += [('registration_date', '>=', filter_date), ('registration_date', '<=', today)]
                    invoice_domain +=[('invoice_date', '>=', filter_date), ('invoice_date', '<=', today)]
        
        delivery_order_state_label=[]
        delivery_order_state_values=[]

        delivery_state_data = request.env['dev.courier.request'].search_read(courier_domain, fields=['sender_state_id', 'name'])

        n_lines = sorted(delivery_state_data, key=itemgetter('sender_state_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('sender_state_id'))
        lines = [{'sender_state_id': k, 'values': [x for x in v]} for k, v in groups]
               
        state_counting_ids=[]                                                                                                                       
        for x in lines:
            state_counting_id = []                                                                                                                  
            for id in x['values']:
                state_counting_id.append(id['id']) 
            state_counting_ids.append(state_counting_id) 
        
        for line in lines:
            delivery_order_state_label.append(line.get('sender_state_id')[1])
            delivery_order_state_values.append(len(line.get('values')))
        
        delivery_state_chart_data = {
            'labels': delivery_order_state_label[:int(delivery_state_range_selection)],
            'datasets': [{
                'label': "Courier State",
                'backgroundColor': all_color_list[:int(delivery_state_range_selection)],
                'data': delivery_order_state_values[:int(delivery_state_range_selection)],
                'detail' : state_counting_ids
            }]
        }

        return {
            'delivery_state_chart_data': delivery_state_chart_data,
        }

        # ---------Seperate method of chart 3------------

    @http.route('/courier/country/chart/data', auth='public', type='json')
    def get_delivery_country_chart_data(self, **kw):
        all_color_list = ['#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
                          '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad']

        today = date.today()
        courier_domain = []
        invoice_domain = [("courier_request_id", '!=', False)]
        data = kw['data']
        delivery_country_range_selection=data['delivery_country_range_selection']
        if not data.get('duration'):
            courier_domain = [('registration_date', '=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    courier_domain += [('user_id','=',user_id)]
                    invoice_domain += [('user_id', '=', user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    courier_domain += [('sender_id','=',partner_id)]
                    invoice_domain += [('partner_id','=', partner_id)]
            if data['priority_id']:
                if data['priority_id'] != 'all':
                    priority_id = int(data['priority_id'])
                    courier_domain += [('priority_id.id','=',priority_id)]
                    invoice_domain += [(('partner_id.id','=', priority_id))]
            
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    courier_domain += [('registration_date', '>=', filter_date), ('registration_date', '<=', today)]
                    invoice_domain +=[('invoice_date', '>=', filter_date), ('invoice_date', '<=', today)]
        
        delivery_order_country_label=[]
        delivery_order_country_values=[]

        delivery_country_data = request.env['dev.courier.request'].search_read(courier_domain, fields=['sender_country_id', 'name'])

        n_lines = sorted(delivery_country_data, key=itemgetter('sender_country_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('sender_country_id'))
        lines = [{'sender_country_id': k, 'values': [x for x in v]} for k, v in groups]
               
        country_counting_ids=[]                                                                                                                       
        for x in lines:
            country_counting_id = []                                                                                                                  
            for id in x['values']:
                country_counting_id.append(id['id']) 
            country_counting_ids.append(country_counting_id) 
    
        for line in lines:
            delivery_order_country_label.append(line.get('sender_country_id')[1])
            delivery_order_country_values.append(len(line.get('values')))
        
        delivery_country_chart_data = {
            'labels': delivery_order_country_label[:int(delivery_country_range_selection)],
            'datasets': [{
                'label': "Courier Country",
                'backgroundColor': all_color_list[:int(delivery_country_range_selection)],
                'data': delivery_order_country_values[:int(delivery_country_range_selection)],
                'detail': country_counting_ids 
            }]
        }

        return {
            'delivery_country_chart_data': delivery_country_chart_data,
        }

        # ---------Seperate method of chart 4------------

    @http.route('/courier/type/chart/data', auth='public', type='json')
    def get_delivery_type_chart_data(self, **kw):
        all_color_list = ['#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
                          '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad']

        today = date.today()
        courier_domain = []
        invoice_domain = [("courier_request_id", '!=', False)]
        data = kw['data']
        delivery_type_range_selection = data['delivery_type_range_selection']
        if not data.get('duration'):
            courier_domain = [('registration_date', '=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    courier_domain += [('user_id','=',user_id)]
                    invoice_domain += [('user_id', '=', user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    courier_domain += [('sender_id','=',partner_id)]
                    invoice_domain += [('partner_id','=', partner_id)]
            if data['priority_id']:
                if data['priority_id'] != 'all':
                    priority_id = int(data['priority_id'])
                    courier_domain += [('priority_id.id','=',priority_id)]
                    invoice_domain += [(('partner_id.id','=', priority_id))]
            
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    courier_domain += [('registration_date', '>=', filter_date), ('registration_date', '<=', today)]
                    invoice_domain +=[('invoice_date', '>=', filter_date), ('invoice_date', '<=', today)]
        
        delivery_order_type_label=[]
        delivery_order_type_values=[]

        delivery_type_data = request.env['dev.courier.request'].search_read(courier_domain, fields=['courier_type_id', 'name'])

        n_lines = sorted(delivery_type_data, key=itemgetter('courier_type_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('courier_type_id'))
        lines = [{'courier_type_id': k, 'values': [x for x in v]} for k, v in groups]
        
        type_counting_ids=[]                                                                                                                       
        for x in lines:
            type_counting_id = []                                                                                                                  
            for id in x['values']:
                type_counting_id.append(id['id']) 
            type_counting_ids.append(type_counting_id) 

        for line in lines:
            delivery_order_type_label.append(line.get('courier_type_id')[1])
            delivery_order_type_values.append(len(line.get('values')))
        
        delivery_type_chart_data = {
            'labels': delivery_order_type_label[:int(delivery_type_range_selection)],
            'datasets': [{
                'label': "Courier Type",
                'backgroundColor': all_color_list[:int(delivery_type_range_selection)],
                'data': delivery_order_type_values[:int(delivery_type_range_selection)],
                'detail': type_counting_ids
            }]
        }

        return {
            'delivery_type_chart_data': delivery_type_chart_data,
        }
    
    
    @http.route('/all_courier_filter', auth='public', type='json')
    def all_courier_filter(self):
#    	print("courier===========================")
        user_list = []
        partner_list = []
        priority_list = []
       
        user_ids = request.env['res.users'].search([])
        partner_ids = request.env['res.partner'].search([('courier', '=', True)])
       
        priority_ids = request.env['dev.courier.priority'].search([])
       

        for user_id in user_ids:
            dic = {'name': user_id.name,
                   'id': user_id.id}
            user_list.append(dic)
        for partner_id in partner_ids:
            dic = {'name': partner_id.name,
                   'id': partner_id.id}
            partner_list.append(dic)
        
        for priority_id in priority_ids:
            dic = {'name': priority_id.name,
                   'id': priority_id.id}
            priority_list.append(dic)
            
        return [user_list, partner_list, priority_list]
    
    @http.route('/get/courier/tiles/data', auth='public', type='json')
    def get_tiles_data(self, **kwargs):
        
        today = date.today()
        courier_domain = []
        invoice_domain = []
        
        if not kwargs.get('duration'):
            courier_domain = [('registration_date', '=', today)]
            invoice_domain = [("courier_request_id", "!=", False),('invoice_date', '=', today)]

        if kwargs:
            if kwargs['user_id']:
                if kwargs['user_id'] != 'all':
                    user_id = int(kwargs['user_id'])
                    courier_domain += [('user_id','=',user_id)]
                    invoice_domain += [('user_id', '=', user_id)]

            if kwargs['partner_id']:
                if kwargs['partner_id'] != 'all':
                    partner_id = int(kwargs['partner_id'])
                    courier_domain += [('sender_id','=',partner_id)]
                    invoice_domain += [('partner_id','=', partner_id)]
            
            if kwargs['priority_id']:
                if kwargs['priority_id'] != 'all':
                    priority_id = int(kwargs['priority_id'])
                    courier_domain += [('priority_id.id','=',priority_id)]
                    invoice_domain += [(('partner_id.id','=', priority_id))]

            if kwargs['duration']:
                duration = kwargs['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    courier_domain += [('registration_date', '>=', filter_date), ('registration_date', '<=', today)]
                    invoice_domain +=[('invoice_date', '>=', filter_date), ('invoice_date', '<=', today)]
            
        
        # ----------Counters------------
        
        new_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'New')] + courier_domain)
        
        collected_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Collected')] + courier_domain)
        
        dispatched_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Dispatched')] + courier_domain)

        intransit_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'In Transit')] + courier_domain)

        out_of_delivery_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Out Of Delivery')] + courier_domain)
        
        delivered_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Delivered')] + courier_domain)
        
        cancel_data = request.env['dev.courier.request'].search([
            ('state_id', '=', 'Cancelled')] + courier_domain)
        
        all_invoice_ids = request.env['account.move'].search([
            ('courier_request_id', '!=', False)] + invoice_domain)
        
        user_name = request.env.user.name
        user_img = request.env.user.image_1920

        return {
            'new_data': new_data.ids,
            'collected_data':collected_data.ids,
            'dispatched_data':dispatched_data.ids,
            'intransit_data':intransit_data.ids,
            'out_of_delivery_data':out_of_delivery_data.ids,
            'delivered_data':delivered_data.ids,
            'cancel_data':cancel_data.ids,
            'all_invoice_ids':all_invoice_ids.ids,
            'user_img': user_img,
            'user_name': user_name
        }

    @http.route('/courier/filter-apply', auth='public', type='json')
    def courier_filter_apply(self, **kw):
        data = kw['data']
        
        user_id = data['user']
        partner_id = data['partner']
        priority_id = data['priority']
        duration = data['duration']

        result = self.get_tiles_data(user_id=user_id, partner_id=partner_id, priority_id=priority_id, duration=duration)
        return result
