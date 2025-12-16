import sys
import os
sys.path.append('src')

def test_ui_components():
    """Test UI components without opening full window"""
    print("=" * 50)
    print("UI COMPONENT TESTING")
    print("=" * 50)
    
    import tkinter as tk
    from tkinter import ttk
    
    # Create a test window
    test_root = tk.Tk()
    test_root.withdraw()  # Don't show the window
    
    # Test 1: Check if all UI modules can be imported
    print("\n1. Testing UI module imports...")
    ui_modules = [
        'ui.dashboard',
        'ui.data_entry',
        'ui.reports',
        'visualization.dashboard_widgets'
    ]
    
    for module_name in ui_modules:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name}: Import successful")
        except Exception as e:
            print(f"  ✗ {module_name}: Import failed - {e}")
    
    # Test 2: Test dashboard widget creation
    print("\n2. Testing dashboard widget creation...")
    try:
        from ui.dashboard import Dashboard
        test_frame = ttk.Frame(test_root)
        dashboard = Dashboard(test_frame, {})
        print("  ✓ Dashboard widget created successfully")
    except Exception as e:
        print(f"  ✗ Dashboard creation failed: {e}")
    
    # Test 3: Test visualization
    print("\n3. Testing visualization components...")
    try:
        import matplotlib.pyplot as plt
        from database.db_connection import get_sqlite_connection
        import pandas as pd
        
        conn = get_sqlite_connection()
        
        # Test basic chart creation
        fig, ax = plt.subplots(figsize=(8, 4))
        df = pd.read_sql_query("SELECT strftime('%Y-%m', date) as month, SUM(amount) as revenue FROM sales GROUP BY month", conn)
        
        if not df.empty:
            ax.plot(df['month'], df['revenue'])
            ax.set_title('Test Chart')
            plt.close(fig)
            print("  ✓ Chart creation successful")
        else:
            print("  ✗ No data for chart")
        
        conn.close()
    except Exception as e:
        print(f"  ✗ Visualization test failed: {e}")
    
    # Test 4: Test report generation
    print("\n4. Testing report generation...")
    try:
        from ui.reports import Reports
        test_frame = ttk.Frame(test_root)
        reports = Reports(test_frame, {})
        print("  ✓ Reports module initialized")
        
        # Test data frame generation
        from database.db_connection import get_sqlite_connection
        conn = get_sqlite_connection()
        df = pd.read_sql_query("SELECT * FROM sales LIMIT 5", conn)
        print(f"  ✓ Sample report data: {len(df)} rows")
        conn.close()
        
    except Exception as e:
        print(f"  ✗ Report generation test failed: {e}")
    
    test_root.destroy()
    
    print("\n" + "=" * 50)
    print("UI COMPONENT TESTS: COMPLETED")
    print("=" * 50)
    return True

if __name__ == "__main__":
    test_ui_components()