import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from database.db_connection import get_sqlite_connection
from data_processing.calculations import BusinessCalculations

class TestBusinessIntelligenceSystem(unittest.TestCase):
    
    def setUp(self):
        self.conn = get_sqlite_connection()
        self.calculator = BusinessCalculations()
    
    def test_database_connection(self):
        """Test database connection"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        self.assertGreater(len(tables), 0, "Database should have tables")
    
    def test_sales_summary(self):
        """Test sales summary calculation"""
        summary = self.calculator.get_sales_summary()
        self.assertIn('total_revenue', summary)
        self.assertIsInstance(summary['total_revenue'], (int, float))
    
    def test_top_products(self):
        """Test top products calculation"""
        top_products = self.calculator.get_top_products(5)
        self.assertLessEqual(len(top_products), 5)
        if len(top_products) > 0:
            self.assertIn('name', top_products.columns)
            self.assertIn('total_revenue', top_products.columns)
    
    def tearDown(self):
        self.conn.close()

if __name__ == '__main__':
    unittest.main()