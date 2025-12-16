import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
import os
from database.db_connection import get_sqlite_connection

class SalesPredictor:
    def __init__(self):
        self.conn = get_sqlite_connection()
        self.models_dir = os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(self.models_dir, exist_ok=True)
    
    def prepare_data(self):
        """Prepare data for sales prediction"""
        query = """
        SELECT 
            s.date,
            s.amount,
            s.quantity,
            p.category,
            p.price,
            c.segment,
            strftime('%m', s.date) as month,
            strftime('%w', s.date) as day_of_week
        FROM sales s
        JOIN products p ON s.product_id = p.id
        JOIN customers c ON s.customer_id = c.id
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Create features
        df['day_of_month'] = df['date'].dt.day
        df['is_weekend'] = df['day_of_week'].isin(['0', '6']).astype(int)
        
        # One-hot encode categorical variables
        df = pd.get_dummies(df, columns=['category', 'segment', 'month'])
        
        # Lag features for time series
        df = df.sort_values('date')
        df['prev_day_sales'] = df['amount'].shift(1)
        df['rolling_7day_avg'] = df['amount'].rolling(window=7).mean().shift(1)
        
        df = df.dropna()
        
        return df
    
    def train_models(self):
        """Train sales prediction models"""
        df = self.prepare_data()
        
        # Features and target
        X = df.drop(['date', 'amount'], axis=1)
        y = df['amount']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train Linear Regression
        print("Training Linear Regression...")
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        
        # Train Random Forest
        print("Training Random Forest...")
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        
        # Evaluate models
        models = {'Linear Regression': lr_model, 'Random Forest': rf_model}
        
        for name, model in models.items():
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            print(f"\n{name} Performance:")
            print(f"MAE: ${mae:.2f}")
            print(f"RMSE: ${rmse:.2f}")
            print(f"R² Score: {r2:.4f}")
        
        # Save models
        with open(os.path.join(self.models_dir, 'sales_lr_model.pkl'), 'wb') as f:
            pickle.dump(lr_model, f)
        
        with open(os.path.join(self.models_dir, 'sales_rf_model.pkl'), 'wb') as f:
            pickle.dump(rf_model, f)
        
        print("\nModels saved successfully!")
        
        return models
    
    def predict_sales(self, input_data):
        """Predict sales for given input"""
        # Load model
        model_path = os.path.join(self.models_dir, 'sales_rf_model.pkl')
        
        if not os.path.exists(model_path):
            print("Model not found. Training first...")
            self.train_models()
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Make prediction
        prediction = model.predict(input_data)
        return prediction