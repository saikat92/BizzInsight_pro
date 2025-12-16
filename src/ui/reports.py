import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from database.db_connection import get_sqlite_connection

class Reports:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.conn = get_sqlite_connection()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create report generation interface"""
        # Report type selection
        ttk.Label(self.parent, text="Generate Report", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        frame = ttk.Frame(self.parent)
        frame.pack(pady=10)
        
        # Report type
        ttk.Label(frame, text="Report Type:").grid(row=0, column=0, padx=5, pady=5)
        self.report_type = tk.StringVar(value="sales_summary")
        report_combo = ttk.Combobox(frame, textvariable=self.report_type,
                                   values=["sales_summary", "product_analysis", 
                                          "customer_analysis", "financial_report"])
        report_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Date range
        ttk.Label(frame, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.start_date = ttk.Entry(frame, width=15)
        self.start_date.grid(row=1, column=1, padx=5, pady=5)
        self.start_date.insert(0, datetime.now().strftime('%Y-%m-01'))
        
        ttk.Label(frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.end_date = ttk.Entry(frame, width=15)
        self.end_date.grid(row=2, column=1, padx=5, pady=5)
        self.end_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Format selection
        ttk.Label(frame, text="Format:").grid(row=3, column=0, padx=5, pady=5)
        self.format_type = tk.StringVar(value="PDF")
        format_combo = ttk.Combobox(frame, textvariable=self.format_type,
                                   values=["PDF", "Excel", "CSV"])
        format_combo.grid(row=3, column=1, padx=5, pady=5)
        
        # Generate button
        ttk.Button(frame, text="Generate Report", 
                  command=self.generate_report).grid(row=4, column=0, columnspan=2, pady=20)
        
        # Status label
        self.status_label = ttk.Label(self.parent, text="")
        self.status_label.pack(pady=5)
    
    def generate_report(self):
        """Generate the selected report"""
        report_type = self.report_type.get()
        format_type = self.format_type.get()
        
        try:
            if report_type == "sales_summary":
                data = self.generate_sales_summary()
            elif report_type == "product_analysis":
                data = self.generate_product_analysis()
            elif report_type == "customer_analysis":
                data = self.generate_customer_analysis()
            elif report_type == "financial_report":
                data = self.generate_financial_report()
            
            # Save report
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{format_type.lower()}",
                filetypes=[(f"{format_type} files", f"*.{format_type.lower()}")]
            )
            
            if filename:
                if format_type == "PDF":
                    self.save_as_pdf(data, filename, report_type)
                elif format_type == "Excel":
                    data.to_excel(filename, index=False)
                else:  # CSV
                    data.to_csv(filename, index=False)
                
                self.status_label.config(text=f"Report saved to: {filename}")
                messagebox.showinfo("Success", "Report generated successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def generate_sales_summary(self):
        """Generate sales summary report"""
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        
        query = f"""
        SELECT 
            date,
            COUNT(*) as transactions,
            SUM(amount) as daily_revenue,
            AVG(amount) as avg_transaction,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM sales
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY date
        ORDER BY date
        """
        
        return pd.read_sql_query(query, self.conn)
    
    def generate_product_analysis(self):
        """Generate product analysis report"""
        query = """
        SELECT 
            p.name,
            p.category,
            SUM(s.quantity) as units_sold,
            SUM(s.amount) as total_revenue,
            AVG(p.price) as avg_price,
            (SUM(s.amount) - SUM(s.quantity * p.cost)) as total_profit
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.id
        ORDER BY total_revenue DESC
        """
        
        return pd.read_sql_query(query, self.conn)
    
    def generate_customer_analysis(self):
        """Generate customer analysis report"""
        query = """
        SELECT 
            c.name,
            c.segment,
            c.join_date,
            COUNT(s.id) as purchase_count,
            SUM(s.amount) as total_spent,
            MAX(s.date) as last_purchase,
            AVG(s.amount) as avg_purchase_value
        FROM customers c
        LEFT JOIN sales s ON c.id = s.customer_id
        GROUP BY c.id
        ORDER BY total_spent DESC
        """
        
        return pd.read_sql_query(query, self.conn)
    
    def generate_financial_report(self):
        """Generate financial report"""
        query = """
        SELECT 
            strftime('%Y-%m', s.date) as month,
            SUM(s.amount) as revenue,
            SUM(s.quantity * p.cost) as cost_of_goods,
            (SUM(s.amount) - SUM(s.quantity * p.cost)) as gross_profit,
            COUNT(DISTINCT s.customer_id) as active_customers,
            COUNT(s.id) as transactions
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY month
        ORDER BY month
        """
        
        return pd.read_sql_query(query, self.conn)
    
    def save_as_pdf(self, data, filename, title):
        """Save report as PDF"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        elements.append(Paragraph(f"Business Intelligence Report: {title}", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Report info
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                                 styles['Normal']))
        elements.append(Paragraph(f"Date Range: {self.start_date.get()} to {self.end_date.get()}", 
                                 styles['Normal']))
        elements.append(Spacer(1, 24))
        
        # Convert DataFrame to list for table
        table_data = [data.columns.tolist()] + data.values.tolist()
        
        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)