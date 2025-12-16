import sys
import os
sys.path.append('src')

def test_machine_learning():
    """Test ML model training and prediction"""
    print("=" * 50)
    print("MACHINE LEARNING TESTING")
    print("=" * 50)
    
    from ml.train import SalesPredictor
    import pandas as pd
    import numpy as np
    
    predictor = SalesPredictor()
    
    print("\n1. Testing data preparation...")
    try:
        data = predictor.prepare_data()
        print(f"✓ Data prepared: {data.shape[0]} rows, {data.shape[1]} columns")
        print(f"  Columns: {list(data.columns[:10])}...")  # Show first 10 columns
    except Exception as e:
        print(f"✗ Data preparation failed: {e}")
        return False
    
    print("\n2. Testing model training...")
    try:
        models = predictor.train_models()
        print("✓ Models trained successfully")
        print(f"  Models trained: {list(models.keys())}")
    except Exception as e:
        print(f"✗ Model training failed: {e}")
        return False
    
    print("\n3. Testing prediction...")
    try:
        # Create sample input for prediction
        if not data.empty:
            sample_input = data.drop(['date', 'amount'], axis=1).iloc[:1]
            prediction = predictor.predict_sales(sample_input)
            print(f"✓ Prediction made: ${prediction[0]:.2f}")
        else:
            print("✗ No data available for prediction")
            return False
    except Exception as e:
        print(f"✗ Prediction failed: {e}")
        return False
    
    print("\n4. Testing model persistence...")
    try:
        import pickle
        model_path = 'src/ml/models/sales_rf_model.pkl'
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                loaded_model = pickle.load(f)
            print("✓ Model saved and can be loaded")
        else:
            print("✗ Model file not found")
            return False
    except Exception as e:
        print(f"✗ Model persistence test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("MACHINE LEARNING TESTS: ALL PASSED ✓")
    print("=" * 50)
    return True

if __name__ == "__main__":
    test_machine_learning()