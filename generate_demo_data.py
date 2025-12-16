import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
from src.database.db_connection import get_session
from src.database.models import Product, Customer, Sale, Employee, Inventory

fake = Faker()

def generate_products(n=100):
    """Generate sample product data"""
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 
                  'Sports', 'Toys', 'Food & Beverages', 'Health']
    
    products = []
    for i in range(n):
        cost = round(random.uniform(5, 500), 2)
        margin = random.uniform(0.2, 1.0)  # 20-100% margin
        price = round(cost * (1 + margin), 2)
        
        products.append({
            'name': f'{fake.word().capitalize()} {random.choice(["Pro", "Deluxe", "Basic", "Premium"])}',
            'category': random.choice(categories),
            'price': price,
            'cost': cost,
            'stock': random.randint(0, 1000)
        })
    
    return pd.DataFrame(products)

def generate_customers(n=500):
    """Generate sample customer data"""
    customers = []
    segments = ['Regular', 'Premium', 'VIP', 'New']
    
    for i in range(n):
        join_date = fake.date_between(start_date='-2y', end_date='today')
        
        customers.append({
            'name': fake.name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'join_date': join_date,
            'segment': random.choice(segments)
        })
    
    return pd.DataFrame(customers)

def generate_sales(n=10000):
    """Generate sample sales data for the past 2 years"""
    sales = []
    start_date = datetime.now() - timedelta(days=730)  # 2 years
    
    for i in range(n):
        sale_date = start_date + timedelta(days=random.randint(0, 730))
        customer_id = random.randint(1, 500)
        product_id = random.randint(1, 100)
        quantity = random.randint(1, 10)
        price = round(random.uniform(10, 1000), 2)
        amount = round(quantity * price, 2)
        
        sales.append({
            'date': sale_date.date(),
            'customer_id': customer_id,
            'product_id': product_id,
            'quantity': quantity,
            'amount': amount,
            'payment_method': random.choice(['Credit Card', 'Cash', 'PayPal', 'Bank Transfer'])
        })
    
    return pd.DataFrame(sales)

def populate_database():
    """Populate database with demo data"""
    print("Generating demo data...")
    
    # Generate data
    products_df = generate_products()
    customers_df = generate_customers()
    sales_df = generate_sales()
    
    # Save to CSV for backup
    products_df.to_csv('data/raw/products.csv', index=False)
    customers_df.to_csv('data/raw/customers.csv', index=False)
    sales_df.to_csv('data/raw/sales.csv', index=False)
    
    # Insert into database
    session = get_session()
    
    try:
        # Clear existing data
        session.query(Sale).delete()
        session.query(Customer).delete()
        session.query(Product).delete()
        session.commit()
        
        # Insert products
        for _, row in products_df.iterrows():
            product = Product(
                name=row['name'],
                category=row['category'],
                price=row['price'],
                cost=row['cost'],
                stock=row['stock']
            )
            session.add(product)
        
        # Insert customers
        for _, row in customers_df.iterrows():
            customer = Customer(
                name=row['name'],
                email=row['email'],
                phone=row['phone'],
                join_date=row['join_date'],
                segment=row['segment']
            )
            session.add(customer)
        
        session.commit()
        
        # Insert sales
        for _, row in sales_df.iterrows():
            sale = Sale(
                date=row['date'],
                customer_id=row['customer_id'],
                product_id=row['product_id'],
                quantity=row['quantity'],
                amount=row['amount'],
                payment_method=row['payment_method']
            )
            session.add(sale)
        
        session.commit()
        print(f"Database populated: {len(products_df)} products, {len(customers_df)} customers, {len(sales_df)} sales")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    populate_database()