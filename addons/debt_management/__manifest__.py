# -*- coding: utf-8 -*-
{
    'name': 'Debt Management',
    'version': '16.0.1.0.0',
    'category': 'Accounting/Finance',
    'summary': 'Comprehensive debt and investment management system',
    'description': """
        Debt Management Module
        ======================
        
        This module provides comprehensive debt management functionality including:
        
        * Debt tracking and monitoring
        * Interest rate calculations
        * Payment schedules and due date management
        * Debt categorization and status tracking
        * Interactive dashboard with statistics and charts
        * Automated notifications for due dates
        * Comprehensive reporting (PDF/Excel)
        * Multi-language support (English/Vietnamese)
        
        Features:
        ---------
        * Create and manage debt records
        * Track creditors and debt amounts
        * Monitor interest rates and payment schedules
        * Categorize debts by type
        * Real-time debt statistics dashboard
        * Overdue debt tracking
        * Payment reminders and notifications
        * Export reports in multiple formats
        
        This module is designed for businesses and individuals who need to track
        and manage their debt obligations effectively.
    """,
    'author': 'Phúc Bảo',
    'maintainer': 'Phúc Bảo',
    'website': 'https://github.com/PhucBaogithub/odoo_debt_management',
    'support': 'baominecraft12344@gmail.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
        'account',
        'contacts',
    ],
    'data': [
        # Security
        'security/debt_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/debt_data.xml',
        
        # Views
        'views/debt_record_views.xml',
        'views/debt_dashboard_views.xml',
        'views/debt_menus.xml',
        
        # Reports
        'reports/debt_reports.xml',
        'reports/debt_report_templates.xml',
        
        # Wizards
        'wizards/debt_report_wizard_views.xml',
    ],
    'demo': [
        'demo/debt_demo.xml',
    ],

    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
}
