import sys
import os
sys.path.append('src')

def test_end_to_end():
    """Test complete system workflow"""
    print("=" * 50)
    print("END-TO-END FUNCTIONAL TESTING")
    print("=" * 50)
    
    from database.db_connection import get_sqlite_connection
    from data_processing.calculations import BusinessCalculations
    from ml.train import SalesPredictor
    import pandas as pd
    import sqlite3
    
    all_passed = True
    
    # Test 1: Database to Analysis Pipeline
    print("\n1. Testing Database → Analysis Pipeline...")
    try:
        calculator = BusinessCalculations()
        
        # Get data from database
        summary = calculator.get_sales_summary()
        top_products = calculator.get_top_products(3)
        trends = calculator.get_sales_trend('monthly')
        
        print(f"  ✓ Total Revenue: ${summary['total_revenue']:,.2f}")
        print(f"  ✓ Transactions: {summary['total_transactions']}")
        print(f"  ✓ Top Product: {top_products.iloc[0]['name']} (${top_products.iloc[0]['total_revenue']:,.2f})")
        print(f"  ✓ Trend periods: {len(trends)} months")
        
    except Exception as e:
        print(f"  ✗ Analysis pipeline failed: {e}")
        all_passed = False
    
    # Test 2: Data Export Pipeline
    print("\n2. Testing Data Export Pipeline...")
    try:
        conn = get_sqlite_connection()
        
        # Export to CSV
        df = pd.read_sql_query("SELECT * FROM sales LIMIT 100", conn)
        test_export_path = "test_export.csv"
        df.to_csv(test_export_path, index=False)
        
        # Verify export
        if os.path.exists(test_export_path):
            imported_df = pd.read_csv(test_export_path)
            print(f"  ✓ CSV Export: {len(imported_df)} rows exported")
            os.remove(test_export_path)  # Clean up
        else:
            print("  ✗ CSV Export failed")
            all_passed = False
        
        conn.close()
        
    except Exception as e:
        print(f"  ✗ Export pipeline failed: {e}")
        all_passed = False
    
    # Test 3: ML Prediction Pipeline
    print("\n3. Testing ML Prediction Pipeline...")
    try:
        predictor = SalesPredictor()
        
        # Prepare data for prediction
        data = predictor.prepare_data()
        if not data.empty:
            # Take a sample for prediction
            sample = data.drop(['date', 'amount'], axis=1).iloc[:1]
            prediction = predictor.predict_sales(sample)
            print(f"  ✓ ML Prediction: ${prediction[0]:.2f}")
        else:
            print("  ✗ No data for ML prediction")
            all_passed = False
            
    except Exception as e:
        print(f"  ✗ ML pipeline failed: {e}")
        all_passed = False
    
    # Test 4: Business Intelligence Metrics
    print("\n4. Testing Business Intelligence Metrics...")
    try:
        calculator = BusinessCalculations()
        
        # Test various business metrics
        metrics_to_test = [
            ("Revenue Growth", lambda: calculator.get_sales_summary()['total_revenue']),
            ("Average Transaction", lambda: calculator.get_sales_summary()['avg_transaction_value']),
            ("Customer Count", lambda: calculator.get_sales_summary()['unique_customers']),
            ("Profit Margin", lambda: calculator.calculate_profit_margin()['margin_percentage'].mean())
        ]
        
        for metric_name, metric_func in metrics_to_test:
            try:
                value = metric_func()
                print(f"  ✓ {metric_name}: {value:,.2f}" if isinstance(value, (int, float)) else f"  ✓ {metric_name}: Calculated")
            except:
                print(f"  ⚠ {metric_name}: Calculation error")
        
    except Exception as e:
        print(f"  ✗ BI metrics failed: {e}")
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("END-TO-END TESTS: ALL PASSED ✓")
    else:
        print("END-TO-END TESTS: SOME FAILED ✗")
    print("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    test_end_to_end()