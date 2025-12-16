import sys
import os
sys.path.append('src')

def test_database():
    """Test database creation and operations"""
    print("=" * 50)
    print("DATABASE TESTING")
    print("=" * 50)
    
    from database.db_connection import get_sqlite_connection, create_database
    
    # Test 1: Database creation
    print("\n1. Testing database creation...")
    try:
        create_database()
        print("✓ Database created successfully")
    except Exception as e:
        print(f"✗ Database creation failed: {e}")
        return False
    
    # Test 2: Database connection
    print("\n2. Testing database connection...")
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        required_tables = ['products', 'customers', 'sales', 'employees', 'inventory']
        missing_tables = [t for t in required_tables if t not in table_names]
        
        if missing_tables:
            print(f"✗ Missing tables: {missing_tables}")
            return False
        else:
            print(f"✓ All tables exist: {table_names}")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    
    # Test 3: Data count
    print("\n3. Testing data counts...")
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        for table in required_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")
        
        # Check if sales data has records
        cursor.execute("SELECT COUNT(*) FROM sales;")
        sales_count = cursor.fetchone()[0]
        if sales_count > 0:
            print(f"✓ Sales data loaded: {sales_count} records")
        else:
            print("✗ No sales data found")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Data count test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("DATABASE TESTS: ALL PASSED ✓")
    print("=" * 50)
    return True

if __name__ == "__main__":
    test_database()