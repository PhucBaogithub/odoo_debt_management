# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class TestDebtRecord(TransactionCase):

    def setUp(self):
        super(TestDebtRecord, self).setUp()
        
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

    def test_debt_record_creation(self):
        """Test basic debt record creation"""
        debt = self.env['debt.record'].create({
            'creditor_id': self.creditor.id,
            'debt_category_id': self.category.id,
            'debt_amount': 10000.0,
            'interest_rate': 5.0,
            'start_date': datetime.now().date(),
            'due_date': (datetime.now() + timedelta(days=365)).date(),
        })
        
        self.assertTrue(debt.debt_reference)
        self.assertEqual(debt.state, 'draft')
        self.assertEqual(debt.outstanding_amount, 10000.0)
        self.assertEqual(debt.paid_amount, 0.0)

    def test_debt_amount_validation(self):
        """Test debt amount validation"""
        with self.assertRaises(ValidationError):
            self.env['debt.record'].create({
                'creditor_id': self.creditor.id,
                'debt_category_id': self.category.id,
                'debt_amount': -1000.0,  # Invalid negative amount
                'interest_rate': 5.0,
                'start_date': datetime.now().date(),
                'due_date': (datetime.now() + timedelta(days=365)).date(),
            })

    def test_interest_rate_validation(self):
        """Test interest rate validation"""
        with self.assertRaises(ValidationError):
            self.env['debt.record'].create({
                'creditor_id': self.creditor.id,
                'debt_category_id': self.category.id,
                'debt_amount': 10000.0,
                'interest_rate': 150.0,  # Invalid rate > 100%
                'start_date': datetime.now().date(),
                'due_date': (datetime.now() + timedelta(days=365)).date(),
            })

    def test_date_validation(self):
        """Test date validation"""
        with self.assertRaises(ValidationError):
            self.env['debt.record'].create({
                'creditor_id': self.creditor.id,
                'debt_category_id': self.category.id,
                'debt_amount': 10000.0,
                'interest_rate': 5.0,
                'start_date': datetime.now().date(),
                'due_date': (datetime.now() - timedelta(days=30)).date(),  # Due date before start date
            })

    def test_debt_activation(self):
        """Test debt activation"""
        debt = self.env['debt.record'].create({
            'creditor_id': self.creditor.id,
            'debt_category_id': self.category.id,
            'debt_amount': 10000.0,
            'interest_rate': 5.0,
            'start_date': datetime.now().date(),
            'due_date': (datetime.now() + timedelta(days=365)).date(),
        })
        
        debt.action_activate()
        self.assertEqual(debt.state, 'active')

    def test_overdue_calculation(self):
        """Test overdue calculation"""
        debt = self.env['debt.record'].create({
            'creditor_id': self.creditor.id,
            'debt_category_id': self.category.id,
            'debt_amount': 10000.0,
            'interest_rate': 5.0,
            'start_date': (datetime.now() - timedelta(days=400)).date(),
            'due_date': (datetime.now() - timedelta(days=30)).date(),  # Past due date
            'state': 'active',
        })
        
        debt._compute_days_overdue()
        debt._compute_is_overdue()
        
        self.assertTrue(debt.days_overdue > 0)
        self.assertTrue(debt.is_overdue)
