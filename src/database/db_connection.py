import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data/database/business.db')

def create_database():
    """Create database and tables if they don't exist"""
    from .models import Base
    
    engine = create_engine(f'sqlite:///{DB_PATH}')
    Base.metadata.create_all(engine)
    
    # Create indexes for better performance
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
    
    return engine

def get_session():
    """Get database session"""
    engine = create_database()
    Session = sessionmaker(bind=engine)
    return Session()

def get_sqlite_connection():
    """Get raw SQLite connection for direct SQL queries"""
    return sqlite3.connect(DB_PATH)