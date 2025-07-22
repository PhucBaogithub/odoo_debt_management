# 💰 Debt Management Module for Odoo 16

A comprehensive debt management system for Odoo 16 that provides complete tracking and management of debt obligations, payments, and financial reporting.

**Author:** Phúc Bảo
**Contact:** baominecraft12344@gmail.com
**Repository:** https://github.com/PhucBaogithub/odoo_debt_management
**Version:** 16.0.1.0.0

## 🚀 Features

### Core Functionality
- **Comprehensive Debt Tracking** - Track all types of debts including loans, credit cards, mortgages, lines of credit, bonds, and more
- **Payment Management** - Record and track payments with detailed breakdowns of principal, interest, and fees
- **Automated Status Tracking** - Automatic detection of overdue debts and status updates
- **Multi-Currency Support** - Handle debts in different currencies
- **Priority System** - Set priorities to focus on critical debts

### Dashboard & Analytics
- **Interactive Dashboard** - Real-time statistics and charts showing debt status and trends
- **Visual Charts** - Pie charts, bar charts, and line graphs for debt analysis
- **Key Metrics** - Total debt, outstanding amounts, payment trends, and more
- **Quick Actions** - Easy access to create new debts and payments

### Reporting System
- **PDF Reports** - Professional debt reports with customizable layouts
- **Excel Export** - Detailed Excel reports with multiple worksheets
- **Report Types**:
  - Debt Summary Report
  - Detailed Debt Report
  - Payment History Report
  - Overdue Debts Report
  - Category Analysis Report

### Advanced Features
- **Category Management** - Organize debts by hierarchical categories
- **Automated Notifications** - Alerts for upcoming due dates and overdue debts
- **Payment Scheduling** - Track payment frequencies and next payment dates
- **Interest Rate Tracking** - Monitor interest rates and calculate costs
- **Security & Access Control** - Role-based permissions (User, Manager, Read-only)

### Multi-Language Support
- **English** - Full English translation
- **Vietnamese** - Complete Vietnamese translation
- **Extensible** - Easy to add more languages

## 📋 Requirements

- Odoo 16.0
- Python 3.8+
- xlsxwriter (for Excel reports)

## 🛠️ Installation

### Method 1: Clone from GitHub (Recommended)

1. **Clone the repository** to your Odoo addons directory:
   ```bash
   cd /path/to/odoo/addons/
   git clone https://github.com/PhucBaogithub/odoo_debt_management.git
   cd odoo_debt_management
   ```

2. **Copy the module** to addons directory:
   ```bash
   cp -r addons/debt_management /path/to/odoo/addons/
   ```

### Method 2: Download ZIP

1. **Download** the ZIP file from GitHub
2. **Extract** to your Odoo addons directory
3. **Copy** the `debt_management` folder to `/path/to/odoo/addons/`

### Installation Steps

1. **Restart Odoo server** to load the new module:
   ```bash
   # For Docker
   docker-compose restart

   # For systemd
   sudo systemctl restart odoo
   ```

2. **Update Apps List**:
   - Go to Apps menu in Odoo
   - Click "Update Apps List"
   - Search for "Debt Management"

3. **Install the module**:
   - Click "Install" on the Debt Management module
   - Wait for installation to complete

4. **Access the module**:
   - Look for "Debt Management" in the main menu
   - Or use direct URL: `http://your-odoo-url/web#action=debt_management.action_debt_record`

## 🎯 Usage Guide

### Getting Started

1. **Access the Module**:
   - Navigate to the "Debt Management" menu in Odoo main menu
   - Or use direct URL: `http://your-odoo-url/web#action=debt_management.action_debt_record`

2. **Quick Start (5 minutes)**:

   **Step 1:** Check pre-configured categories
   - Go to Configuration > Debt Categories
   - Default categories available: Business Loan, Credit Card, Mortgage, etc.

   **Step 2:** Create your first debt record
   - Go to Debt Records > All Debt Records
   - Click "Create"
   - Fill in: Creditor, Amount (e.g., 100000), Interest Rate (e.g., 5.5%), Dates
   - Click "Save" then "Activate"

   **Step 3:** Record a payment
   - From debt record, click "Payments" button
   - Click "Create"
   - Enter payment amount and date
   - Click "Confirm Payment"

   **Step 4:** View reports
   - Go to Reports > Generate Reports
   - Choose report type and format (PDF/Excel)
   - Click "Generate Report"

### Advanced Features

3. **Dashboard Overview**:
   - Real-time debt statistics
   - Payment trends and charts
   - Overdue debt alerts

4. **Payment Management**:
   - Automatic principal/interest breakdown
   - Multiple payment methods support
   - Payment history tracking

