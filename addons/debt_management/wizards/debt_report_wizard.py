# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import xlsxwriter
from datetime import datetime, timedelta


class DebtReportWizard(models.TransientModel):
    _name = 'debt.report.wizard'
    _description = 'Debt Report Wizard'

    report_type = fields.Selection([
        ('summary', 'Debt Summary Report'),
        ('detailed', 'Detailed Debt Report'),
        ('payment_history', 'Payment History Report'),
        ('overdue', 'Overdue Debts Report'),
        ('category_analysis', 'Category Analysis Report')
    ], string='Report Type', required=True, default='summary')

    output_format = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel')
    ], string='Output Format', required=True, default='pdf')

    date_from = fields.Date(
        string='Date From',
        default=lambda self: fields.Date.today().replace(day=1)
    )
    
    date_to = fields.Date(
        string='Date To',
        default=fields.Date.today
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    debt_category_ids = fields.Many2many(
        'debt.category',
        string='Debt Categories',
        help='Leave empty to include all categories'
    )

    creditor_ids = fields.Many2many(
        'res.partner',
        string='Creditors',
        domain=[('is_company', '=', True)],
        help='Leave empty to include all creditors'
    )

    state_filter = fields.Selection([
        ('all', 'All States'),
        ('active', 'Active Only'),
        ('overdue', 'Overdue Only'),
        ('paid', 'Paid Only')
    ], string='Status Filter', default='all')

    include_payments = fields.Boolean(
        string='Include Payment Details',
        default=True,
        help='Include payment history in the report'
    )

    group_by = fields.Selection([
        ('category', 'Group by Category'),
        ('creditor', 'Group by Creditor'),
        ('status', 'Group by Status'),
        ('none', 'No Grouping')
    ], string='Group By', default='category')

    def action_generate_report(self):
        """Generate the selected report"""
        self.ensure_one()
        
        if self.output_format == 'pdf':
            return self._generate_pdf_report()
        else:
            return self._generate_excel_report()

    def _get_debt_domain(self):
        """Build domain for debt records based on wizard filters"""
        domain = [('company_id', '=', self.company_id.id)]
        
        if self.date_from:
            domain.append(('start_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('start_date', '<=', self.date_to))
        
        if self.debt_category_ids:
            domain.append(('debt_category_id', 'in', self.debt_category_ids.ids))
        
        if self.creditor_ids:
            domain.append(('creditor_id', 'in', self.creditor_ids.ids))
        
        if self.state_filter != 'all':
            domain.append(('state', '=', self.state_filter))
        
        return domain

    def _generate_pdf_report(self):
        """Generate PDF report"""
        domain = self._get_debt_domain()
        debt_records = self.env['debt.record'].search(domain)
        
        if not debt_records:
            raise UserError(_('No debt records found for the selected criteria.'))
        
        data = {
            'wizard_id': self.id,
            'debt_ids': debt_records.ids,
            'report_type': self.report_type,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'include_payments': self.include_payments,
            'group_by': self.group_by,
        }
        
        return self.env.ref('debt_management.action_debt_report_pdf').report_action(self, data=data)

    def _generate_excel_report(self):
        """Generate Excel report"""
        domain = self._get_debt_domain()
        debt_records = self.env['debt.record'].search(domain)
        
        if not debt_records:
            raise UserError(_('No debt records found for the selected criteria.'))
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1,
            'align': 'center'
        })
        
        currency_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1
        })
        
        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'border': 1
        })
        
        cell_format = workbook.add_format({'border': 1})
        
        # Create worksheets based on report type
        if self.report_type == 'summary':
            self._create_summary_sheet(workbook, debt_records, header_format, currency_format, cell_format)
        elif self.report_type == 'detailed':
            self._create_detailed_sheet(workbook, debt_records, header_format, currency_format, date_format, cell_format)
        elif self.report_type == 'payment_history':
            self._create_payment_history_sheet(workbook, debt_records, header_format, currency_format, date_format, cell_format)
        elif self.report_type == 'overdue':
            overdue_debts = debt_records.filtered(lambda r: r.state == 'overdue')
            self._create_overdue_sheet(workbook, overdue_debts, header_format, currency_format, date_format, cell_format)
        elif self.report_type == 'category_analysis':
            self._create_category_analysis_sheet(workbook, debt_records, header_format, currency_format, cell_format)
        
        workbook.close()
        output.seek(0)
        
        # Create attachment
        filename = f"debt_report_{self.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def _create_summary_sheet(self, workbook, debt_records, header_format, currency_format, cell_format):
        """Create summary worksheet"""
        worksheet = workbook.add_worksheet('Debt Summary')
        
        # Headers
        headers = ['Category', 'Count', 'Total Debt', 'Outstanding', 'Paid Amount', 'Avg Interest Rate']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Group by category
        categories = debt_records.mapped('debt_category_id')
        row = 1
        
        for category in categories:
            category_debts = debt_records.filtered(lambda r: r.debt_category_id == category)
            
            worksheet.write(row, 0, category.name, cell_format)
            worksheet.write(row, 1, len(category_debts), cell_format)
            worksheet.write(row, 2, sum(category_debts.mapped('debt_amount')), currency_format)
            worksheet.write(row, 3, sum(category_debts.mapped('outstanding_amount')), currency_format)
            worksheet.write(row, 4, sum(category_debts.mapped('paid_amount')), currency_format)
            
            avg_rate = sum(category_debts.mapped('interest_rate')) / len(category_debts) if category_debts else 0
            worksheet.write(row, 5, f"{avg_rate:.2f}%", cell_format)
            
            row += 1
        
        # Totals
        worksheet.write(row + 1, 0, 'TOTAL', header_format)
        worksheet.write(row + 1, 1, len(debt_records), header_format)
        worksheet.write(row + 1, 2, sum(debt_records.mapped('debt_amount')), currency_format)
        worksheet.write(row + 1, 3, sum(debt_records.mapped('outstanding_amount')), currency_format)
        worksheet.write(row + 1, 4, sum(debt_records.mapped('paid_amount')), currency_format)
        
        # Auto-adjust column widths
        worksheet.set_column('A:F', 15)

    def _create_detailed_sheet(self, workbook, debt_records, header_format, currency_format, date_format, cell_format):
        """Create detailed worksheet"""
        worksheet = workbook.add_worksheet('Detailed Report')
        
        # Headers
        headers = ['Reference', 'Creditor', 'Category', 'Debt Amount', 'Outstanding', 'Paid', 
                  'Interest Rate', 'Start Date', 'Due Date', 'Status', 'Priority']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data rows
        for row, debt in enumerate(debt_records, 1):
            worksheet.write(row, 0, debt.debt_reference, cell_format)
            worksheet.write(row, 1, debt.creditor_id.name, cell_format)
            worksheet.write(row, 2, debt.debt_category_id.name, cell_format)
            worksheet.write(row, 3, debt.debt_amount, currency_format)
            worksheet.write(row, 4, debt.outstanding_amount, currency_format)
            worksheet.write(row, 5, debt.paid_amount, currency_format)
            worksheet.write(row, 6, f"{debt.interest_rate}%", cell_format)
            worksheet.write(row, 7, debt.start_date, date_format)
            worksheet.write(row, 8, debt.due_date, date_format)
            worksheet.write(row, 9, debt.state.title(), cell_format)
            
            priority_map = {'0': 'Low', '1': 'Normal', '2': 'High', '3': 'Very High'}
            worksheet.write(row, 10, priority_map.get(debt.priority, 'Normal'), cell_format)
        
        # Auto-adjust column widths
        worksheet.set_column('A:K', 12)

    def _create_payment_history_sheet(self, workbook, debt_records, header_format, currency_format, date_format, cell_format):
        """Create payment history worksheet"""
        worksheet = workbook.add_worksheet('Payment History')
        
        # Headers
        headers = ['Payment Ref', 'Debt Ref', 'Creditor', 'Payment Date', 'Amount', 
                  'Principal', 'Interest', 'Fee', 'Payment Type', 'Method', 'Status']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Get all payments for the debt records
        payments = self.env['debt.payment'].search([
            ('debt_record_id', 'in', debt_records.ids)
        ], order='payment_date desc')
        
        # Data rows
        for row, payment in enumerate(payments, 1):
            worksheet.write(row, 0, payment.payment_reference, cell_format)
            worksheet.write(row, 1, payment.debt_record_id.debt_reference, cell_format)
            worksheet.write(row, 2, payment.creditor_id.name, cell_format)
            worksheet.write(row, 3, payment.payment_date, date_format)
            worksheet.write(row, 4, payment.amount, currency_format)
            worksheet.write(row, 5, payment.principal_amount or 0, currency_format)
            worksheet.write(row, 6, payment.interest_amount or 0, currency_format)
            worksheet.write(row, 7, payment.fee_amount or 0, currency_format)
            worksheet.write(row, 8, payment.payment_type.title(), cell_format)
            worksheet.write(row, 9, payment.payment_method.title(), cell_format)
            worksheet.write(row, 10, payment.state.title(), cell_format)
        
        # Auto-adjust column widths
        worksheet.set_column('A:K', 12)

    def _create_overdue_sheet(self, workbook, overdue_debts, header_format, currency_format, date_format, cell_format):
        """Create overdue debts worksheet"""
        worksheet = workbook.add_worksheet('Overdue Debts')
        
        # Headers
        headers = ['Reference', 'Creditor', 'Outstanding Amount', 'Due Date', 'Days Overdue', 'Priority']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data rows
        for row, debt in enumerate(overdue_debts, 1):
            worksheet.write(row, 0, debt.debt_reference, cell_format)
            worksheet.write(row, 1, debt.creditor_id.name, cell_format)
            worksheet.write(row, 2, debt.outstanding_amount, currency_format)
            worksheet.write(row, 3, debt.due_date, date_format)
            worksheet.write(row, 4, debt.days_overdue, cell_format)
            
            priority_map = {'0': 'Low', '1': 'Normal', '2': 'High', '3': 'Very High'}
            worksheet.write(row, 5, priority_map.get(debt.priority, 'Normal'), cell_format)
        
        # Auto-adjust column widths
        worksheet.set_column('A:F', 15)

    def _create_category_analysis_sheet(self, workbook, debt_records, header_format, currency_format, cell_format):
        """Create category analysis worksheet"""
        worksheet = workbook.add_worksheet('Category Analysis')
        
        # Headers
        headers = ['Category', 'Total Debts', 'Active', 'Overdue', 'Paid', 'Total Amount', 'Outstanding', 'Percentage']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Calculate totals
        total_outstanding = sum(debt_records.mapped('outstanding_amount'))
        
        # Group by category
        categories = debt_records.mapped('debt_category_id')
        row = 1
        
        for category in categories:
            category_debts = debt_records.filtered(lambda r: r.debt_category_id == category)
            category_outstanding = sum(category_debts.mapped('outstanding_amount'))
            
            worksheet.write(row, 0, category.name, cell_format)
            worksheet.write(row, 1, len(category_debts), cell_format)
            worksheet.write(row, 2, len(category_debts.filtered(lambda r: r.state == 'active')), cell_format)
            worksheet.write(row, 3, len(category_debts.filtered(lambda r: r.state == 'overdue')), cell_format)
            worksheet.write(row, 4, len(category_debts.filtered(lambda r: r.state == 'paid')), cell_format)
            worksheet.write(row, 5, sum(category_debts.mapped('debt_amount')), currency_format)
            worksheet.write(row, 6, category_outstanding, currency_format)
            
            percentage = (category_outstanding / total_outstanding * 100) if total_outstanding else 0
            worksheet.write(row, 7, f"{percentage:.1f}%", cell_format)
            
            row += 1
        
        # Auto-adjust column widths
        worksheet.set_column('A:H', 12)
