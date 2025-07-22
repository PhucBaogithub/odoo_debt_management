# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class DebtDashboardController(http.Controller):

    @http.route('/debt_management/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self):
        """Get dashboard data for debt management"""
        
        # Get current user's company
        company_id = request.env.company.id
        currency = request.env.company.currency_id
        
        # Base domain for company filtering
        domain = [('company_id', '=', company_id)]
        
        # Get debt statistics
        debt_records = request.env['debt.record'].search(domain)
        
        # Calculate totals
        total_debt = sum(debt_records.mapped('debt_amount'))
        total_outstanding = sum(debt_records.mapped('outstanding_amount'))
        total_paid = sum(debt_records.mapped('paid_amount'))
        
        # Get status breakdown
        status_data = []
        for state in ['draft', 'active', 'overdue', 'paid', 'cancelled']:
            count = len(debt_records.filtered(lambda r: r.state == state))
            amount = sum(debt_records.filtered(lambda r: r.state == state).mapped('outstanding_amount'))
            if count > 0:
                status_data.append({
                    'status': state.title(),
                    'count': count,
                    'amount': amount,
                    'formatted_amount': f"{currency.symbol}{amount:,.2f}"
                })
        
        # Get category breakdown
        categories = request.env['debt.category'].search([])
        category_data = []
        for category in categories:
            category_debts = debt_records.filtered(lambda r: r.debt_category_id.id == category.id)
            if category_debts:
                outstanding = sum(category_debts.mapped('outstanding_amount'))
                category_data.append({
                    'category': category.name,
                    'count': len(category_debts),
                    'amount': outstanding,
                    'formatted_amount': f"{currency.symbol}{outstanding:,.2f}"
                })
        
        # Sort by amount descending
        category_data.sort(key=lambda x: x['amount'], reverse=True)
        
        # Get overdue debts
        overdue_debts = debt_records.filtered(lambda r: r.state == 'overdue')
        overdue_data = []
        for debt in overdue_debts:
            overdue_data.append({
                'reference': debt.debt_reference,
                'creditor': debt.creditor_id.name,
                'amount': debt.outstanding_amount,
                'formatted_amount': f"{currency.symbol}{debt.outstanding_amount:,.2f}",
                'days_overdue': debt.days_overdue,
                'due_date': debt.due_date.strftime('%Y-%m-%d') if debt.due_date else '',
            })
        
        # Get upcoming due dates (next 30 days)
        today = fields.Date.context_today(request.env.user)
        next_month = today + timedelta(days=30)
        upcoming_debts = debt_records.filtered(
            lambda r: r.due_date and today <= r.due_date <= next_month and r.state in ['active', 'overdue']
        )
        upcoming_data = []
        for debt in upcoming_debts:
            upcoming_data.append({
                'reference': debt.debt_reference,
                'creditor': debt.creditor_id.name,
                'amount': debt.outstanding_amount,
                'formatted_amount': f"{currency.symbol}{debt.outstanding_amount:,.2f}",
                'due_date': debt.due_date.strftime('%Y-%m-%d'),
                'days_until_due': (debt.due_date - today).days,
            })
        
        # Sort by due date
        upcoming_data.sort(key=lambda x: x['due_date'])
        
        # Get recent payments (last 30 days)
        recent_date = today - timedelta(days=30)
        recent_payments = request.env['debt.payment'].search([
            ('company_id', '=', company_id),
            ('payment_date', '>=', recent_date),
            ('state', '=', 'confirmed')
        ], order='payment_date desc', limit=10)
        
        payment_data = []
        for payment in recent_payments:
            payment_data.append({
                'reference': payment.payment_reference,
                'debt_reference': payment.debt_record_id.debt_reference,
                'creditor': payment.creditor_id.name,
                'amount': payment.amount,
                'formatted_amount': f"{currency.symbol}{payment.amount:,.2f}",
                'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                'payment_type': payment.payment_type,
            })
        
        # Get monthly payment trends (last 12 months)
        monthly_data = []
        for i in range(12):
            month_start = today.replace(day=1) - relativedelta(months=i)
            month_end = month_start + relativedelta(months=1) - timedelta(days=1)
            
            month_payments = request.env['debt.payment'].search([
                ('company_id', '=', company_id),
                ('payment_date', '>=', month_start),
                ('payment_date', '<=', month_end),
                ('state', '=', 'confirmed')
            ])
            
            total_amount = sum(month_payments.mapped('amount'))
            monthly_data.append({
                'month': month_start.strftime('%Y-%m'),
                'month_name': month_start.strftime('%B %Y'),
                'amount': total_amount,
                'formatted_amount': f"{currency.symbol}{total_amount:,.2f}",
                'count': len(month_payments)
            })
        
        # Reverse to show oldest to newest
        monthly_data.reverse()
        
        return {
            'currency_symbol': currency.symbol,
            'totals': {
                'total_debt': total_debt,
                'total_outstanding': total_outstanding,
                'total_paid': total_paid,
                'formatted_total_debt': f"{currency.symbol}{total_debt:,.2f}",
                'formatted_total_outstanding': f"{currency.symbol}{total_outstanding:,.2f}",
                'formatted_total_paid': f"{currency.symbol}{total_paid:,.2f}",
            },
            'status_breakdown': status_data,
            'category_breakdown': category_data,
            'overdue_debts': overdue_data,
            'upcoming_debts': upcoming_data,
            'recent_payments': payment_data,
            'monthly_trends': monthly_data,
            'counts': {
                'total_debts': len(debt_records),
                'active_debts': len(debt_records.filtered(lambda r: r.state == 'active')),
                'overdue_debts': len(overdue_debts),
                'paid_debts': len(debt_records.filtered(lambda r: r.state == 'paid')),
            }
        }

    @http.route('/debt_management/chart_data/<string:chart_type>', type='json', auth='user')
    def get_chart_data(self, chart_type):
        """Get specific chart data"""
        
        company_id = request.env.company.id
        domain = [('company_id', '=', company_id)]
        
        if chart_type == 'category_pie':
            # Category breakdown pie chart
            debt_records = request.env['debt.record'].search(domain + [('state', 'in', ['active', 'overdue'])])
            categories = {}
            
            for debt in debt_records:
                category_name = debt.debt_category_id.name
                if category_name not in categories:
                    categories[category_name] = 0
                categories[category_name] += debt.outstanding_amount
            
            return {
                'labels': list(categories.keys()),
                'data': list(categories.values()),
                'type': 'pie'
            }
        
        elif chart_type == 'status_bar':
            # Status breakdown bar chart
            debt_records = request.env['debt.record'].search(domain)
            statuses = {}
            
            for debt in debt_records:
                status = debt.state.title()
                if status not in statuses:
                    statuses[status] = 0
                statuses[status] += debt.outstanding_amount
            
            return {
                'labels': list(statuses.keys()),
                'data': list(statuses.values()),
                'type': 'bar'
            }
        
        elif chart_type == 'payment_trend':
            # Payment trend line chart
            today = fields.Date.context_today(request.env.user)
            monthly_data = []
            labels = []
            
            for i in range(12):
                month_start = today.replace(day=1) - relativedelta(months=11-i)
                month_end = month_start + relativedelta(months=1) - timedelta(days=1)
                
                month_payments = request.env['debt.payment'].search([
                    ('company_id', '=', company_id),
                    ('payment_date', '>=', month_start),
                    ('payment_date', '<=', month_end),
                    ('state', '=', 'confirmed')
                ])
                
                total_amount = sum(month_payments.mapped('amount'))
                monthly_data.append(total_amount)
                labels.append(month_start.strftime('%b %Y'))
            
            return {
                'labels': labels,
                'data': monthly_data,
                'type': 'line'
            }
        
        return {'error': 'Invalid chart type'}