5. **Reporting System**:
   - PDF and Excel reports
   - Multiple report types (Summary, Detailed, Payment History, etc.)
   - Customizable filters and date ranges

### Dashboard Overview

The dashboard provides:
- **Total Debt Statistics** - Overview of all debt amounts
- **Status Breakdown** - Charts showing debt by status and category
- **Overdue Alerts** - List of overdue debts requiring attention
- **Upcoming Due Dates** - Debts due in the next 30 days
- **Recent Payments** - Latest payment activity
- **Payment Trends** - 12-month payment history chart

### Generating Reports

1. **Access Reports**:
   - Go to Reports > Generate Reports

2. **Select Report Type**:
   - Choose from Summary, Detailed, Payment History, Overdue, or Category Analysis

3. **Set Filters**:
   - Date range, categories, creditors, status filters
   - Choose PDF or Excel format

4. **Generate and Download**:
   - Click "Generate Report"
   - Download the generated file

## 🏗️ Module Structure

```
debt_management/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── debt_dashboard_controller.py
├── data/
│   └── debt_data.xml
├── demo/
│   └── debt_demo.xml
├── i18n/
│   └── vi.po
├── models/
│   ├── __init__.py
│   ├── debt_category.py
│   ├── debt_payment.py
│   └── debt_record.py
├── reports/
│   ├── debt_reports.xml
│   └── debt_report_templates.xml
├── security/
│   ├── debt_security.xml
│   └── ir.model.access.csv
├── static/
│   ├── description/
│   └── src/
│       ├── css/
│       ├── js/
│       └── xml/
├── tests/
│   ├── __init__.py
│   ├── test_debt_category.py
│   ├── test_debt_payment.py
│   └── test_debt_record.py
├── views/
│   ├── debt_dashboard_views.xml
│   ├── debt_menus.xml
│   └── debt_record_views.xml
└── wizards/
    ├── __init__.py
    ├── debt_report_wizard.py
    └── debt_report_wizard_views.xml
```

## 🔐 Security Groups

- **Debt User** - Can create and manage debt records and payments
- **Debt Manager** - Full access including configuration and deletion
- **Debt Read Only** - View-only access to all debt information

## 🧪 Testing

The module includes comprehensive tests:

```bash
# Run module tests
python3 -m pytest addons/debt_management/tests/
```

Or use the validation script:
```bash
python3 validate_module.py
```

## 📊 Database Models

### debt.record
Main debt tracking model with fields for creditor, amounts, dates, status, etc.

### debt.payment
Payment tracking model linked to debt records with principal/interest breakdown.

### debt.category
Hierarchical categorization system for organizing debts.

## 🎨 User Interface

- **Form Views** - User-friendly forms for data entry
- **List Views** - Sortable and filterable list displays
- **Kanban Views** - Visual card-based views grouped by status
- **Dashboard** - Interactive charts and statistics
- **Search Views** - Advanced filtering and grouping options

## 🔧 Customization

The module is designed to be easily customizable:

- **Add new debt types** - Extend the debt_type selection field
- **Custom reports** - Create new report templates
- **Additional fields** - Extend models with custom fields
- **Workflow modifications** - Customize state transitions
- **New translations** - Add support for additional languages

## 📝 Changelog

### Version 16.0.1.0.0
- Initial release
- Complete debt management functionality
- Dashboard with charts and statistics
- PDF and Excel reporting
- Multi-language support (EN/VI)
- Comprehensive test suite

## 🆘 Troubleshooting

### Common Issues

**Issue: "Access Error" when trying to access**
- Solution: Update the module after installation
- Go to Apps > Debt Management > Upgrade

**Issue: Menu not visible**
- Solution: Clear browser cache and refresh
- Or use direct URL: `http://your-odoo-url/web#action=debt_management.action_debt_record`

**Issue: Cannot create debt records**
- Solution: Ensure you have "Internal User" access rights
- Check that creditors are set up as companies in Contacts

### Getting Help

For support, bug reports, or feature requests:
1. **Email:** baominecraft12344@gmail.com
2. **GitHub Issues:** https://github.com/PhucBaogithub/odoo_debt_management/issues
3. **Documentation:** Check this README and module help texts

## 🔄 Updates and Contributions

- **Latest Version:** Check GitHub for updates
- **Contributions:** Pull requests welcome
- **Bug Reports:** Use GitHub Issues

## 📄 License

This module is licensed under LGPL-3.

## 👥 Credits

**Developer:** Phúc Bảo
**Email:** baominecraft12344@gmail.com
**GitHub:** https://github.com/PhucBaogithub
**Repository:** https://github.com/PhucBaogithub/odoo_debt_management

Developed for Odoo 16 Community.

---

**Note**: This module follows Odoo's standard conventions and best practices for module development, ensuring compatibility and maintainability.
