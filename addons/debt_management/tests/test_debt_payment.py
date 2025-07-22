# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class TestDebtPayment(TransactionCase):

    def setUp(self):
        super(TestDebtPayment, self).setUp()
        
        # Create test creditor
        self.creditor = self.env['res.partner'].create({
            'name': 'Test Bank',
            'is_company': True,
        })
        
        # Create test category
        self.category = self.env['debt.category'].create({
            'name': 'Test Loan',
            'code': 'TL',
        })
        
        # Create test debt record
        self.debt = self.env['debt.record'].create({
            'creditor_id': self.creditor.id,
            'debt_category_id': self.category.id,
            'debt_amount': 10000.0,
            'interest_rate': 5.0,
            'start_date': datetime.now().date(),
            'due_date': (datetime.now() + timedelta(days=365)).date(),
            'state': 'active',
        })

    def test_payment_creation(self):
        """Test basic payment creation"""
        payment = self.env['debt.payment'].create({
            'debt_record_id': self.debt.id,
            'amount': 1000.0,
            'payment_date': datetime.now().date(),
            'payment_method': 'bank_transfer',
            'payment_type': 'mixed',
        })
        
        self.assertTrue(payment.payment_reference)
        self.assertEqual(payment.state, 'draft')
        self.assertEqual(payment.creditor_id, self.creditor)

    def test_payment_amount_validation(self):
        """Test payment amount validation"""
        with self.assertRaises(ValidationError):
            self.env['debt.payment'].create({
                'debt_record_id': self.debt.id,
                'amount': -100.0,  # Invalid negative amount
                'payment_date': datetime.now().date(),
                'payment_method': 'bank_transfer',
                'payment_type': 'mixed',
            })

    def test_payment_exceeds_debt(self):
        """Test payment amount exceeding debt"""
        with self.assertRaises(ValidationError):
            self.env['debt.payment'].create({
                'debt_record_id': self.debt.id,
                'amount': 15000.0,  # Exceeds debt amount
                'payment_date': datetime.now().date(),
                'payment_method': 'bank_transfer',
                'payment_type': 'mixed',
            })

    def test_payment_confirmation(self):
        """Test payment confirmation"""
        payment = self.env['debt.payment'].create({
            'debt_record_id': self.debt.id,
            'amount': 1000.0,
            'payment_date': datetime.now().date(),
            'payment_method': 'bank_transfer',
            'payment_type': 'mixed',
        })
        
        payment.action_confirm()
        self.assertEqual(payment.state, 'confirmed')

    def test_payment_breakdown_validation(self):
        """Test payment breakdown validation"""
        with self.assertRaises(ValidationError):
            payment = self.env['debt.payment'].create({
                'debt_record_id': self.debt.id,
                'amount': 1000.0,
                'payment_date': datetime.now().date(),
                'payment_method': 'bank_transfer',
                'payment_type': 'mixed',
                'principal_amount': 800.0,
                'interest_amount': 300.0,  # Total exceeds payment amount
                'fee_amount': 0.0,
            })

    def test_outstanding_amount_calculation(self):
        """Test outstanding amount calculation after payment"""
        payment = self.env['debt.payment'].create({
            'debt_record_id': self.debt.id,
            'amount': 2000.0,
            'payment_date': datetime.now().date(),
            'payment_method': 'bank_transfer',
            'payment_type': 'principal',
            'principal_amount': 2000.0,
        })
        
        payment.action_confirm()
        
        # Refresh debt record to get updated amounts
        self.debt.invalidate_cache()
        self.assertEqual(self.debt.paid_amount, 2000.0)
        self.assertEqual(self.debt.outstanding_amount, 8000.0)
