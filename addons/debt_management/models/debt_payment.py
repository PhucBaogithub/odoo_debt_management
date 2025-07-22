# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class DebtPayment(models.Model):
    _name = 'debt.payment'
    _description = 'Debt Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'payment_date desc'
    _rec_name = 'payment_reference'

    payment_reference = fields.Char(
        string='Payment Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    debt_record_id = fields.Many2one(
        'debt.record',
        string='Debt Record',
        required=True,
        ondelete='cascade',
        tracking=True,
        help="Related debt record"
    )
    
    creditor_id = fields.Many2one(
        related='debt_record_id.creditor_id',
        string='Creditor',
        store=True,
        readonly=True,
        help="Creditor from the debt record"
    )
    
    company_id = fields.Many2one(
        related='debt_record_id.company_id',
        string='Company',
        store=True,
        readonly=True,
        help="Company from the debt record"
    )
    
    # Payment Information
    amount = fields.Monetary(
        string='Payment Amount',
        required=True,
        currency_field='currency_id',
        tracking=True,
        help="Amount paid in this payment"
    )
    
    currency_id = fields.Many2one(
        related='debt_record_id.currency_id',
        string='Currency',
        store=True,
        readonly=True,
        help="Currency from the debt record"
    )
    
    payment_date = fields.Date(
        string='Payment Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        help="Date when the payment was made"
    )
    
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('online', 'Online Payment'),
        ('other', 'Other')
    ], string='Payment Method', required=True, default='bank_transfer', tracking=True)
    
    # Payment Type
    payment_type = fields.Selection([
        ('principal', 'Principal Payment'),
        ('interest', 'Interest Payment'),
        ('mixed', 'Principal + Interest'),
        ('penalty', 'Penalty Payment'),
        ('fee', 'Fee Payment')
    ], string='Payment Type', required=True, default='mixed', tracking=True)
    
    principal_amount = fields.Monetary(
        string='Principal Amount',
        currency_field='currency_id',
        help="Principal portion of the payment"
    )
    
    interest_amount = fields.Monetary(
        string='Interest Amount',
        currency_field='currency_id',
        help="Interest portion of the payment"
    )
    
    fee_amount = fields.Monetary(
        string='Fee Amount',
        currency_field='currency_id',
        help="Fee portion of the payment"
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Additional Information
    description = fields.Text(
        string='Description',
        help="Additional notes about this payment"
    )
    
    reference_number = fields.Char(
        string='Reference Number',
        help="Bank reference, check number, or transaction ID"
    )
    
    # Related Information
    remaining_debt = fields.Monetary(
        string='Remaining Debt After Payment',
        compute='_compute_remaining_debt',
        currency_field='currency_id',
        help="Debt amount remaining after this payment"
    )
    
    is_final_payment = fields.Boolean(
        string='Is Final Payment',
        compute='_compute_is_final_payment',
        help="True if this payment clears the debt"
    )

    @api.model
    def create(self, vals):
        if vals.get('payment_reference', _('New')) == _('New'):
            vals['payment_reference'] = self.env['ir.sequence'].next_by_code('debt.payment') or _('New')
        return super(DebtPayment, self).create(vals)

    @api.depends('debt_record_id.outstanding_amount', 'amount')
    def _compute_remaining_debt(self):
        for payment in self:
            if payment.debt_record_id and payment.state == 'confirmed':
                # Calculate what would remain after this payment
                current_outstanding = payment.debt_record_id.outstanding_amount
                payment.remaining_debt = max(0, current_outstanding - payment.amount)
            else:
                payment.remaining_debt = payment.debt_record_id.outstanding_amount if payment.debt_record_id else 0

    @api.depends('remaining_debt')
    def _compute_is_final_payment(self):
        for payment in self:
            payment.is_final_payment = payment.remaining_debt == 0

    @api.onchange('amount', 'payment_type')
    def _onchange_amount_breakdown(self):
        """Auto-calculate principal and interest breakdown"""
        if self.payment_type == 'principal':
            self.principal_amount = self.amount
            self.interest_amount = 0
            self.fee_amount = 0
        elif self.payment_type == 'interest':
            self.principal_amount = 0
            self.interest_amount = self.amount
            self.fee_amount = 0
        elif self.payment_type == 'fee':
            self.principal_amount = 0
            self.interest_amount = 0
            self.fee_amount = self.amount
        elif self.payment_type == 'mixed' and self.debt_record_id:
            # Simple calculation - could be enhanced with proper interest calculation
            if self.debt_record_id.interest_rate > 0:
                # Assume 80% principal, 20% interest for mixed payments
                self.principal_amount = self.amount * 0.8
                self.interest_amount = self.amount * 0.2
                self.fee_amount = 0
            else:
                self.principal_amount = self.amount
                self.interest_amount = 0
                self.fee_amount = 0

    @api.constrains('amount')
    def _check_payment_amount(self):
        for payment in self:
            if payment.amount <= 0:
                raise ValidationError(_('Payment amount must be greater than zero.'))
            
            if payment.debt_record_id and payment.amount > payment.debt_record_id.outstanding_amount:
                raise ValidationError(_(
                    'Payment amount (%(amount)s) cannot exceed outstanding debt amount (%(outstanding)s).'
                ) % {
                    'amount': payment.amount,
                    'outstanding': payment.debt_record_id.outstanding_amount
                })

    @api.constrains('principal_amount', 'interest_amount', 'fee_amount', 'amount')
    def _check_payment_breakdown(self):
        for payment in self:
            total_breakdown = (payment.principal_amount or 0) + (payment.interest_amount or 0) + (payment.fee_amount or 0)
            if abs(total_breakdown - payment.amount) > 0.01:  # Allow small rounding differences
                raise ValidationError(_(
                    'The sum of principal, interest, and fee amounts must equal the total payment amount.'
                ))

    @api.constrains('payment_date', 'debt_record_id')
    def _check_payment_date(self):
        for payment in self:
            if payment.debt_record_id and payment.payment_date < payment.debt_record_id.start_date:
                raise ValidationError(_(
                    'Payment date cannot be earlier than the debt start date.'
                ))

    def action_confirm(self):
        """Confirm the payment"""
        self.write({'state': 'confirmed'})
        self.message_post(body=_('Payment has been confirmed.'))
        
        # Check if debt is fully paid
        if self.is_final_payment:
            self.debt_record_id.action_mark_paid()

    def action_cancel(self):
        """Cancel the payment"""
        if self.state == 'confirmed':
            # If cancelling a confirmed payment, update debt status
            self.debt_record_id._compute_outstanding_amount()
            if self.debt_record_id.state == 'paid':
                self.debt_record_id.write({'state': 'active'})
        
        self.write({'state': 'cancelled'})
        self.message_post(body=_('Payment has been cancelled.'))

    def action_set_to_draft(self):
        """Set payment back to draft"""
        self.write({'state': 'draft'})
        self.message_post(body=_('Payment has been set back to draft.'))

    def unlink(self):
        """Override unlink to check for confirmed payments"""
        for payment in self:
            if payment.state == 'confirmed':
                raise UserError(_('Cannot delete confirmed payments. Please cancel the payment first.'))
        return super(DebtPayment, self).unlink()
