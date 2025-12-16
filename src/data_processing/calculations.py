import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database.db_connection import get_sqlite_connection

class BusinessCalculations:
    def __init__(self):
        self.conn = get_sqlite_connection()
    
    def get_sales_summary(self, start_date=None, end_date=None):
        """Calculate sales summary metrics"""
        query = """
        SELECT 
            COUNT(*) as total_transactions,
            SUM(amount) as total_revenue,
            AVG(amount) as avg_transaction_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM sales
        """
        
        if start_date and end_date:
            query += f" WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        
        df = pd.read_sql_query(query, self.conn)
        return df.to_dict('records')[0]
    
    def get_top_products(self, limit=10):
        """Get top selling products"""
        query = f"""
        SELECT 
            p.name,
            p.category,
            SUM(s.quantity) as total_quantity,
            SUM(s.amount) as total_revenue,
            COUNT(*) as transactions
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.id
        ORDER BY total_revenue DESC
        LIMIT {limit}
        """
        
        return pd.read_sql_query(query, self.conn)
    
    def get_customer_segmentation(self):
        """Segment customers by value"""
        query = """
        SELECT 
            c.segment,
            COUNT(DISTINCT c.id) as customer_count,
            SUM(s.amount) as total_spent,
            AVG(s.amount) as avg_spent_per_customer,
            COUNT(s.id) as total_transactions
        FROM customers c
        LEFT JOIN sales s ON c.id = s.customer_id
        GROUP BY c.segment
        ORDER BY total_spent DESC
        """
        
        return pd.read_sql_query(query, self.conn)
    
    def get_sales_trend(self, period='monthly'):
        """Get sales trend over time"""
        if period == 'monthly':
            group_by = "strftime('%Y-%m', date)"
        elif period == 'weekly':
            group_by = "strftime('%Y-%W', date)"
        else:  # daily
            group_by = "date"
        
        query = f"""
        SELECT 
            {group_by} as period,
            SUM(amount) as revenue,
            COUNT(*) as transactions,
            AVG(amount) as avg_transaction
        FROM sales
        GROUP BY {group_by}
        ORDER BY period
        """
        
        return pd.read_sql_query(query, self.conn)
    
    def calculate_profit_margin(self):
        """Calculate profit margins by product category"""
        query = """
        SELECT 
            p.category,
            SUM(s.amount) as revenue,
            SUM(s.quantity * p.cost) as cost,
            (SUM(s.amount) - SUM(s.quantity * p.cost)) as profit,
            ((SUM(s.amount) - SUM(s.quantity * p.cost)) / SUM(s.amount)) * 100 as margin_percentage
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.category
        ORDER BY profit DESC
        """
        
        return pd.read_sql_query(query, self.conn)