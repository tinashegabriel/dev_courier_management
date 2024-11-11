# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

import base64
import math
from datetime import datetime
from random import randint
import barcode
from barcode.writer import ImageWriter
from odoo import fields, models, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError


class courier_request(models.Model):
    _name = 'dev.courier.request'
    _description = 'Courier Request'
    _inherit = ['mail.thread.cc', 'portal.mixin', 'mail.activity.mixin', 'rating.mixin']
    _order = "id desc"
    _fold_name = 'fold'

    #    FEEDBACK[RATING]
    feedback_rate = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], default='0',
                                     string='Rate', compute='_get_rating_value', readonly=True)
    feedback_date = fields.Date('Feedback Date', compute='_get_rating_value', readonly=True)
    review = fields.Text('Review', compute='_get_rating_value', readonly=True)
    rating_image = fields.Binary('Image', compute='_get_rating_value', readonly=True)
    rating_text = fields.Selection([
        ('top', 'Satisfied'),
        ('ok', 'Okay'),
        ('ko', 'Dissatisfied'),
        ('none', 'No Rating yet')], string='Rating', readonly=True)

    def _get_rating_value(self):
        for request in self:
            request.write({
                'feedback_rate': False,
                'feedback_date': False,
                'rating_image': False,
                'review': '',
                'rating_text': False
            })
            rating_id = self.env['rating.rating'].search([('res_id', '=', self.id),
                                                          ('res_model', '=', 'dev.courier.request')], order='id desc',
                                                         limit=1)
            if rating_id:
                rating = int(rating_id.rating)
                if rating > 4:
                    rating = 4
                request.write({
                    'feedback_rate': str(rating),
                    'feedback_date': rating_id.write_date,
                    'rating_image': rating_id.rating_image,
                    'review': rating_id.feedback,
                    'rating_text': rating_id.rating_text
                })

    def rating_apply(self, rate, token=None, rating=None, feedback=None,
                     subtype_xmlid=None, notify_delay_send=False):
        return super(courier_request, self).rating_apply(rate, token=token, rating=rating, feedback=feedback,
                                                         subtype_xmlid="dev_courier_management.mt_courier_rating")

    def _rating_get_parent_field_name(self):
        return 'sender_id'

    def _rating_get_partner(self):
        res = super(courier_request, self)._rating_get_partner()
        if not res and self.sender_id:
            return self.sender_id
        return res

    def _send_courier_rating_mail(self, force_send=False):
        for request in self:
            rating_template = request.state_id.rating_template_id
            if rating_template:
                request.rating_send_request(rating_template, lang=request.sender_id.lang, force_send=force_send)

    @api.onchange('state_id')
    def onchange_state_id(self):
        if self.state_id:
            if self.state_id.rating_template_id:
                self._send_courier_rating_mail()

    #    Portal
    def _compute_access_url(self):
        super(courier_request, self)._compute_access_url()
        for advice in self:
            advice.access_url = '/my/request/%s' % (advice.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % (_('request'), self.name)

    @api.model
    def get_default_state(self):
        return self.env['dev.courier.stages'].search([], order='sequence', limit=1).id

    @api.onchange('signature')
    def onchange_signature(self):
        self.signature_date = datetime.now()

    def generate_barcode(self, parcel_line_id):
        def rounit(x):
            return int(math.ceil(x / 10.0)) * 10

        def pre_barcode(n):
            _start = 10 ** (n - 1)
            _end = (10 ** n) - 1
            return randint(_start, _end)

        barcode_num = pre_barcode(12)
        barcode_list = list(map(int, str(barcode_num)))
        calculation = barcode_list[0] * 1 + barcode_list[1] * 3 + \
                      barcode_list[2] * 1 + barcode_list[3] * 3 + \
                      barcode_list[4] * 1 + barcode_list[5] * 3 + \
                      barcode_list[6] * 1 + barcode_list[7] * 3 + \
                      barcode_list[8] * 1 + barcode_list[9] * 3 + \
                      barcode_list[10] * 1 + barcode_list[11] * 3
        rounded = rounit(calculation)
        check_sum = rounded - calculation
        barcode_list.append(check_sum)
        makenum = lambda barcode_list: int(
            ''.join(str(i) for i in barcode_list))
        barcode_number = makenum(barcode_list)
        parcel_line_id.barcode = barcode_number
        ean = barcode.get('ean13', str(barcode_number), writer=ImageWriter())
        img_barcode = ean.save('barcode')
        base64_image = open(img_barcode, 'rb')
        image_read = base64_image.read()
        barcode_image = base64.encodebytes(image_read)
        parcel_line_id.barcode_image = barcode_image

    def generate_parcel_barcode(self):
        if not self.courier_lines:
            raise UserError(_('''Please add Parcel Details !'''))
        for parcel_line_id in self.courier_lines:
            self.generate_barcode(parcel_line_id)

    @api.onchange('sender_mobile')
    def onchange_sender_mobile(self):
        if self.sender_mobile:
            partner_id = self.env['res.partner'].sudo().search(
                ['&', '|', ('phone', '=', self.sender_mobile), ('mobile', '=', self.sender_mobile),
                 ('courier', '=', True)],
                limit=1)
            if partner_id:
                self.sender_id = partner_id.id

    @api.onchange('receiver_mobile')
    def onchange_receiver_mobile(self):
        if self.receiver_mobile:
            partner_id = self.env['res.partner'].sudo().search(
                ['&', '|', ('phone', '=', self.receiver_mobile), ('mobile', '=', self.receiver_mobile),
                 ('courier', '=', True)],
                limit=1)
            if partner_id:
                self.receiver_id = partner_id.id

    def create_tasks(self):
        project_id = self.env.company and self.env.company.cm_project_id or False
        if not project_id:
            raise UserError(_('''Configure Project into Courier Management > Configuration > Settings'''))
        lines = []
        for line_id in self.courier_lines:
            line_vals = {'parcel_line_id': line_id.id}
            lines.append((0, 0, line_vals))
        vals = {'courier_request_id': self.id,
                'project_id': project_id and project_id.id or False,
                'line_ids': lines
                }
        wizard_id = self.env['cm.parcel.tasks'].sudo().create(vals)
        action = self.env.ref('dev_courier_management.action_cm_parcel_tasks').sudo().read()[0]
        action.update({'res_id': wizard_id.id})
        return action

    def _compute_task_count(self):
        for rec in self:
            count = len(rec.parcel_task_ids)
            rec.task_count = count

    def view_tasks(self):
        action = self.env.ref('project.action_view_all_task').sudo().read()[0]
        action.update({'display_name': 'Parcel Tasks'})
        if len(self.parcel_task_ids) > 1:
            action['domain'] = [('id', 'in', self.parcel_task_ids.ids)]
        elif len(self.parcel_task_ids) == 1:
            action['views'] = [(self.env.ref('project.view_task_form2').id, 'form')]
            action['res_id'] = self.parcel_task_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action['context'] = {}
        return action

    name = fields.Char('Name', default='/', copy=False)
    sender_id = fields.Many2one('res.partner', string='Sender', required=True, domain=[('courier', '=', True)])
    sender_name = fields.Char('Sender Name', required=True, tracking=1)
    sender_street = fields.Char('Sender Street', required=True)
    sender_street2 = fields.Char('Sender Street2')
    sender_city = fields.Char('Sender City', required=True)
    sender_state_id = fields.Many2one('res.country.state', string='Sender State', required=True)
    sender_country_id = fields.Many2one('res.country', string='Sender Country', required=True)
    sender_zip = fields.Char('Sender Zip', required=True)
    sender_mobile = fields.Char('Sender Mobile', required=True, tracking=1)
    sender_email = fields.Char('Sender Email', required=True)

    receiver_id = fields.Many2one('res.partner', string='Receiver', required=True, domain=[('courier', '=', True)])
    receiver_name = fields.Char('Sender Name', required=True, tracking=1)
    receiver_street = fields.Char('Street', required=True)
    receiver_street2 = fields.Char('Street2')
    receiver_city = fields.Char('City', required=True)
    receiver_state_id = fields.Many2one('res.country.state', string='State', required=True)
    receiver_country_id = fields.Many2one('res.country', string='Country', required=True)
    receiver_zip = fields.Char('Zip', required=True)
    receiver_mobile = fields.Char('Receiver Mobile', required=True, tracking=1)
    receiver_email = fields.Char('Receiver Email', required=True)

    registration_date = fields.Date('Registration Date', default=datetime.today(), tracking=1)
    delivery_date = fields.Date('Delivery Date', tracking=1)
    courier_type_id = fields.Many2one('dev.courier.type', string='Type', tracking=1)
    category_id = fields.Many2one('dev.courier.category', string='Category', tracking=1)
    priority_id = fields.Many2one('dev.courier.priority', string='Priority', tracking=1)

    tag_ids = fields.Many2many('dev.courier.tags', string='Tags')
    total_km = fields.Integer('Kilometres', tracking=1)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    state_id = fields.Many2one('dev.courier.stages', string='Status', compute='_compte_stage_id', index=True,
                               tracking=1,
                               readonly=False, store=True, group_expand='_read_group_stage_ids', ondelete='restrict',
                               default=get_default_state)

    courier_lines = fields.One2many('courier.request.lines', 'request_id', string='Courier Lines')
    notes = fields.Text('Notes')
    courier_charge = fields.Monetary('Courier Charge', compute='_get_courier_charge')
    distance_charge = fields.Monetary('Distance Charge', compute='_get_distance_charge')
    edi_distance_charge = fields.Monetary('Distance Charges')
    edi_additional_charge = fields.Monetary('Additional Charges')
    additional_charge = fields.Monetary('Additional Charge', compute='_get_additional_charge')
    total_charge_amount = fields.Monetary('Total Charge', compute='_get_total_charge', store=True)
    invoice_count = fields.Integer('Invoice Count', compute='_get_invoice_count')
    allow_invoice = fields.Boolean('Allow Invoice', compute='compute_allow_invoice')
    color = fields.Integer()
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    courier_image_ids = fields.One2many('ir.attachment', 'courier_request_id', string='Parcel Images')
    total_parcel = fields.Integer(string='Total Parcel', compute='_compute_total_parcel')
    signature_name = fields.Char(string='Full Name', tracking=1, copy=False)
    signature_date = fields.Datetime(string='Signature Date', tracking=1, copy=False)
    signature = fields.Binary(string='Signature', copy=False)
    parcel_task_ids = fields.One2many('project.task', 'courier_request_id', string='Tasks')
    task_count = fields.Integer(string='Tasks', compute='_compute_task_count')
    preference = fields.Selection(string='Preference', selection=[('self_drop', 'Self Drop by Customer'), ('pickup', 'Pickup by Courier Agent')],
                             default='self_drop', required=True)
    wcr_id = fields.Many2one('cm.website.courier.request', string='Website Courier Request')

    @api.depends('courier_lines')
    def _compute_total_parcel(self):
        for rec in self:
            parcel = sum(line.quantity for line in self.courier_lines)
            rec.total_parcel = parcel

    def get_formatted_date(self):
        date = datetime.strptime(str(self.registration_date), "%Y-%m-%d").strftime('%d/%m/%Y')
        return date

    def send_by_mail(self):
        self.ensure_one()
        template_id = self.env.ref('dev_courier_management.template_dev_courier_request_send_by_mail')
        ctx = {
            'default_model': 'dev.courier.request',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id and template_id.id),
            'default_template_id': template_id and template_id.id or False,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': False,
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def _get_invoice_count(self):
        for rec in self:
            invoice_ids = self.env['account.move'].sudo().search([('courier_request_id', '=', rec.id),
                                                                  ('move_type', '=', 'out_invoice')])
            rec.invoice_count = len(invoice_ids)

    @api.onchange('sender_id')
    def onchange_sender(self):
        if self.sender_id:
            vals = {
                'sender_name': self.sender_id.name or '',
                'sender_street': self.sender_id.street or '',
                'sender_street2': self.sender_id.street2 or '',
                'sender_city': self.sender_id.city or '',
                'sender_state_id': self.sender_id.state_id.id or False,
                'sender_country_id': self.sender_id.country_id.id or False,
                'sender_zip': self.sender_id.zip or False,
                'sender_mobile': self.sender_id.mobile or self.sender_id.phone or False,
                'sender_email': self.sender_id.email or ''
            }
            self.write(vals)
        else:
            vals = {
                'sender_name': '',
                'sender_street': '',
                'sender_street2': '',
                'sender_city': False,
                'sender_state_id': False,
                'sender_country_id': False,
                'sender_city': False,
                'sender_zip': '',
                'sender_mobile': '',
                'sender_email': ''
            }
            self.write(vals)

    @api.onchange('receiver_id')
    def onchange_receiver(self):
        if self.receiver_id:
            vals = {
                'receiver_name': self.receiver_id.name or '',
                'receiver_street': self.receiver_id.street or '',
                'receiver_street2': self.receiver_id.street2 or '',
                'receiver_city': self.receiver_id.city or '',
                'receiver_state_id': self.receiver_id.state_id.id or False,
                'receiver_country_id': self.receiver_id.country_id.id or False,
                'receiver_zip': self.receiver_id.zip or False,
                'receiver_mobile': self.receiver_id.mobile or self.receiver_id.phone or False,
                'receiver_email': self.receiver_id.email or '',
            }
            self.write(vals)
        else:
            vals = {
                'receiver_name': '',
                'receiver_street': '',
                'receiver_street2': '',
                'receiver_city': False, 'receiver_state_id': False,
                'receiver_country_id': False, 'receiver_city': False,
                'receiver_zip': '',
                'receiver_mobile': '',
                'receiver_email': '',
            }
            self.write(vals)

    @api.depends('total_km', 'edi_distance_charge')
    def _get_distance_charge(self):
        for request in self:
            if request.edi_distance_charge:
                request.distance_charge = request.edi_distance_charge
            else:
                dis_id = self.env['dev.courier.distance.rule'].search([('from_km', '<=', request.total_km),
                                                                       ('to_km', '>=', request.total_km)], order='id',
                                                                      limit=1)
                if dis_id:
                    request.distance_charge = dis_id.price
                    request.edi_distance_charge = dis_id.price
                else:
                    request.distance_charge = 0
                    request.edi_distance_charge = 0

    @api.depends('courier_charge', 'priority_id', 'total_km', 'edi_additional_charge')
    def _get_additional_charge(self):
        for request in self:
            if request.edi_additional_charge:
                request.additional_charge = request.edi_additional_charge
            else:
                amount = ((request.courier_charge * request.total_km) / 100) * request.priority_id.price
                request.additional_charge = amount
                request.edi_additional_charge = amount

    @api.depends('courier_lines', 'courier_lines.total_price')
    def _get_courier_charge(self):
        for request in self:
            request.courier_charge = sum([line.total_price for line in request.courier_lines])

    @api.depends('courier_charge', 'distance_charge', 'additional_charge')
    def _get_total_charge(self):
        for request in self:
            request.total_charge_amount = request.courier_charge + request.distance_charge + request.additional_charge

    @api.depends('sender_name')
    def _compte_stage_id(self):
        for request in self:
            if not request.state_id:
                request.state_id = self.env['dev.courier.stages'].search([], order='sequence', limit=1).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = []
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('dev.courier.sequence') or 'New'
        request_id = super(courier_request, self).create(vals)
        if request_id.sender_id:
            if request_id.sender_id.id not in request_id.message_partner_ids.ids:
                request_id.message_subscribe(partner_ids=request_id.sender_id.ids)
        if request_id.receiver_id:
            if request_id.receiver_id.id not in request_id.message_partner_ids.ids:
                request_id.message_subscribe(partner_ids=request_id.receiver_id.ids)
        return request_id

    @api.onchange('sender_state_id', 'receiver_state_id')
    def onchange_state(self):
        if self.sender_state_id:
            self.sender_country_id = self.sender_state_id.country_id and self.sender_state_id.country_id.id or False
        if self.receiver_state_id:
            self.receiver_country_id = self.receiver_state_id.country_id and self.receiver_state_id.country_id.id or False

    def unlink(self):
        for request in self:
            name = ''
            for state in request.company_id.cur_delete_state_ids:
                if name:
                    name = name + ', ' + state.name
                else:
                    name = state.name

            if request.state_id.id not in request.company_id.cur_delete_state_ids.ids:
                raise ValidationError(_("Request can be deleted only in '%s' states !") % (name))
        return super(courier_request, self).unlink()

    def get_courier_product_lines(self):
        inv_line = []
        for line in self.courier_lines:
            tax_ids = []
            product_id = self.company_id.courier_product_id
            if product_id.taxes_id:
                tax_ids = product_id.taxes_id.ids
            price = line.price
            if line.dim_price > price:
                price = line.dim_price
            inv_line.append((0, 0, {
                'product_id': product_id.id,
                'quantity': line.quantity,
                'name': line.name,
                'product_uom_id': product_id.uom_id and product_id.uom_id.id or False,
                'price_unit': price,
                'tax_ids': [(6, 0, tax_ids)],
            }))
        if self.company_id.distance_product_id and self.distance_charge:
            product_id = self.company_id.distance_product_id
            tax_ids = []
            if product_id.taxes_id:
                tax_ids = product_id.taxes_id.ids
            price = self.distance_charge
            inv_line.append((0, 0, {
                'product_id': product_id.id,
                'quantity': 1,
                'name': 'Distance Charge',
                'product_uom_id': product_id.uom_id and product_id.uom_id.id or False,
                'price_unit': price,
                'tax_ids': [(6, 0, tax_ids)],
            }))

        if self.company_id.additional_charge_pro_id and self.additional_charge:
            product_id = self.company_id.additional_charge_pro_id
            tax_ids = []
            if product_id.taxes_id:
                tax_ids = product_id.taxes_id.ids
            price = self.additional_charge
            inv_line.append((0, 0, {
                'product_id': product_id.id,
                'quantity': 1,
                'name': 'Additional Charge',
                'product_uom_id': product_id.uom_id and product_id.uom_id.id or False,
                'price_unit': price,
                'tax_ids': [(6, 0, tax_ids)],
            }))
        return inv_line

    @api.depends('state_id')
    def compute_allow_invoice(self):
        for request in self:
            if request.state_id.allow_create_invoice:
                request.allow_invoice = True
            else:
                request.allow_invoice = False

    def action_view_invoice(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        invoice_ids = self.env['account.move'].search([('courier_request_id', '=', self.id),
                                                       ('move_type', '=', 'out_invoice')])
        if len(invoice_ids) > 1:
            action['domain'] = [('id', 'in', invoice_ids.ids)]
        elif invoice_ids:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoice_ids.id
        action['context'] = {
            'create': 0,
        }
        return action

    def create_customer_invoice(self):
        journal_pool = self.env['account.journal'].sudo()
        journal_id = journal_pool.search([('type', '=', 'sale')], limit=1)
        if not journal_id:
            raise ValidationError(_('Please Create Sale Journal'))
        if not self.company_id.courier_product_id:
            raise ValidationError(_('Please Select Courier Product in Courier Setting.'))
        if not self.company_id.distance_product_id:
            raise ValidationError(_('Please Select Distance Charge Product in Courier Setting.'))
        if not self.company_id.additional_charge_pro_id:
            raise ValidationError(_('Please Select Additional Charge Product in Courier Setting.'))
        inv_val = {
            'partner_id': self.sender_id and self.sender_id.id or False,
            'courier_request_id': self.id,
            'move_type': 'out_invoice',
            'journal_id': journal_id and journal_id.id or False,
            'currency_id': self.currency_id and self.currency_id.id or False,
            'invoice_line_ids': self.get_courier_product_lines(),
            'state': 'draft',
            'company_id': self.company_id and self.company_id.id or False,
        }
        inv_id = self.env['account.move'].create(inv_val)
        if inv_id:
            action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = inv_id.id
            context = {
                'default_move_type': 'out_invoice',
                "create": False,
            }
            return action


class courier_lines(models.Model):
    _name = "courier.request.lines"
    _description = 'Courier Details'

    name = fields.Char('Name', required=True)
    description = fields.Char(string='Description')
    quantity = fields.Integer('Quantity', default=1, required=True)
    weight = fields.Float('Weight(KG)', required=True)
    dimension_id = fields.Many2one('dev.courier.dimension.rule', string='L X W X H')
    price = fields.Monetary('Weight Price')
    dim_price = fields.Monetary('Dimension Price')
    total_price = fields.Monetary('Subtotal', compute='_get_total_price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    request_id = fields.Many2one('dev.courier.request', string='Courier Request')
    barcode = fields.Char(string='Barcode Number')
    barcode_image = fields.Binary(string='Barcode')

    @api.depends('quantity', 'price', 'dim_price')
    def _get_total_price(self):
        for line in self:
            price = line.price
            if line.dim_price > line.price:
                price = line.dim_price
            line.total_price = line.quantity * price

    @api.onchange('weight')
    def onchange_weight(self):
        if self.weight:
            rule_id = self.env['dev.courier.weight.rule'].search([('from_weight', '<=', self.weight),
                                                                  ('to_weight', '>=', self.weight)], order="id",
                                                                 limit=1)
            if rule_id:
                self.price = rule_id.price
            else:
                self.price = 0
        else:
            self.price = 0

    @api.onchange('dimension_id')
    def onchange_dimension(self):
        print("self======", self)
        if self.dimension_id:
            self.dim_price = self.dimension_id.price
        else:
            self.dim_price = 0.0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
