from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    category = Column(String(50))
    price = Column(Float)
    cost = Column(Float)
    stock = Column(Integer)
    
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    join_date = Column(Date, default=datetime.date.today)
    segment = Column(String(50))  # 'Regular', 'Premium', etc.
    
class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    amount = Column(Float)
    payment_method = Column(String(50))
    
class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    department = Column(String(50))
    salary = Column(Float)
    hire_date = Column(Date)
    
class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    last_updated = Column(Date)
    
# Create relationships
Customer.sales = relationship("Sale", back_populates="customer")
Product.sales = relationship("Sale", back_populates="product")
Sale.customer = relationship("Customer", back_populates="sales")
Sale.product = relationship("Product", back_populates="sales")