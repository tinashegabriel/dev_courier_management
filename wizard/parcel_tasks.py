# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##########################################################################

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class CreateParcelTasks(models.TransientModel):
    _name = 'cm.parcel.tasks'
    _description = 'Create Parcel Tasks'

    def create_tasks(self):
        project_id = self.env.company.cm_project_id or False
        if any(not rec.employee_id for rec in self.line_ids):
            raise ValidationError(_('''Add Delivery Boy in all Parcel !'''))
        if any(not rec.parcel for rec in self.line_ids):
            raise ValidationError(_('''Add Parcel in all the lines !'''))
        for line_id in self.line_ids:
            notes = '''<b>Delivery Item</b> : ''' + line_id.parcel
            if line_id.notes:
                notes += '''<br/><br/><b>Delivery Instructions</b> : ''' + line_id.notes
            if not line_id.employee_id.user_id:
                raise ValidationError(_('''Related User is not linked with %s Staff Member''') % (line_id.employee_id.name))
            vals = {'project_id': project_id and project_id.id or False,
                    'name': self.courier_request_id.name + ' : ' + line_id.parcel,
                    'user_ids': [(6, 0, [line_id.employee_id.user_id.id])],
                    'description': notes,
                    'courier_request_id': self.courier_request_id and self.courier_request_id.id or False,
                    'parcel_line_id_number': line_id.id
                    }
            task_id = self.env['project.task'].create(vals)


    courier_request_id = fields.Many2one('dev.courier.request', string='Courier Request')
    project_id = fields.Many2one('project.project', string='Project')
    line_ids = fields.One2many('cm.parcel.tasks.line', 'wizard_id', string='Lines')


class CreateParcelTasksLine(models.TransientModel):
    _name = 'cm.parcel.tasks.line'
    _description = 'Parcel Tasks Lines'

    wizard_id = fields.Many2one('cm.parcel.tasks', string='Parcel Task Wizard')
    parcel_line_id = fields.Many2one('courier.request.lines', string='Parcel Line')
    parcel = fields.Char(string='Parcel', related='parcel_line_id.name')
    notes = fields.Text(string='Delivery Instructions')
    employee_id = fields.Many2one('hr.employee', string='Delivery Boy', domain=[('cm_delivery_boy', '=', True)])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
