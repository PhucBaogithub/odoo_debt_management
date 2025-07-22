# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestDebtCategory(TransactionCase):

    def test_category_creation(self):
        """Test basic category creation"""
        category = self.env['debt.category'].create({
            'name': 'Business Loan',
            'code': 'BL',
            'description': 'Business loans and financing',
        })
        
        self.assertEqual(category.name, 'Business Loan')
        self.assertEqual(category.code, 'BL')
        self.assertTrue(category.active)

    def test_category_code_uniqueness(self):
        """Test category code uniqueness constraint"""
        self.env['debt.category'].create({
            'name': 'Business Loan',
            'code': 'BL',
        })
        
        with self.assertRaises(Exception):  # Should raise integrity error
            self.env['debt.category'].create({
                'name': 'Bank Loan',
                'code': 'BL',  # Duplicate code
            })

    def test_category_hierarchy(self):
        """Test category parent-child relationship"""
        parent_category = self.env['debt.category'].create({
            'name': 'Loans',
            'code': 'LOAN',
        })
        
        child_category = self.env['debt.category'].create({
            'name': 'Business Loans',
            'code': 'BL',
            'parent_id': parent_category.id,
        })
        
        self.assertEqual(child_category.parent_id, parent_category)
        self.assertIn(child_category, parent_category.child_ids)

    def test_category_complete_name(self):
        """Test complete name computation"""
        parent_category = self.env['debt.category'].create({
            'name': 'Loans',
            'code': 'LOAN',
        })
        
        child_category = self.env['debt.category'].create({
            'name': 'Business Loans',
            'code': 'BL',
            'parent_id': parent_category.id,
        })
        
        child_category._compute_complete_name()
        self.assertEqual(child_category.complete_name, 'Loans / Business Loans')

    def test_category_recursion_check(self):
        """Test recursion prevention in category hierarchy"""
        category1 = self.env['debt.category'].create({
            'name': 'Category 1',
            'code': 'C1',
        })
        
        category2 = self.env['debt.category'].create({
            'name': 'Category 2',
            'code': 'C2',
            'parent_id': category1.id,
        })
        
        # Try to create recursion
        with self.assertRaises(ValidationError):
            category1.write({'parent_id': category2.id})

    def test_category_debt_statistics(self):
        """Test debt statistics computation"""
        category = self.env['debt.category'].create({
            'name': 'Test Category',
            'code': 'TC',
        })
        
        creditor = self.env['res.partner'].create({
            'name': 'Test Creditor',
            'is_company': True,
        })
        
        # Create test debt records
        debt1 = self.env['debt.record'].create({
            'creditor_id': creditor.id,
            'debt_category_id': category.id,
            'debt_amount': 5000.0,
            'interest_rate': 5.0,
            'start_date': '2024-01-01',
            'due_date': '2025-01-01',
        })
        
        debt2 = self.env['debt.record'].create({
            'creditor_id': creditor.id,
            'debt_category_id': category.id,
            'debt_amount': 3000.0,
            'interest_rate': 4.0,
            'start_date': '2024-01-01',
            'due_date': '2025-01-01',
        })
        
        # Statistics should be automatically updated when debts are created
        # Force refresh to ensure values are computed
        category.invalidate_cache()

        self.assertEqual(category.debt_count, 2)
        self.assertEqual(category.total_debt_amount, 8000.0)
        self.assertEqual(category.outstanding_debt_amount, 8000.0)
