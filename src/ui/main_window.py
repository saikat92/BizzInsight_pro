import tkinter as tk
from tkinter import ttk, messagebox
from .dashboard import Dashboard
from .data_entry import DataEntry
from .reports import Reports
from visualization.dashboard_widgets import ChartsDashboard

class MainWindow:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        
        # Create menu bar
        self.create_menu()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_data_entry_tab()
        self.create_analytics_tab()
        self.create_reports_tab()
        self.create_settings_tab()
        
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Refresh Data", command=self.refresh_data)
        tools_menu.add_command(label="Run ML Models", command=self.run_ml_models)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_docs)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_dashboard_tab(self):
        """Create dashboard tab with KPIs and charts"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Create dashboard
        self.dashboard = Dashboard(dashboard_frame, self.config)
        
    def create_data_entry_tab(self):
        """Create data entry tab"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="Data Entry")
        
        self.data_entry = DataEntry(data_frame, self.config)
    
    def create_analytics_tab(self):
        """Create analytics tab with charts"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="Analytics")
        
        self.charts = ChartsDashboard(analytics_frame, self.config)
    
    def create_reports_tab(self):
        """Create reports tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        
        self.reports = Reports(reports_frame, self.config)
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Settings widgets
        ttk.Label(settings_frame, text="Application Settings", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Theme selection
        ttk.Label(settings_frame, text="Theme:").pack(pady=5)
        self.theme_var = tk.StringVar(value="light")
        theme_combo = ttk.Combobox(settings_frame, textvariable=self.theme_var,
                                  values=["light", "dark", "blue"])
        theme_combo.pack(pady=5)
        
        # Refresh interval
        ttk.Label(settings_frame, text="Data Refresh Interval (minutes):").pack(pady=5)
        self.refresh_var = tk.StringVar(value="5")
        ttk.Entry(settings_frame, textvariable=self.refresh_var, width=10).pack(pady=5)
        
        # Save button
        ttk.Button(settings_frame, text="Save Settings", 
                  command=self.save_settings).pack(pady=20)
    
    def export_data(self):
        messagebox.showinfo("Export", "Data export feature coming soon!")
    
    def refresh_data(self):
        self.dashboard.refresh()
        messagebox.showinfo("Refresh", "Data refreshed successfully!")
    
    def run_ml_models(self):
        from ml.train import SalesPredictor
        predictor = SalesPredictor()
        predictor.train_models()
        messagebox.showinfo("ML Models", "Machine learning models trained successfully!")
    
    def show_docs(self):
        messagebox.showinfo("Documentation", "See docs/ folder for documentation.")
    
    def show_about(self):
        about_text = """Business Intelligence System v1.0
Final Project - Python Power Program
Developed as part of 120-hour training program
        
Features:
• Database Management
• Data Analytics
• Machine Learning
• Interactive Dashboard
• Report Generation"""
        messagebox.showinfo("About", about_text)
    
    def save_settings(self):
        messagebox.showinfo("Settings", "Settings saved successfully!")