# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class DebtRecord(models.Model):
    _name = 'debt.record'
    _description = 'Debt Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'debt_reference'

    # Basic Information
    debt_reference = fields.Char(
        string='Debt Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    creditor_id = fields.Many2one(
        'res.partner',
        string='Creditor/Lender',
        required=True,
        domain=[('is_company', '=', True)],
        tracking=True,
        help="The creditor or lending institution"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True
    )
    
    # Financial Information
    debt_amount = fields.Monetary(
        string='Debt Amount',
        required=True,
        currency_field='currency_id',
        tracking=True,
        help="Original debt amount"
    )
    
    outstanding_amount = fields.Monetary(
        string='Outstanding Amount',
        compute='_compute_outstanding_amount',
        store=True,
        currency_field='currency_id',
        help="Current outstanding debt amount"
    )
    
    paid_amount = fields.Monetary(
        string='Paid Amount',
        compute='_compute_paid_amount',
        store=True,
        currency_field='currency_id',
        help="Total amount paid so far"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
        tracking=True
    )
    
    interest_rate = fields.Float(
        string='Interest Rate (%)',
        digits=(5, 2),
        default=0.0,
        tracking=True,
        help="Annual interest rate percentage"
    )
    
    # Dates
    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        help="Date when the debt was incurred"
    )
    
    due_date = fields.Date(
        string='Due Date',
        required=True,
        tracking=True,
        help="Final payment due date"
    )
    
    next_payment_date = fields.Date(
        string='Next Payment Date',
        compute='_compute_next_payment_date',
        store=True,
        help="Date of the next scheduled payment"
    )
    
    # Classification
    debt_category_id = fields.Many2one(
        'debt.category',
        string='Debt Category',
        required=True,
        tracking=True,
        help="Category or type of debt"
    )
    
    debt_type = fields.Selection([
        ('loan', 'Loan'),
        ('credit_card', 'Credit Card'),
        ('mortgage', 'Mortgage'),
        ('line_of_credit', 'Line of Credit'),
        ('bond', 'Bond'),
        ('other', 'Other')
    ], string='Debt Type', required=True, default='loan', tracking=True)
    
    # Status and State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Priority', default='1', tracking=True)
    
    # Additional Information
    description = fields.Text(
        string='Description/Notes',
        help="Additional notes about this debt"
    )
    
    payment_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual'),
        ('one_time', 'One Time')
    ], string='Payment Frequency', default='monthly', required=True)
    
    # Computed Fields
    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_days_overdue',
        store=True,
        help="Number of days past due date"
    )
    
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        store=True,
        help="True if debt is past due date"
    )
    
    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_count',
        help="Number of payments made"
    )
    
    # Relations
    payment_ids = fields.One2many(
        'debt.payment',
        'debt_record_id',
        string='Payments',
        help="Payment records for this debt"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('debt_reference', _('New')) == _('New'):
                vals['debt_reference'] = self.env['ir.sequence'].next_by_code('debt.record') or _('New')

        records = super(DebtRecord, self).create(vals_list)

        # Update category statistics
        categories = records.mapped('debt_category_id')
        if categories:
            categories._compute_debt_count()
            categories._compute_debt_statistics()
        return records

    @api.depends('debt_amount', 'payment_ids.amount')
    def _compute_paid_amount(self):
        for record in self:
            record.paid_amount = sum(record.payment_ids.mapped('amount'))

    @api.depends('debt_amount', 'paid_amount')
    def _compute_outstanding_amount(self):
        for record in self:
            record.outstanding_amount = record.debt_amount - record.paid_amount

    @api.depends('due_date')
    def _compute_days_overdue(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.due_date and record.due_date < today and record.state == 'active':
                record.days_overdue = (today - record.due_date).days
            else:
                record.days_overdue = 0

    @api.depends('days_overdue', 'state')
    def _compute_is_overdue(self):
        for record in self:
            record.is_overdue = record.days_overdue > 0 and record.state == 'active'

    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for record in self:
            record.payment_count = len(record.payment_ids)

    @api.depends('payment_ids', 'payment_frequency', 'start_date')
    def _compute_next_payment_date(self):
        for record in self:
            if record.payment_ids:
                last_payment = max(record.payment_ids.mapped('payment_date'))
                if record.payment_frequency == 'monthly':
                    record.next_payment_date = last_payment + timedelta(days=30)
                elif record.payment_frequency == 'quarterly':
                    record.next_payment_date = last_payment + timedelta(days=90)
                elif record.payment_frequency == 'semi_annual':
                    record.next_payment_date = last_payment + timedelta(days=180)
                elif record.payment_frequency == 'annual':
                    record.next_payment_date = last_payment + timedelta(days=365)
                else:
                    record.next_payment_date = False
            else:
                record.next_payment_date = record.start_date

    @api.constrains('debt_amount')
    def _check_debt_amount(self):
        for record in self:
            if record.debt_amount <= 0:
                raise ValidationError(_('Debt amount must be greater than zero.'))

    @api.constrains('interest_rate')
    def _check_interest_rate(self):
        for record in self:
            if record.interest_rate < 0 or record.interest_rate > 100:
                raise ValidationError(_('Interest rate must be between 0 and 100 percent.'))

    @api.constrains('start_date', 'due_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.due_date and record.start_date > record.due_date:
                raise ValidationError(_('Start date cannot be later than due date.'))

    def action_activate(self):
        """Activate the debt record"""
        self.write({'state': 'active'})
        self.message_post(body=_('Debt record has been activated.'))

    def action_mark_paid(self):
        """Mark debt as fully paid"""
        if self.outstanding_amount > 0:
            raise UserError(_('Cannot mark as paid. Outstanding amount: %s') % self.outstanding_amount)
        self.write({'state': 'paid'})
        self.message_post(body=_('Debt has been marked as fully paid.'))

    def action_cancel(self):
        """Cancel the debt record"""
        self.write({'state': 'cancelled'})
        self.message_post(body=_('Debt record has been cancelled.'))

    def action_view_payments(self):
        """Open payments view for this debt"""
        return {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'debt.payment',
            'view_mode': 'tree,form',
            'domain': [('debt_record_id', '=', self.id)],
            'context': {'default_debt_record_id': self.id},
        }



    def write(self, vals):
        """Override write to update category statistics"""
        old_categories = self.mapped('debt_category_id')
        result = super(DebtRecord, self).write(vals)

        # Update statistics for old and new categories
        new_categories = self.mapped('debt_category_id')
        all_categories = old_categories | new_categories
        if all_categories:
            all_categories._compute_debt_count()
            all_categories._compute_debt_statistics()
        return result

    def unlink(self):
        """Override unlink to update category statistics"""
        categories = self.mapped('debt_category_id')
        result = super(DebtRecord, self).unlink()
        if categories:
            categories._compute_debt_count()
            categories._compute_debt_statistics()
        return result

    @api.model
    def _cron_update_overdue_status(self):
        """Cron job to update overdue status"""
        today = fields.Date.context_today(self)
        overdue_debts = self.search([
            ('due_date', '<', today),
            ('state', '=', 'active'),
            ('outstanding_amount', '>', 0)
        ])
        overdue_debts.write({'state': 'overdue'})
        _logger.info('Updated %d debt records to overdue status', len(overdue_debts))
