"""
Thread-safe database operations for UI components
"""

import sqlite3
import threading
import pandas as pd
from queue import Queue

class ThreadSafeDB:
    """Thread-safe database operations"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThreadSafeDB, cls).__new__(cls)
        return cls._instance
    
    def get_connection(self):
        """Get a new connection for the current thread"""
        import os
        db_path = os.path.join(os.path.dirname(__file__), '../../data/database/business.db')
        return sqlite3.connect(db_path)
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        conn = self.get_connection()
        try:
            if params:
                result = pd.read_sql_query(query, conn, params=params)
            else:
                result = pd.read_sql_query(query, conn)
            return result
        finally:
            conn.close()
    
    def get_sales_summary(self):
        """Get sales summary - thread-safe"""
        query = """
        SELECT 
            COUNT(*) as total_transactions,
            SUM(amount) as total_revenue,
            AVG(amount) as avg_transaction_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM sales
        """
        return self.execute_query(query)
    
    def get_top_products(self, limit=10):
        """Get top products - thread-safe"""
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
        return self.execute_query(query)


# Helper function for UI components
def run_db_query_in_thread(query_func, callback, *args):
    """Run database query in thread and call callback with result"""
    def worker():
        try:
            db = ThreadSafeDB()
            result = query_func(db, *args)
            callback(result)
        except Exception as e:
            print(f"Database query error: {e}")
            callback(None)
    
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()