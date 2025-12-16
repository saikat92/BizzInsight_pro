import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
from database.db_connection import get_sqlite_connection

class ChartsDashboard:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.conn = get_sqlite_connection()
        
        # Create frames
        self.create_controls_frame()
        self.create_charts_frame()
        
    def create_controls_frame(self):
        """Create control panel for charts"""
        controls_frame = ttk.Frame(self.parent)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Chart Controls", 
                 font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        
        # Chart type selection
        ttk.Label(controls_frame, text="Chart Type:").pack(side='left', padx=5)
        self.chart_type = tk.StringVar(value="sales_trend")
        chart_combo = ttk.Combobox(controls_frame, textvariable=self.chart_type,
                                  values=["sales_trend", "top_products", 
                                         "customer_segments", "profit_margin"])
        chart_combo.pack(side='left', padx=5)
        
        # Period selection
        ttk.Label(controls_frame, text="Period:").pack(side='left', padx=5)
        self.period = tk.StringVar(value="monthly")
        period_combo = ttk.Combobox(controls_frame, textvariable=self.period,
                                   values=["daily", "weekly", "monthly", "quarterly"])
        period_combo.pack(side='left', padx=5)
        
        # Update button
        ttk.Button(controls_frame, text="Update Chart", 
                  command=self.update_chart).pack(side='left', padx=10)
    
    def create_charts_frame(self):
        """Create frame for charts"""
        self.charts_frame = ttk.Frame(self.parent)
        self.charts_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create initial chart
        self.update_chart()
    
    def update_chart(self):
        """Update chart based on selections"""
        # Clear existing chart
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        chart_type = self.chart_type.get()
        
        if chart_type == "sales_trend":
            self.plot_sales_trend()
        elif chart_type == "top_products":
            self.plot_top_products()
        elif chart_type == "customer_segments":
            self.plot_customer_segments()
        elif chart_type == "profit_margin":
            self.plot_profit_margin()
    
    def plot_sales_trend(self):
        """Plot sales trend over time"""
        period = self.period.get()
        
        if period == 'monthly':
            query = "SELECT strftime('%Y-%m', date) as period, SUM(amount) as revenue FROM sales GROUP BY period ORDER BY period"
        elif period == 'weekly':
            query = "SELECT strftime('%Y-%W', date) as period, SUM(amount) as revenue FROM sales GROUP BY period ORDER BY period"
        else:  # daily
            query = "SELECT date as period, SUM(amount) as revenue FROM sales GROUP BY date ORDER BY date"
        
        df = pd.read_sql_query(query, self.conn)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df['period'], df['revenue'], marker='o', linewidth=2)
        ax.set_title(f'Sales Trend ({period.capitalize()})', fontsize=14, fontweight='bold')
        ax.set_xlabel('Period')
        ax.set_ylabel('Revenue ($)')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def plot_top_products(self):
        """Plot top selling products"""
        query = """
        SELECT p.name, SUM(s.amount) as revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.id
        ORDER BY revenue DESC
        LIMIT 10
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(df['name'], df['revenue'], color='skyblue')
        ax.set_title('Top 10 Products by Revenue', fontsize=14, fontweight='bold')
        ax.set_xlabel('Revenue ($)')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'${width:,.0f}', ha='left', va='center')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def plot_customer_segments(self):
        """Plot customer segments"""
        query = """
        SELECT segment, COUNT(*) as count, SUM(amount) as total_spent
        FROM customers c
        LEFT JOIN sales s ON c.id = s.customer_id
        GROUP BY segment
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Pie chart for customer count
        ax1.pie(df['count'], labels=df['segment'], autopct='%1.1f%%')
        ax1.set_title('Customer Distribution by Segment')
        
        # Bar chart for spending
        ax2.bar(df['segment'], df['total_spent'], color='lightgreen')
        ax2.set_title('Total Spending by Segment')
        ax2.set_ylabel('Total Spent ($)')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def plot_profit_margin(self):
        """Plot profit margins by category"""
        query = """
        SELECT p.category, 
               SUM(s.amount) as revenue,
               SUM(s.quantity * p.cost) as cost,
               (SUM(s.amount) - SUM(s.quantity * p.cost)) as profit
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.category
        """
        
        df = pd.read_sql_query(query, self.conn)
        df['margin'] = (df['profit'] / df['revenue']) * 100
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = range(len(df))
        ax.bar(x, df['revenue'], width=0.4, label='Revenue', align='center')
        ax.bar([i + 0.4 for i in x], df['profit'], width=0.4, label='Profit', align='center')
        
        ax.set_xlabel('Product Category')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Revenue vs Profit by Category')
        ax.set_xticks([i + 0.2 for i in x])
        ax.set_xticklabels(df['category'], rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add margin percentages
        for i, margin in enumerate(df['margin']):
            ax.text(i + 0.2, df['profit'].iloc[i], f'{margin:.1f}%', 
                   ha='center', va='bottom')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)