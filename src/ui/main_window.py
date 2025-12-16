import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ui.dashboard import Dashboard
from ui.data_entry import DataEntry
from ui.reports import Reports
from visualization.dashboard_widgets import ChartsDashboard
from ui.styles import UIConfig

class MainWindow:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.ui_config = UIConfig()
        
        # Configure root window
        self.root.configure(bg=self.ui_config.theme['light'])
        
        # Create menu bar
        self.create_menu()
        
        # Create header with company logo
        self.create_header()
        
        # Create notebook for tabs with custom style
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Apply custom style to notebook
        style = ttk.Style()
        style.configure('Premium.TNotebook',
                       background=self.ui_config.theme['light'],
                       borderwidth=0)
        style.configure('Premium.TNotebook.Tab',
                       background=self.ui_config.theme['white'],
                       foreground=self.ui_config.theme['dark'],
                       padding=[25, 10],
                       font=self.ui_config.fonts['body_bold'])
        style.map('Premium.TNotebook.Tab',
                 background=[('selected', self.ui_config.theme['primary'])],
                 foreground=[('selected', self.ui_config.theme['white'])])
        
        self.notebook.configure(style='Premium.TNotebook')
        
        # Create tabs with premium dashboard
        self.create_dashboard_tab()
        # self.create_dashboard_tab()
        # self.create_analytics_tab()
        # self.create_reports_tab()
        # self.create_ml_tab()
        
        # Create status bar
        self.create_status_bar()
    
    # =============== ADD THIS FUNCTION RIGHT HERE ===============
    def create_menu(self):
        """Create premium application menu bar"""
        # Create the main menu bar
        menubar = tk.Menu(self.root, bg=self.ui_config.theme['white'],
                         fg=self.ui_config.theme['dark'],
                         activebackground=self.ui_config.theme['primary'],
                         activeforeground=self.ui_config.theme['white'],
                         bd=0)
        self.root.config(menu=menubar)
        
        # ============ File Menu ============
        file_menu = tk.Menu(menubar, tearoff=0,
                           bg=self.ui_config.theme['white'],
                           fg=self.ui_config.theme['dark'],
                           activebackground=self.ui_config.theme['primary_light'],
                           activeforeground=self.ui_config.theme['white'])
        menubar.add_cascade(label="File", menu=file_menu)
        
        # File menu items
        file_menu.add_command(label="New Project", 
                             accelerator="Ctrl+N",
                             command=self.new_project)
        file_menu.add_command(label="Open Project", 
                             accelerator="Ctrl+O",
                             command=self.open_project)
        file_menu.add_separator()
        
        # Export submenu
        export_menu = tk.Menu(file_menu, tearoff=0,
                             bg=self.ui_config.theme['white'],
                             fg=self.ui_config.theme['dark'])
        file_menu.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="Export Dashboard as PDF", 
                               command=self.export_dashboard_pdf)
        export_menu.add_command(label="Export Data as Excel", 
                               command=self.export_data_excel)
        export_menu.add_command(label="Export Charts as Image", 
                               command=self.export_charts_image)
        
        file_menu.add_separator()
        file_menu.add_command(label="Settings", 
                             accelerator="Ctrl+,",
                             command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", 
                             accelerator="Alt+F4",
                             command=self.root.quit)
        
        # ============ Edit Menu ============
        edit_menu = tk.Menu(menubar, tearoff=0,
                           bg=self.ui_config.theme['white'],
                           fg=self.ui_config.theme['dark'])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        edit_menu.add_command(label="Undo", 
                             accelerator="Ctrl+Z",
                             command=self.undo_action)
        edit_menu.add_command(label="Redo", 
                             accelerator="Ctrl+Y",
                             command=self.redo_action)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", 
                             accelerator="Ctrl+X",
                             command=self.cut_action)
        edit_menu.add_command(label="Copy", 
                             accelerator="Ctrl+C",
                             command=self.copy_action)
        edit_menu.add_command(label="Paste", 
                             accelerator="Ctrl+V",
                             command=self.paste_action)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", 
                             accelerator="Ctrl+F",
                             command=self.find_action)
        edit_menu.add_command(label="Replace", 
                             accelerator="Ctrl+H",
                             command=self.replace_action)
        
        # ============ View Menu ============
        view_menu = tk.Menu(menubar, tearoff=0,
                           bg=self.ui_config.theme['white'],
                           fg=self.ui_config.theme['dark'])
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0,
                            bg=self.ui_config.theme['white'],
                            fg=self.ui_config.theme['dark'])
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        
        self.theme_var = tk.StringVar(value="light")
        theme_menu.add_radiobutton(label="Light Theme", 
                                   variable=self.theme_var,
                                   value="light",
                                   command=self.switch_theme)
        theme_menu.add_radiobutton(label="Dark Theme", 
                                   variable=self.theme_var,
                                   value="dark",
                                   command=self.switch_theme)
        theme_menu.add_radiobutton(label="Blue Theme", 
                                   variable=self.theme_var,
                                   value="blue",
                                   command=self.switch_theme)
        
        view_menu.add_separator()
        
        # Dashboard layout
        layout_menu = tk.Menu(view_menu, tearoff=0,
                             bg=self.ui_config.theme['white'],
                             fg=self.ui_config.theme['dark'])
        view_menu.add_cascade(label="Layout", menu=layout_menu)
        
        self.layout_var = tk.StringVar(value="grid")
        layout_menu.add_radiobutton(label="Grid Layout", 
                                    variable=self.layout_var,
                                    value="grid",
                                    command=self.change_layout)
        layout_menu.add_radiobutton(label="Tabbed Layout", 
                                    variable=self.layout_var,
                                    value="tabbed",
                                    command=self.change_layout)
        layout_menu.add_radiobutton(label="Freeform Layout", 
                                    variable=self.layout_var,
                                    value="freeform",
                                    command=self.change_layout)
        
        view_menu.add_separator()
        view_menu.add_command(label="Full Screen", 
                             accelerator="F11",
                             command=self.toggle_fullscreen)
        view_menu.add_command(label="Zoom In", 
                             accelerator="Ctrl++",
                             command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", 
                             accelerator="Ctrl+-",
                             command=self.zoom_out)
        view_menu.add_command(label="Reset Zoom", 
                             accelerator="Ctrl+0",
                             command=self.reset_zoom)
        
        # ============ Tools Menu ============
        tools_menu = tk.Menu(menubar, tearoff=0,
                            bg=self.ui_config.theme['white'],
                            fg=self.ui_config.theme['dark'])
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        tools_menu.add_command(label="Refresh Data", 
                              accelerator="F5",
                              command=self.refresh_data)
        tools_menu.add_command(label="Run ML Models", 
                              accelerator="Ctrl+R",
                              command=self.run_ml_models)
        tools_menu.add_separator()
        
        # Analysis tools submenu
        analysis_menu = tk.Menu(tools_menu, tearoff=0,
                               bg=self.ui_config.theme['white'],
                               fg=self.ui_config.theme['dark'])
        tools_menu.add_cascade(label="Analysis Tools", menu=analysis_menu)
        
        analysis_menu.add_command(label="Sales Forecasting", 
                                 command=self.run_sales_forecasting)
        analysis_menu.add_command(label="Customer Segmentation", 
                                 command=self.run_customer_segmentation)
        analysis_menu.add_command(label="Market Basket Analysis", 
                                 command=self.run_market_basket_analysis)
        analysis_menu.add_command(label="Trend Analysis", 
                                 command=self.run_trend_analysis)
        
        tools_menu.add_separator()
        tools_menu.add_command(label="Database Maintenance", 
                              command=self.database_maintenance)
        tools_menu.add_command(label="Data Cleanup Wizard", 
                              command=self.data_cleanup_wizard)
        tools_menu.add_command(label="Performance Monitor", 
                              command=self.open_performance_monitor)
        
        # ============ Data Menu ============
        data_menu = tk.Menu(menubar, tearoff=0,
                           bg=self.ui_config.theme['white'],
                           fg=self.ui_config.theme['dark'])
        menubar.add_cascade(label="Data", menu=data_menu)
        
        data_menu.add_command(label="Import Data", 
                             accelerator="Ctrl+I",
                             command=self.import_data)
        data_menu.add_command(label="Export Data", 
                             accelerator="Ctrl+E",
                             command=self.export_data)
        data_menu.add_separator()
        data_menu.add_command(label="Data Validation", 
                             command=self.data_validation)
        data_menu.add_command(label="Data Transformation", 
                             command=self.data_transformation)
        data_menu.add_command(label="Merge Datasets", 
                             command=self.merge_datasets)
        data_menu.add_separator()
        data_menu.add_command(label="Generate Sample Data", 
                             command=self.generate_sample_data)
        data_menu.add_command(label="Clear Cache", 
                             command=self.clear_cache)
        
        # ============ Reports Menu ============
        reports_menu = tk.Menu(menubar, tearoff=0,
                              bg=self.ui_config.theme['white'],
                              fg=self.ui_config.theme['dark'])
        menubar.add_cascade(label="Reports", menu=reports_menu)
        
        # Quick reports
        reports_menu.add_command(label="Daily Sales Report", 
                                command=lambda: self.generate_report("daily_sales"))
        reports_menu.add_command(label="Weekly Performance", 
                                command=lambda: self.generate_report("weekly_performance"))
        reports_menu.add_command(label="Monthly Financials", 
                                command=lambda: self.generate_report("monthly_financials"))
        reports_menu.add_command(label="Quarterly Analysis", 
                                command=lambda: self.generate_report("quarterly_analysis"))
        
        reports_menu.add_separator()
        
        # Custom reports
        custom_menu = tk.Menu(reports_menu, tearoff=0,
                             bg=self.ui_config.theme['white'],
                             fg=self.ui_config.theme['dark'])
        reports_menu.add_cascade(label="Custom Reports", menu=custom_menu)
        
        custom_menu.add_command(label="Sales by Product", 
                               command=lambda: self.generate_custom_report("sales_by_product"))
        custom_menu.add_command(label="Customer Behavior", 
                               command=lambda: self.generate_custom_report("customer_behavior"))
        custom_menu.add_command(label="Inventory Analysis", 
                               command=lambda: self.generate_custom_report("inventory_analysis"))
        custom_menu.add_command(label="Employee Performance", 
                               command=lambda: self.generate_custom_report("employee_performance"))
        
        reports_menu.add_separator()
        reports_menu.add_command(label="Report Scheduler", 
                                command=self.open_report_scheduler)
        reports_menu.add_command(label="Report Templates", 
                                command=self.manage_report_templates)
        
        # ============ Window Menu ============
        window_menu = tk.Menu(menubar, tearoff=0,
                             bg=self.ui_config.theme['white'],
                             fg=self.ui_config.theme['dark'])
        menubar.add_cascade(label="Window", menu=window_menu)
        
        window_menu.add_command(label="New Window", 
                               accelerator="Ctrl+Shift+N",
                               command=self.new_window)
        window_menu.add_command(label="Close Window", 
                               accelerator="Ctrl+W",
                               command=self.close_window)
        window_menu.add_separator()
        window_menu.add_command(label="Cascade", 
                               command=self.cascade_windows)
        window_menu.add_command(label="Tile Horizontally", 
                               command=self.tile_horizontally)
        window_menu.add_command(label="Tile Vertically", 
                               command=self.tile_vertically)
        window_menu.add_separator()
        window_menu.add_command(label="Minimize All", 
                               accelerator="Ctrl+M",
                               command=self.minimize_all)
        window_menu.add_command(label="Arrange Icons", 
                               command=self.arrange_icons)
        
        # ============ Help Menu ============
        help_menu = tk.Menu(menubar, tearoff=0,
                           bg=self.ui_config.theme['white'],
                           fg=self.ui_config.theme['dark'])
        menubar.add_cascade(label="Help", menu=help_menu)
        
        help_menu.add_command(label="Documentation", 
                             accelerator="F1",
                             command=self.open_documentation)
        help_menu.add_command(label="Video Tutorials", 
                             command=self.open_tutorials)
        help_menu.add_separator()
        help_menu.add_command(label="Check for Updates", 
                             command=self.check_for_updates)
        help_menu.add_command(label="Keyboard Shortcuts", 
                             accelerator="Ctrl+Shift+K",
                             command=self.show_keyboard_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="Community Forum", 
                             command=self.open_forum)
        help_menu.add_command(label="Submit Feedback", 
                             command=self.submit_feedback)
        help_menu.add_command(label="Report Issue", 
                             command=self.report_issue)
        help_menu.add_separator()
        help_menu.add_command(label="About", 
                             command=self.show_about)
        
        # ============ Bind Keyboard Shortcuts ============
        self.bind_shortcuts()
    
    # =============== MENU ACTION HANDLERS ===============
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts to menu actions"""
        self.root.bind('<Control-n>', lambda e: self.new_project())
        self.root.bind('<Control-o>', lambda e: self.open_project())
        self.root.bind('<Control-,>', lambda e: self.open_settings())
        self.root.bind('<F5>', lambda e: self.refresh_data())
        self.root.bind('<Control-r>', lambda e: self.run_ml_models())
        self.root.bind('<Control-i>', lambda e: self.import_data())
        self.root.bind('<Control-e>', lambda e: self.export_data())
        self.root.bind('<F1>', lambda e: self.open_documentation())
        self.root.bind('<Control-Shift-K>', lambda e: self.show_keyboard_shortcuts())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
    
    def new_project(self):
        """Create a new project"""
        from tkinter import messagebox
        messagebox.showinfo("New Project", "Create new project functionality")
    
    def open_project(self):
        """Open existing project"""
        from tkinter import filedialog, messagebox
        filename = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("Business Intelligence Project", "*.bip"), ("All files", "*.*")]
        )
        if filename:
            messagebox.showinfo("Open Project", f"Opening: {filename}")
    
    def open_settings(self):
        """Open settings dialog"""
        from tkinter import messagebox
        messagebox.showinfo("Settings", "Settings dialog would open here")
    
    def export_dashboard_pdf(self):
        """Export dashboard as PDF"""
        from tkinter import messagebox
        messagebox.showinfo("Export PDF", "Exporting dashboard as PDF...")
    
    def export_data_excel(self):
        """Export data as Excel"""
        from tkinter import messagebox
        messagebox.showinfo("Export Excel", "Exporting data as Excel...")
    
    def export_charts_image(self):
        """Export charts as image"""
        from tkinter import messagebox
        messagebox.showinfo("Export Image", "Exporting charts as image...")
    
    def undo_action(self):
        """Undo last action"""
        print("Undo action")
    
    def redo_action(self):
        """Redo last undone action"""
        print("Redo action")
    
    def cut_action(self):
        """Cut selected text"""
        self.root.focus_get().event_generate("<<Cut>>")
    
    def copy_action(self):
        """Copy selected text"""
        self.root.focus_get().event_generate("<<Copy>>")
    
    def paste_action(self):
        """Paste from clipboard"""
        self.root.focus_get().event_generate("<<Paste>>")
    
    def find_action(self):
        """Find text"""
        from tkinter import messagebox
        messagebox.showinfo("Find", "Find dialog would open here")
    
    def replace_action(self):
        """Replace text"""
        from tkinter import messagebox
        messagebox.showinfo("Replace", "Replace dialog would open here")
    
    def switch_theme(self):
        """Switch between light/dark theme"""
        theme = self.theme_var.get()
        self.ui_config = UIConfig(theme=theme)
        from tkinter import messagebox
        messagebox.showinfo("Theme Changed", f"Switched to {theme} theme")
    
    def change_layout(self):
        """Change dashboard layout"""
        layout = self.layout_var.get()
        from tkinter import messagebox
        messagebox.showinfo("Layout Changed", f"Changed to {layout} layout")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)
    
    def zoom_in(self):
        """Zoom in dashboard"""
        print("Zoom in")
    
    def zoom_out(self):
        """Zoom out dashboard"""
        print("Zoom out")
    
    def reset_zoom(self):
        """Reset zoom level"""
        print("Reset zoom")
    
    def refresh_data(self):
        """Refresh all data"""
        if hasattr(self, 'dashboard'):
            self.dashboard.refresh()
        from tkinter import messagebox
        messagebox.showinfo("Refresh", "Data refreshed successfully!")
    
    def run_ml_models(self):
        """Run machine learning models"""
        from ml.train import SalesPredictor
        predictor = SalesPredictor()
        predictor.train_models()
        from tkinter import messagebox
        messagebox.showinfo("ML Models", "Machine learning models trained successfully!")
    
    def run_sales_forecasting(self):
        """Run sales forecasting"""
        from tkinter import messagebox
        messagebox.showinfo("Sales Forecasting", "Running sales forecasting...")
    
    def run_customer_segmentation(self):
        """Run customer segmentation"""
        from tkinter import messagebox
        messagebox.showinfo("Customer Segmentation", "Running customer segmentation...")
    
    def run_market_basket_analysis(self):
        """Run market basket analysis"""
        from tkinter import messagebox
        messagebox.showinfo("Market Basket Analysis", "Running market basket analysis...")
    
    def run_trend_analysis(self):
        """Run trend analysis"""
        from tkinter import messagebox
        messagebox.showinfo("Trend Analysis", "Running trend analysis...")
    
    def database_maintenance(self):
        """Perform database maintenance"""
        from tkinter import messagebox
        messagebox.showinfo("Database Maintenance", "Running database maintenance...")
    
    def data_cleanup_wizard(self):
        """Open data cleanup wizard"""
        from tkinter import messagebox
        messagebox.showinfo("Data Cleanup", "Opening data cleanup wizard...")
    
    def open_performance_monitor(self):
        """Open performance monitor"""
        from tkinter import messagebox
        messagebox.showinfo("Performance Monitor", "Opening performance monitor...")
    
    def import_data(self):
        """Import data from file"""
        from tkinter import filedialog, messagebox
        filename = filedialog.askopenfilename(
            title="Import Data",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            messagebox.showinfo("Import", f"Importing: {filename}")
    
    def export_data(self):
        """Export data to file"""
        from tkinter import filedialog, messagebox
        filename = filedialog.asksaveasfilename(
            title="Export Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            messagebox.showinfo("Export", f"Exporting to: {filename}")
    
    def data_validation(self):
        """Validate data"""
        from tkinter import messagebox
        messagebox.showinfo("Data Validation", "Running data validation...")
    
    def data_transformation(self):
        """Transform data"""
        from tkinter import messagebox
        messagebox.showinfo("Data Transformation", "Running data transformation...")
    
    def merge_datasets(self):
        """Merge datasets"""
        from tkinter import messagebox
        messagebox.showinfo("Merge Datasets", "Merging datasets...")
    
    def generate_sample_data(self):
        """Generate sample data"""
        from generate_demo_data import populate_database
        populate_database()
        from tkinter import messagebox
        messagebox.showinfo("Sample Data", "Sample data generated successfully!")
    
    def clear_cache(self):
        """Clear application cache"""
        from tkinter import messagebox
        messagebox.showinfo("Clear Cache", "Cache cleared successfully!")
    
    def generate_report(self, report_type):
        """Generate report"""
        from tkinter import messagebox
        messagebox.showinfo("Generate Report", f"Generating {report_type.replace('_', ' ')} report...")
    
    def generate_custom_report(self, report_type):
        """Generate custom report"""
        from tkinter import messagebox
        messagebox.showinfo("Custom Report", f"Generating custom {report_type.replace('_', ' ')} report...")
    
    def open_report_scheduler(self):
        """Open report scheduler"""
        from tkinter import messagebox
        messagebox.showinfo("Report Scheduler", "Opening report scheduler...")
    
    def manage_report_templates(self):
        """Manage report templates"""
        from tkinter import messagebox
        messagebox.showinfo("Report Templates", "Managing report templates...")
    
    def new_window(self):
        """Open new window"""
        from tkinter import messagebox
        messagebox.showinfo("New Window", "Opening new window...")
    
    def close_window(self):
        """Close current window"""
        self.root.quit()
    
    def cascade_windows(self):
        """Cascade windows"""
        print("Cascade windows")
    
    def tile_horizontally(self):
        """Tile windows horizontally"""
        print("Tile horizontally")
    
    def tile_vertically(self):
        """Tile windows vertically"""
        print("Tile vertically")
    
    def minimize_all(self):
        """Minimize all windows"""
        self.root.iconify()
    
    def arrange_icons(self):
        """Arrange icons"""
        print("Arrange icons")
    
    def open_documentation(self):
        """Open documentation"""
        import webbrowser
        webbrowser.open("https://docs.python.org/")
        from tkinter import messagebox
        messagebox.showinfo("Documentation", "Opening documentation in browser...")
    
    def open_tutorials(self):
        """Open video tutorials"""
        import webbrowser
        webbrowser.open("https://www.youtube.com/")
        from tkinter import messagebox
        messagebox.showinfo("Tutorials", "Opening tutorials in browser...")
    
    def check_for_updates(self):
        """Check for updates"""
        from tkinter import messagebox
        messagebox.showinfo("Check Updates", "Checking for updates...")
    
    def show_keyboard_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts = """
        Keyboard Shortcuts:
        
        File Operations:
        Ctrl+N       - New Project
        Ctrl+O       - Open Project
        Ctrl+S       - Save
        Ctrl+Shift+S - Save As
        Ctrl+P       - Print
        Ctrl+Q       - Exit
        
        Edit Operations:
        Ctrl+Z       - Undo
        Ctrl+Y       - Redo
        Ctrl+X       - Cut
        Ctrl+C       - Copy
        Ctrl+V       - Paste
        Ctrl+A       - Select All
        Ctrl+F       - Find
        Ctrl+H       - Replace
        
        View Operations:
        F11          - Full Screen
        Ctrl++       - Zoom In
        Ctrl+-       - Zoom Out
        Ctrl+0       - Reset Zoom
        
        Data Operations:
        F5           - Refresh Data
        Ctrl+R       - Run ML Models
        Ctrl+I       - Import Data
        Ctrl+E       - Export Data
        
        Help:
        F1           - Help/Documentation
        Ctrl+Shift+K - Keyboard Shortcuts
        """
        from tkinter import Toplevel, Text, Scrollbar
        shortcuts_window = Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("500x400")
        
        text = Text(shortcuts_window, wrap='word', font=('Consolas', 10))
        scrollbar = Scrollbar(shortcuts_window, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        text.insert('1.0', shortcuts)
        text.config(state='disabled')
        
        text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def open_forum(self):
        """Open community forum"""
        import webbrowser
        webbrowser.open("https://stackoverflow.com/")
        from tkinter import messagebox
        messagebox.showinfo("Community Forum", "Opening community forum...")
    
    def submit_feedback(self):
        """Submit feedback"""
        from tkinter import messagebox
        messagebox.showinfo("Submit Feedback", "Opening feedback form...")
    
    def report_issue(self):
        """Report issue"""
        from tkinter import messagebox
        messagebox.showinfo("Report Issue", "Opening issue reporter...")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Business Intelligence System v1.0
        
A comprehensive desktop application for business analytics,
data management, and machine learning predictions.

Features:
• Database Management (SQLite)
• Interactive Dashboard
• Real-time Analytics
• Machine Learning Models
• Report Generation
• Data Visualization

Developed as part of Python Power Program
120-Hour Complete Training Program

© 2024 Business Intelligence System
All rights reserved."""
        from tkinter import messagebox
        messagebox.showinfo("About", about_text)
    
    # =============== CONTINUE WITH OTHER METHODS ===============

    def create_header(self):
        """Create premium header with logo"""
        header = tk.Frame(self.root, bg=self.ui_config.theme['primary'],
                         height=60)
        header.pack(fill='x', side='top')
        
        # Logo/Title
        logo_frame = tk.Frame(header, bg=self.ui_config.theme['primary'])
        logo_frame.pack(side='left', padx=30)
        
        # Icon
        icon_label = tk.Label(logo_frame, text="📊",
                             font=("Segoe UI", 24),
                             bg=self.ui_config.theme['primary'],
                             fg=self.ui_config.theme['white'])
        icon_label.pack(side='left', padx=(0, 10))
        
        # Title
        title_label = tk.Label(logo_frame, text="Business Intelligence Suite",
                              font=self.ui_config.fonts['h2'],
                              bg=self.ui_config.theme['primary'],
                              fg=self.ui_config.theme['white'])
        title_label.pack(side='left')
        
        # Quick stats in header
        stats_frame = tk.Frame(header, bg=self.ui_config.theme['primary'])
        stats_frame.pack(side='right', padx=30)
        
        # You could add real-time stats here
        stats_label = tk.Label(stats_frame, 
                              text="Real-time Analytics • Live Data",
                              font=self.ui_config.fonts['small'],
                              bg=self.ui_config.theme['primary'],
                              fg=self.ui_config.theme['white'])
        stats_label.pack()
    
    def create_dashboard_tab(self):
        """Create premium dashboard tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="🏠 Dashboard")
        
        # Create premium dashboard
        self.dashboard = Dashboard(dashboard_frame, self.config)
        self.dashboard.pack(fill='both', expand=True)
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_bar = tk.Frame(self.root, bg=self.ui_config.theme['dark'],
                             height=30)
        status_bar.pack(fill='x', side='bottom')
        
        # Left status
        left_status = tk.Label(status_bar,
                              text="Business Intelligence System v1.0 • Ready",
                              font=self.ui_config.fonts['caption'],
                              bg=self.ui_config.theme['dark'],
                              fg=self.ui_config.theme['white'])
        left_status.pack(side='left', padx=20)
        
        # Right status
        right_status = tk.Label(status_bar,
                               text="Database: Connected • Memory: Optimal",
                               font=self.ui_config.fonts['caption'],
                               bg=self.ui_config.theme['dark'],
                               fg=self.ui_config.theme['white'])
        right_status.pack(side='right', padx=20)