import sys
import os
sys.path.append('src')

def test_data_processing():
    """Test data processing calculations"""
    print("=" * 50)
    print("DATA PROCESSING TESTING")
    print("=" * 50)
    
    from data_processing.calculations import BusinessCalculations
    
    calculator = BusinessCalculations()
    
    tests = [
        ("Sales Summary", calculator.get_sales_summary),
        ("Top Products", lambda: calculator.get_top_products(5)),
        ("Customer Segmentation", calculator.get_customer_segmentation),
        ("Sales Trend", lambda: calculator.get_sales_trend('monthly')),
        ("Profit Margin", calculator.calculate_profit_margin)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        try:
            result = test_func()
            
            # Check if result is not empty
            if hasattr(result, 'empty') and result.empty:
                print(f"  ✗ {test_name}: Empty result")
                all_passed = False
            elif hasattr(result, '__len__') and len(result) == 0:
                print(f"  ✗ {test_name}: Empty result")
                all_passed = False
            else:
                print(f"  ✓ {test_name}: Success")
                
                # Show sample of result
                if hasattr(result, 'head'):
                    print(f"    Sample: {result.head(3).to_string() if len(result) > 3 else result.to_string()}")
                elif isinstance(result, dict):
                    print(f"    Result keys: {list(result.keys())}")
                    
        except Exception as e:
            print(f"  ✗ {test_name} failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("DATA PROCESSING TESTS: ALL PASSED ✓")
    else:
        print("DATA PROCESSING TESTS: SOME FAILED ✗")
    print("=" * 50)
    return all_passed

if __name__ == "__main__":
    test_data_processing()