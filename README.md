# Odoo Debt Management Module

A comprehensive debt management system for Odoo 16 that provides complete tracking and management of debt obligations, payments, and financial reporting.

![Odoo Version](https://img.shields.io/badge/Odoo-16.0-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)

**Author:** Phúc Bảo  
**Contact:** baominecraft12344@gmail.com  
**Repository:** https://github.com/PhucBaogithub/odoo_debt_management  

## Table of Contents

- [Features](#-features)
- [Installation](#️-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

## Features

### Core Functionality
-  **Comprehensive Debt Tracking** - Track all types of debts (loans, credit cards, mortgages, etc.)
-  **Payment Management** - Record payments with automatic principal/interest breakdown
-  **Automated Status Tracking** - Automatic overdue detection and status updates
-  **Multi-Currency Support** - Handle debts in different currencies
-  **Priority System** - Set priorities to focus on critical debts

### Dashboard & Analytics
-  **Interactive Dashboard** - Real-time statistics and charts
-  **Visual Charts** - Pie charts, bar charts, and line graphs
-  **Key Metrics** - Total debt, outstanding amounts, payment trends
-  **Quick Actions** - Easy access to create new debts and payments

### Reporting System
-  **PDF Reports** - Professional debt reports with customizable layouts
-  **Excel Export** - Detailed Excel reports with multiple worksheets
-  **Multiple Report Types** - Summary, Detailed, Payment History, Overdue, Category Analysis

### Advanced Features
-  **Category Management** - Organize debts by hierarchical categories
-  **Payment Scheduling** - Track payment frequencies and next payment dates
-  **Interest Rate Tracking** - Monitor interest rates and calculate costs
-  **Security & Access Control** - Role-based permissions
-  **Multi-Language Support** - English and Vietnamese translations

## Installation

### Prerequisites
- Odoo 16.0
- Python 3.8+
- PostgreSQL database

### Method 1: Clone from GitHub (Recommended)

```bash
# Navigate to your Odoo addons directory
cd /path/to/odoo/addons/

# Clone the repository
git clone https://github.com/PhucBaogithub/odoo_debt_management.git

# Copy the module to addons directory
cp -r odoo_debt_management/addons/debt_management ./
```

### Method 2: Download ZIP

1. Download the ZIP file from GitHub
2. Extract to your Odoo addons directory
3. Copy the `debt_management` folder to `/path/to/odoo/addons/`

### Installation Steps

1. **Restart Odoo server**:
   ```bash
   # For Docker
   docker-compose restart
   
   # For systemd
   sudo systemctl restart odoo
   ```

2. **Update Apps List**:
   - Go to Apps menu in Odoo
   - Click "Update Apps List"

3. **Install the module**:
   - Search for "Debt Management"
   - Click "Install"

4. **Access the module**:
   - Look for "Debt Management" in the main menu
   - Or use direct URL: `http://your-odoo-url/web#action=debt_management.action_debt_record`

## Quick Start

### 5-Minute Setup

1. **Check Categories** (Pre-configured):
   - Business Loan, Credit Card, Mortgage, Equipment Loan, etc.

2. **Create First Debt Record**:
   - Go to Debt Records > All Debt Records
   - Click "Create"
   - Fill: Creditor, Amount (100000), Interest Rate (5.5%), Dates
   - Save and Activate

3. **Record Payment**:
   - From debt record, click "Payments"
   - Create new payment
   - Enter amount and confirm

4. **View Reports**:
   - Go to Reports > Generate Reports
   - Choose type and format
   - Generate and download

## Usage Guide

### Main Menu Structure
```
 Debt Management
├──  Dashboard
├──  Debt Records
│   ├── All Debt Records
│   ├── Active Debts
│   ├── Overdue Debts
│   └── High Priority
├──  Payments
├──  Analysis
├──  Reports
└──  Configuration
```

### Creating Debt Records
1. Navigate to Debt Records > All Debt Records
2. Click "Create"
3. Fill required fields:
   - **Creditor/Lender**: Select or create creditor
   - **Debt Amount**: Original debt amount
   - **Interest Rate**: Annual percentage rate
   - **Start Date & Due Date**: Debt timeline
   - **Category**: Type of debt
4. Save and Activate

### Recording Payments
1. From debt record, click "Payments" button
2. Click "Create"
3. Enter payment details:
   - Amount, Date, Method
   - System auto-calculates principal/interest split
4. Confirm payment

### Generating Reports
1. Go to Reports > Generate Reports
2. Select report type and filters
3. Choose PDF or Excel format
4. Generate and download

## Troubleshooting

### Common Issues

**Access Error when opening module**
```bash
# Solution: Update module after installation
Apps > Debt Management > Upgrade
```

**Menu not visible**
```bash
# Solution: Clear cache and refresh
# Or use direct URL
http://your-odoo-url/web#action=debt_management.action_debt_record
```

**Cannot create debt records**
- Ensure user has "Internal User" access rights
- Check creditors are set up as companies

### Getting Help
- **Email**: baominecraft12344@gmail.com
- **GitHub Issues**: [Report Issues](https://github.com/PhucBaogithub/odoo_debt_management/issues)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the LGPL-3 License.

## Contact

**Phúc Bảo**
- Email: baominecraft12344@gmail.com
- GitHub: [@PhucBaogithub](https://github.com/PhucBaogithub)
- Repository: [odoo_debt_management](https://github.com/PhucBaogithub/odoo_debt_management)

---

 **If you find this project helpful, please give it a star!**

## Changelog

### Version 16.0.1.0.0
- Initial release
- Complete debt management functionality
- Dashboard with charts and statistics
- PDF and Excel reporting
- Multi-language support (EN/VI)
- Comprehensive test suite

---

*Made with love for the Odoo Community*
