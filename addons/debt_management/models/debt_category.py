# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DebtCategory(models.Model):
    _name = 'debt.category'
    _description = 'Debt Category'
    _order = 'sequence, name'

    name = fields.Char(
        string='Category Name',
        required=True,
        translate=True,
        help="Name of the debt category"
    )
    
    code = fields.Char(
        string='Category Code',
        required=True,
        help="Unique code for the debt category"
    )
    
    description = fields.Text(
        string='Description',
        translate=True,
        help="Description of the debt category"
    )
    
    color = fields.Integer(
        string='Color',
        default=0,
        help="Color for the category in kanban view"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Sequence for ordering categories"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help="If unchecked, it will allow you to hide the category without removing it"
    )
    
    parent_id = fields.Many2one(
        'debt.category',
        string='Parent Category',
        index=True,
        ondelete='cascade',
        help="Parent category for hierarchical organization"
    )
    
    child_ids = fields.One2many(
        'debt.category',
        'parent_id',
        string='Child Categories',
        help="Child categories under this category"
    )
    
    debt_count = fields.Integer(
        string='Debt Count',
        compute='_compute_debt_count',
        help="Number of debts in this category"
    )
    
    total_debt_amount = fields.Monetary(
        string='Total Debt Amount',
        compute='_compute_debt_statistics',
        currency_field='currency_id',
        help="Total debt amount in this category"
    )
    
    outstanding_debt_amount = fields.Monetary(
        string='Outstanding Debt Amount',
        compute='_compute_debt_statistics',
        currency_field='currency_id',
        help="Total outstanding debt amount in this category"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        help="Currency for debt amounts"
    )
    
    # Computed fields for category path
    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True,
        help="Complete category path"
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Category code must be unique!'),
    ]

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = f"{category.parent_id.complete_name} / {category.name}"
            else:
                category.complete_name = category.name

    def _compute_debt_count(self):
        for category in self:
            category.debt_count = self.env['debt.record'].search_count([
                ('debt_category_id', '=', category.id)
            ])

    def _compute_debt_statistics(self):
        for category in self:
            debts = self.env['debt.record'].search([
                ('debt_category_id', '=', category.id)
            ])
            category.total_debt_amount = sum(debts.mapped('debt_amount'))
            category.outstanding_debt_amount = sum(debts.mapped('outstanding_amount'))

    @api.constrains('parent_id')
    def _check_parent_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))

    def name_get(self):
        result = []
        for category in self:
            name = category.complete_name or category.name
            result.append((category.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Search in both name and complete_name
            categories = self._search([
                '|',
                ('name', operator, name),
                ('complete_name', operator, name)
            ] + args, limit=limit, access_rights_uid=name_get_uid)
            return self.browse(categories).name_get()
        return super(DebtCategory, self)._name_search(
            name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )

    def action_view_debts(self):
        """Open debts view for this category"""
        return {
            'name': _('Debts in Category: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'debt.record',
            'view_mode': 'tree,form,kanban',
            'domain': [('debt_category_id', '=', self.id)],
            'context': {'default_debt_category_id': self.id},
        }
