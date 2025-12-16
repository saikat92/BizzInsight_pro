import tkinter as tk
from tkinter import ttk, font
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
from database.db_connection import get_sqlite_connection
from data_processing.calculations import BusinessCalculations

class Dashboard(ttk.Frame):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.conn = get_sqlite_connection()
        self.calculator = BusinessCalculations()
        
        # Color scheme
        self.colors = {
            'primary': '#1a237e',
            'primary_light': '#534bae',
            'primary_dark': '#000051',
            'secondary': '#00b0ff',
            'success': '#00c853',
            'warning': '#ff9100',
            'error': '#ff5252',
            'dark': '#263238',
            'light': '#eceff1',
            'white': '#ffffff',
            'gray': '#90a4ae',
            'gray_light': '#cfd8dc'
        }
        
        # Fonts
        self.fonts = {
            'h1': ('Segoe UI', 28, 'bold'),
            'h2': ('Segoe UI', 18, 'bold'),
            'h3': ('Segoe UI', 14, 'bold'),
            'body': ('Segoe UI', 11),
            'small': ('Segoe UI', 10),
            'mono': ('Consolas', 10)
        }
        
        # Setup UI
        self.setup_styles()
        self.create_widgets()
        self.load_data()
        
        # Auto-refresh every 60 seconds
        self.auto_refresh_id = self.after(60000, self.auto_refresh)
    
    def setup_styles(self):
        """Configure custom ttk styles for premium look"""
        style = ttk.Style()
        
        # Configure main styles
        style.configure('Dashboard.TFrame', background=self.colors['light'])
        style.configure('Card.TFrame', background=self.colors['white'], 
                       relief='solid', borderwidth=1)
        style.configure('CardHeader.TFrame', background=self.colors['primary'])
        
        # Button styles
        style.configure('Primary.TButton', 
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=self.fonts['body'],
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_light']),
                           ('pressed', self.colors['primary_dark'])])
        
        style.configure('Secondary.TButton',
                       background=self.colors['light'],
                       foreground=self.colors['dark'],
                       font=self.fonts['body'],
                       borderwidth=0)
        
        # Label styles
        style.configure('CardTitle.TLabel',
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=self.fonts['h3'])
        
        style.configure('KPIValue.TLabel',
                       font=('Segoe UI', 36, 'bold'))
        
        style.configure('KPILabel.TLabel',
                       font=self.fonts['small'],
                       foreground=self.colors['gray'])
        
        # Notebook style
        style.configure('Dashboard.TNotebook',
                       background=self.colors['light'],
                       borderwidth=0)
        style.configure('Dashboard.TNotebook.Tab',
                       background=self.colors['white'],
                       padding=[20, 10])
        style.map('Dashboard.TNotebook.Tab',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', self.colors['white'])])
    
    def create_widgets(self):
        """Create all dashboard widgets"""
        # Main container with scrollbar
        main_container = ttk.Frame(self, style='Dashboard.TFrame')
        main_container.pack(fill='both', expand=True)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(main_container, bg=self.colors['light'], 
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient='vertical', 
                                 command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dashboard.TFrame')
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack everything
        canvas.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y')
        
        # Header
        self.create_header(scrollable_frame)
        
        # KPI Cards
        self.create_kpi_cards(scrollable_frame)
        
        # Charts Section
        self.create_charts_section(scrollable_frame)
        
        # Recent Activity & Performance
        self.create_tables_section(scrollable_frame)
        
        # Footer
        self.create_footer(scrollable_frame)
    
    def create_header(self, parent):
        """Create dashboard header"""
        header_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Left side: Title and date
        left_frame = ttk.Frame(header_frame, style='Dashboard.TFrame')
        left_frame.pack(side='left', fill='x', expand=True)
        
        # Title
        title_label = tk.Label(left_frame, text="Business Intelligence Dashboard",
                              font=self.fonts['h1'],
                              bg=self.colors['light'],
                              fg=self.colors['primary'])
        title_label.pack(anchor='w')
        
        # Subtitle
        today = datetime.now().strftime("%B %d, %Y • %I:%M %p")
        subtitle_label = tk.Label(left_frame, text=f"Last updated: {today}",
                                 font=self.fonts['small'],
                                 bg=self.colors['light'],
                                 fg=self.colors['gray'])
        subtitle_label.pack(anchor='w')
        
        # Right side: Controls
        right_frame = ttk.Frame(header_frame, style='Dashboard.TFrame')
        right_frame.pack(side='right')
        
        # Refresh button with icon
        refresh_btn = ttk.Button(right_frame, text="🔄 Refresh", 
                                style='Secondary.TButton',
                                command=self.refresh)
        refresh_btn.pack(side='left', padx=5)
        
        # Export button
        export_btn = ttk.Button(right_frame, text="📊 Export", 
                               style='Secondary.TButton',
                               command=self.export_dashboard)
        export_btn.pack(side='left', padx=5)
        
        # Settings button
        settings_btn = ttk.Button(right_frame, text="⚙️ Settings", 
                                 style='Secondary.TButton')
        settings_btn.pack(side='left', padx=5)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
    
    def create_kpi_cards(self, parent):
        """Create KPI cards section"""
        # Container for KPI cards
        kpi_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        kpi_frame.pack(fill='x', pady=(0, 30))
        
        # Title
        kpi_title = tk.Label(kpi_frame, text="Key Performance Indicators",
                            font=self.fonts['h2'],
                            bg=self.colors['light'],
                            fg=self.colors['dark'])
        kpi_title.pack(anchor='w', pady=(0, 15))
        
        # Cards container
        cards_container = ttk.Frame(kpi_frame, style='Dashboard.TFrame')
        cards_container.pack(fill='x')
        
        # Create 4 cards in a grid
        self.kpi_cards = {}
        kpis = [
            ("revenue", "Total Revenue", "💰", self.colors['success'], "$0"),
            ("customers", "Total Customers", "👥", self.colors['secondary'], "0"),
            ("transactions", "Transactions", "🛒", self.colors['warning'], "0"),
            ("avg_order", "Avg Order Value", "📈", self.colors['primary'], "$0")
        ]
        
        for i, (key, title, icon, color, default_value) in enumerate(kpis):
            card = self.create_kpi_card(cards_container, title, icon, color, default_value)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
            self.kpi_cards[key] = card
            
            # Configure grid column weight
            cards_container.columnconfigure(i, weight=1)
    
    def create_kpi_card(self, parent, title, icon, color, value):
        """Create a single KPI card"""
        card = ttk.Frame(parent, style='Card.TFrame')
        
        # Card header
        header = ttk.Frame(card, style='CardHeader.TFrame')
        header.pack(fill='x')
        
        # Icon
        icon_label = tk.Label(header, text=icon, font=("Segoe UI", 24),
                             bg=self.colors['primary'], fg=self.colors['white'])
        icon_label.pack(side='left', padx=(15, 10), pady=15)
        
        # Title
        title_label = tk.Label(header, text=title, 
                              font=self.fonts['body'],
                              bg=self.colors['primary'],
                              fg=self.colors['white'])
        title_label.pack(side='left', padx=(0, 15), pady=15)
        
        # KPI value
        value_frame = ttk.Frame(card, style='Card.TFrame')
        value_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        value_label = tk.Label(value_frame, text=value,
                              font=self.fonts['h1'],
                              bg=self.colors['white'],
                              fg=color)
        value_label.pack(expand=True)
        
        # Store reference for updating
        card.value_label = value_label
        
        # Add hover effect
        card.bind('<Enter>', lambda e, c=card: self.on_card_hover(c, True))
        card.bind('<Leave>', lambda e, c=card: self.on_card_hover(c, False))
        
        return card
    
    def create_charts_section(self, parent):
        """Create charts section with tabs"""
        charts_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        charts_frame.pack(fill='both', expand=True, pady=(0, 30))
        
        # Title
        charts_title = tk.Label(charts_frame, text="Analytics & Insights",
                               font=self.fonts['h2'],
                               bg=self.colors['light'],
                               fg=self.colors['dark'])
        charts_title.pack(anchor='w', pady=(0, 15))
        
        # Create notebook for chart tabs
        self.chart_notebook = ttk.Notebook(charts_frame, style='Dashboard.TNotebook')
        self.chart_notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_sales_trend_tab()
        self.create_product_performance_tab()
        self.create_customer_analysis_tab()
        self.create_geographic_tab()
        
        # Chart controls
        self.create_chart_controls(charts_frame)
    
    def create_sales_trend_tab(self):
        """Create sales trend chart tab"""
        trend_frame = ttk.Frame(self.chart_notebook, style='Dashboard.TFrame')
        self.chart_notebook.add(trend_frame, text="📈 Sales Trend")
        
        # Create figure for sales trend
        self.sales_fig, self.sales_ax = plt.subplots(figsize=(10, 5))
        self.sales_fig.patch.set_facecolor(self.colors['white'])
        self.sales_ax.set_facecolor(self.colors['white'])
        
        # Embed in tkinter
        self.sales_canvas = FigureCanvasTkAgg(self.sales_fig, trend_frame)
        self.sales_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_product_performance_tab(self):
        """Create product performance chart tab"""
        product_frame = ttk.Frame(self.chart_notebook, style='Dashboard.TFrame')
        self.chart_notebook.add(product_frame, text="📦 Product Performance")
        
        # Create figure for product performance
        self.product_fig, self.product_ax = plt.subplots(figsize=(10, 5))
        self.product_fig.patch.set_facecolor(self.colors['white'])
        self.product_ax.set_facecolor(self.colors['white'])
        
        # Embed in tkinter
        self.product_canvas = FigureCanvasTkAgg(self.product_fig, product_frame)
        self.product_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_customer_analysis_tab(self):
        """Create customer analysis chart tab"""
        customer_frame = ttk.Frame(self.chart_notebook, style='Dashboard.TFrame')
        self.chart_notebook.add(customer_frame, text="👥 Customer Analysis")
        
        # Create figure for customer analysis
        self.customer_fig, self.customer_ax = plt.subplots(1, 2, figsize=(12, 5))
        self.customer_fig.patch.set_facecolor(self.colors['white'])
        for ax in self.customer_ax:
            ax.set_facecolor(self.colors['white'])
        
        # Embed in tkinter
        self.customer_canvas = FigureCanvasTkAgg(self.customer_fig, customer_frame)
        self.customer_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_geographic_tab(self):
        """Create geographic distribution tab"""
        geo_frame = ttk.Frame(self.chart_notebook, style='Dashboard.TFrame')
        self.chart_notebook.add(geo_frame, text="🌍 Geographic")
        
        # Placeholder for geographic chart
        geo_label = tk.Label(geo_frame, text="Geographic distribution chart\n(Can be extended with geographic data)",
                            font=self.fonts['body'],
                            bg=self.colors['white'])
        geo_label.pack(expand=True)
    
    def create_chart_controls(self, parent):
        """Create chart controls"""
        controls_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        controls_frame.pack(fill='x', pady=(10, 0))
        
        # Date range selection
        date_frame = ttk.Frame(controls_frame, style='Dashboard.TFrame')
        date_frame.pack(side='left')
        
        tk.Label(date_frame, text="Date Range:", 
                font=self.fonts['body'],
                bg=self.colors['light']).pack(side='left', padx=(0, 5))
        
        self.date_range = tk.StringVar(value="last_30_days")
        date_options = ["Last 7 Days", "Last 30 Days", "Last Quarter", "Last Year", "Custom"]
        date_combo = ttk.Combobox(date_frame, textvariable=self.date_range,
                                 values=date_options, width=15)
        date_combo.pack(side='left', padx=5)
        
        # Chart type selection
        type_frame = ttk.Frame(controls_frame, style='Dashboard.TFrame')
        type_frame.pack(side='left', padx=20)
        
        tk.Label(type_frame, text="Chart Type:", 
                font=self.fonts['body'],
                bg=self.colors['light']).pack(side='left', padx=(0, 5))
        
        self.chart_style = tk.StringVar(value="line")
        style_combo = ttk.Combobox(type_frame, textvariable=self.chart_style,
                                  values=["Line", "Bar", "Area", "Scatter"], width=10)
        style_combo.pack(side='left', padx=5)
        
        # Update button
        update_btn = ttk.Button(controls_frame, text="Update Charts", 
                               style='Primary.TButton',
                               command=self.update_all_charts)
        update_btn.pack(side='right')
    
    def create_tables_section(self, parent):
        """Create tables section for recent activity and performance"""
        tables_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        tables_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Create two columns
        left_frame = ttk.Frame(tables_frame, style='Dashboard.TFrame')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(tables_frame, style='Dashboard.TFrame')
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Recent Activity Table
        self.create_recent_activity_table(left_frame)
        
        # Top Performers Table
        self.create_top_performers_table(right_frame)
    
    def create_recent_activity_table(self, parent):
        """Create recent activity table"""
        # Header
        header_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="Recent Activity", 
                font=self.fonts['h3'],
                bg=self.colors['light']).pack(side='left')
        
        view_all_btn = ttk.Button(header_frame, text="View All →",
                                 style='Secondary.TButton')
        view_all_btn.pack(side='right')
        
        # Create table
        columns = ('Time', 'Customer', 'Product', 'Amount', 'Status')
        
        # Create Treeview with custom style
        style = ttk.Style()
        style.configure('Recent.Treeview',
                       background=self.colors['white'],
                       foreground=self.colors['dark'],
                       rowheight=35,
                       fieldbackground=self.colors['white'])
        style.map('Recent.Treeview',
                 background=[('selected', self.colors['gray_light'])])
        
        self.recent_tree = ttk.Treeview(parent, columns=columns, 
                                       show='headings', height=8,
                                       style='Recent.Treeview')
        
        # Define headings
        self.recent_tree.heading('Time', text='Time')
        self.recent_tree.heading('Customer', text='Customer')
        self.recent_tree.heading('Product', text='Product')
        self.recent_tree.heading('Amount', text='Amount')
        self.recent_tree.heading('Status', text='Status')
        
        # Define columns
        self.recent_tree.column('Time', width=120)
        self.recent_tree.column('Customer', width=150)
        self.recent_tree.column('Product', width=150)
        self.recent_tree.column('Amount', width=100)
        self.recent_tree.column('Status', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', 
                                 command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.recent_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def create_top_performers_table(self, parent):
        """Create top performers table"""
        # Header
        header_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="Top Performers", 
                font=self.fonts['h3'],
                bg=self.colors['light']).pack(side='left')
        
        # Create table
        columns = ('Rank', 'Product', 'Revenue', 'Growth', 'Trend')
        
        # Create Treeview
        self.top_tree = ttk.Treeview(parent, columns=columns, 
                                    show='headings', height=8,
                                    style='Recent.Treeview')
        
        # Define headings
        self.top_tree.heading('Rank', text='Rank')
        self.top_tree.heading('Product', text='Product')
        self.top_tree.heading('Revenue', text='Revenue')
        self.top_tree.heading('Growth', text='Growth')
        self.top_tree.heading('Trend', text='Trend')
        
        # Define columns
        self.top_tree.column('Rank', width=50)
        self.top_tree.column('Product', width=200)
        self.top_tree.column('Revenue', width=100)
        self.top_tree.column('Growth', width=80)
        self.top_tree.column('Trend', width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', 
                                 command=self.top_tree.yview)
        self.top_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.top_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def create_footer(self, parent):
        """Create dashboard footer"""
        footer_frame = ttk.Frame(parent, style='Dashboard.TFrame')
        footer_frame.pack(fill='x', pady=(20, 0))
        
        # Separator
        ttk.Separator(footer_frame, orient='horizontal').pack(fill='x', pady=(0, 10))
        
        # Status indicators
        status_frame = ttk.Frame(footer_frame, style='Dashboard.TFrame')
        status_frame.pack(fill='x')
        
        # Last update time
        self.last_update_label = tk.Label(status_frame, 
                                         text="Last update: Loading...",
                                         font=self.fonts['small'],
                                         bg=self.colors['light'],
                                         fg=self.colors['gray'])
        self.last_update_label.pack(side='left')
        
        # Data freshness indicator
        self.freshness_label = tk.Label(status_frame, 
                                       text="● Live",
                                       font=self.fonts['small'],
                                       bg=self.colors['light'],
                                       fg=self.colors['success'])
        self.freshness_label.pack(side='right', padx=(0, 20))
        
        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_btn = tk.Checkbutton(status_frame, 
                                         text="Auto-refresh (60s)",
                                         variable=self.auto_refresh_var,
                                         font=self.fonts['small'],
                                         bg=self.colors['light'],
                                         activebackground=self.colors['light'],
                                         command=self.toggle_auto_refresh)
        auto_refresh_btn.pack(side='right', padx=20)
    
    def load_data(self):
        """Load all dashboard data"""
        # Update KPIs in a separate thread
        threading.Thread(target=self.update_kpis, daemon=True).start()
        
        # Update charts
        self.update_all_charts()
        
        # Update tables
        self.update_tables()
        
        # Update timestamp
        self.last_update_label.config(
            text=f"Last update: {datetime.now().strftime('%I:%M:%S %p')}"
        )
    
    def update_kpis(self):
        """Update KPI cards with live data"""
        try:
            # Get sales summary
            summary = self.calculator.get_sales_summary()
            if not summary:
                print("summary is empty")
            
            # Update KPI cards
            self.kpi_cards['revenue'].value_label.config(
                text=f"${summary['total_revenue']:,.0f}"
            )
            self.kpi_cards['customers'].value_label.config(
                text=f"{summary['unique_customers']:,}"
            )
            self.kpi_cards['transactions'].value_label.config(
                text=f"{summary['total_transactions']:,}"
            )
            self.kpi_cards['avg_order'].value_label.config(
                text=f"${summary['avg_transaction_value']:,.2f}"
            )
            
        except Exception as e:
            print(f"Error updating KPIs: {e}")
    
    def update_all_charts(self):
        """Update all charts"""
        self.update_sales_chart()
        self.update_product_chart()
        self.update_customer_chart()
    
    def update_sales_chart(self):
        """Update sales trend chart"""
        try:
            self.sales_ax.clear()
            
            # Get sales trend data
            sales_trend = self.calculator.get_sales_trend('weekly')
            
            if not sales_trend.empty:
                # Plot data
                if self.chart_style.get().lower() == 'bar':
                    bars = self.sales_ax.bar(range(len(sales_trend)), 
                                            sales_trend['revenue'],
                                            color=self.colors['primary'],
                                            alpha=0.7)
                    # Add value labels
                    for bar in bars:
                        height = bar.get_height()
                        self.sales_ax.text(bar.get_x() + bar.get_width()/2.,
                                          height + 0.1,
                                          f'${height:,.0f}',
                                          ha='center', va='bottom',
                                          fontsize=8)
                else:  # Default to line chart
                    self.sales_ax.plot(sales_trend['period'], 
                                      sales_trend['revenue'],
                                      marker='o',
                                      linewidth=2,
                                      color=self.colors['primary'])
                
                # Formatting
                self.sales_ax.set_title('Weekly Sales Trend', 
                                       fontsize=14, 
                                       fontweight='bold',
                                       color=self.colors['dark'])
                self.sales_ax.set_xlabel('Week')
                self.sales_ax.set_ylabel('Revenue ($)')
                self.sales_ax.grid(True, alpha=0.3)
                plt.setp(self.sales_ax.get_xticklabels(), rotation=45)
                
                # Set colors
                self.sales_ax.spines['bottom'].set_color(self.colors['gray'])
                self.sales_ax.spines['left'].set_color(self.colors['gray'])
                self.sales_ax.tick_params(colors=self.colors['dark'])
                self.sales_ax.yaxis.label.set_color(self.colors['dark'])
                self.sales_ax.xaxis.label.set_color(self.colors['dark'])
                self.sales_ax.title.set_color(self.colors['dark'])
                
            self.sales_fig.tight_layout()
            self.sales_canvas.draw()
            
        except Exception as e:
            print(f"Error updating sales chart: {e}")
    
    def update_product_chart(self):
        """Update product performance chart"""
        try:
            self.product_ax.clear()
            
            # Get top products
            top_products = self.calculator.get_top_products(8)
            
            if not top_products.empty:
                # Create horizontal bar chart
                y_pos = range(len(top_products))
                bars = self.product_ax.barh(y_pos, top_products['total_revenue'],
                                           color=[self.colors['primary'], 
                                                  self.colors['primary_light'],
                                                  self.colors['secondary'],
                                                  self.colors['success']] * 2,
                                           alpha=0.8)
                
                # Add product names
                self.product_ax.set_yticks(y_pos)
                self.product_ax.set_yticklabels(top_products['name'])
                
                # Add value labels
                for i, (bar, revenue) in enumerate(zip(bars, top_products['total_revenue'])):
                    self.product_ax.text(bar.get_width() + bar.get_width() * 0.01,
                                        bar.get_y() + bar.get_height()/2,
                                        f'${revenue:,.0f}',
                                        va='center',
                                        fontsize=9)
                
                # Formatting
                self.product_ax.set_title('Top Products by Revenue',
                                         fontsize=14,
                                         fontweight='bold',
                                         color=self.colors['dark'])
                self.product_ax.set_xlabel('Revenue ($)')
                
                # Set colors
                self.product_ax.spines['bottom'].set_color(self.colors['gray'])
                self.product_ax.spines['left'].set_color(self.colors['gray'])
                self.product_ax.tick_params(colors=self.colors['dark'])
                self.product_ax.xaxis.label.set_color(self.colors['dark'])
                self.product_ax.title.set_color(self.colors['dark'])
                
            self.product_fig.tight_layout()
            self.product_canvas.draw()
            
        except Exception as e:
            print(f"Error updating product chart: {e}")
    
    def update_customer_chart(self):
        """Update customer analysis chart"""
        try:
            # Clear axes
            for ax in self.customer_ax:
                ax.clear()
            
            # Get customer segmentation
            customer_data = self.calculator.get_customer_segmentation()
            
            if not customer_data.empty:
                # Pie chart for customer distribution
                colors = [self.colors['primary'], 
                         self.colors['primary_light'],
                         self.colors['secondary'],
                         self.colors['success']]
                
                wedges, texts, autotexts = self.customer_ax[0].pie(
                    customer_data['customer_count'],
                    labels=customer_data['segment'],
                    colors=colors,
                    autopct='%1.1f%%',
                    startangle=90
                )
                
                # Format pie chart
                self.customer_ax[0].set_title('Customer Distribution',
                                             fontsize=12,
                                             fontweight='bold',
                                             color=self.colors['dark'])
                
                # Make autopct text white
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                
                # Bar chart for spending
                bars = self.customer_ax[1].bar(customer_data['segment'],
                                              customer_data['total_spent'],
                                              color=colors,
                                              alpha=0.8)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    self.customer_ax[1].text(bar.get_x() + bar.get_width()/2.,
                                            height + height * 0.01,
                                            f'${height:,.0f}',
                                            ha='center',
                                            va='bottom',
                                            fontsize=9)
                
                # Format bar chart
                self.customer_ax[1].set_title('Total Spending by Segment',
                                             fontsize=12,
                                             fontweight='bold',
                                             color=self.colors['dark'])
                self.customer_ax[1].set_xlabel('Customer Segment')
                self.customer_ax[1].set_ylabel('Total Spent ($)')
                self.customer_ax[1].tick_params(axis='x', rotation=45)
                
                # Set colors for bar chart
                self.customer_ax[1].spines['bottom'].set_color(self.colors['gray'])
                self.customer_ax[1].spines['left'].set_color(self.colors['gray'])
                self.customer_ax[1].tick_params(colors=self.colors['dark'])
                self.customer_ax[1].xaxis.label.set_color(self.colors['dark'])
                self.customer_ax[1].yaxis.label.set_color(self.colors['dark'])
                self.customer_ax[1].title.set_color(self.colors['dark'])
            
            self.customer_fig.tight_layout()
            self.customer_canvas.draw()
            
        except Exception as e:
            print(f"Error updating customer chart: {e}")
    
    def update_tables(self):
        """Update data tables"""
        self.update_recent_activity()
        self.update_top_performers()
    
    def update_recent_activity(self):
        """Update recent activity table"""
        try:
            # Clear existing items
            for item in self.recent_tree.get_children():
                self.recent_tree.delete(item)
            
            # Get recent sales
            query = """
            SELECT 
                s.date || ' ' || time(s.date) as timestamp,
                c.name as customer,
                p.name as product,
                s.amount,
                CASE 
                    WHEN s.amount > 500 THEN 'High'
                    WHEN s.amount > 100 THEN 'Medium'
                    ELSE 'Low'
                END as status
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            JOIN products p ON s.product_id = p.id
            ORDER BY s.date DESC, s.id DESC
            LIMIT 20
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            # Insert data
            for _, row in df.iterrows():
                # Determine tag based on status
                if row['status'] == 'High':
                    tag = 'high'
                elif row['status'] == 'Medium':
                    tag = 'medium'
                else:
                    tag = 'low'
                
                self.recent_tree.insert('', 'end',
                                       values=(row['timestamp'],
                                               row['customer'],
                                               row['product'],
                                               f"${row['amount']:,.2f}",
                                               row['status']),
                                       tags=(tag,))
            
            # Configure tag colors
            self.recent_tree.tag_configure('high', 
                                          background=self.colors['success'] + '20')  # 20 = 12% opacity
            self.recent_tree.tag_configure('medium',
                                          background=self.colors['warning'] + '20')
            self.recent_tree.tag_configure('low',
                                          background=self.colors['error'] + '20')
            
        except Exception as e:
            print(f"Error updating recent activity: {e}")
    
    def update_top_performers(self):
        """Update top performers table"""
        try:
            # Clear existing items
            for item in self.top_tree.get_children():
                self.top_tree.delete(item)
            
            # Get top products with growth
            query = """
            WITH monthly_sales AS (
                SELECT 
                    p.id,
                    p.name,
                    strftime('%Y-%m', s.date) as month,
                    SUM(s.amount) as revenue
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE s.date >= date('now', '-60 days')
                GROUP BY p.id, month
            ),
            current_month AS (
                SELECT 
                    id,
                    name,
                    revenue as current_revenue
                FROM monthly_sales
                WHERE month = strftime('%Y-%m', 'now')
            ),
            previous_month AS (
                SELECT 
                    id,
                    revenue as previous_revenue
                FROM monthly_sales
                WHERE month = strftime('%Y-%m', date('now', '-1 month'))
            )
            SELECT 
                ROW_NUMBER() OVER (ORDER BY cm.current_revenue DESC) as rank,
                cm.name,
                cm.current_revenue,
                CASE 
                    WHEN pm.previous_revenue IS NULL OR pm.previous_revenue = 0 THEN 100
                    ELSE ((cm.current_revenue - pm.previous_revenue) / pm.previous_revenue * 100)
                END as growth
            FROM current_month cm
            LEFT JOIN previous_month pm ON cm.id = pm.id
            ORDER BY cm.current_revenue DESC
            LIMIT 10
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            # Insert data
            for _, row in df.iterrows():
                # Determine trend icon
                growth = row['growth']
                if growth > 20:
                    trend = "📈↑"
                elif growth > 0:
                    trend = "↗"
                elif growth < -10:
                    trend = "📉↓"
                else:
                    trend = "➡"
                
                # Format growth with color indicator
                if growth > 0:
                    growth_text = f"+{growth:.1f}%"
                else:
                    growth_text = f"{growth:.1f}%"
                
                self.top_tree.insert('', 'end',
                                    values=(row['rank'],
                                            row['name'],
                                            f"${row['current_revenue']:,.0f}",
                                            growth_text,
                                            trend))
            
        except Exception as e:
            print(f"Error updating top performers: {e}")
    
    def refresh(self):
        """Refresh all dashboard data"""
        self.load_data()
        self.freshness_label.config(text="● Live", fg=self.colors['success'])
        
        # Show notification
        self.show_notification("Dashboard refreshed successfully!")
    
    def auto_refresh(self):
        """Auto-refresh dashboard"""
        if self.auto_refresh_var.get():
            self.refresh()
            # Schedule next auto-refresh
            self.auto_refresh_id = self.after(60000, self.auto_refresh)
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        if self.auto_refresh_var.get():
            self.auto_refresh()
            self.freshness_label.config(text="● Auto-refresh ON", 
                                       fg=self.colors['success'])
        else:
            if hasattr(self, 'auto_refresh_id'):
                self.after_cancel(self.auto_refresh_id)
            self.freshness_label.config(text="● Auto-refresh OFF", 
                                       fg=self.colors['gray'])
    
    def export_dashboard(self):
        """Export dashboard as image or PDF"""
        # This would be implemented to export the dashboard
        print("Export feature would be implemented here")
    
    def show_notification(self, message):
        """Show a temporary notification"""
        # Create notification frame
        notification = tk.Frame(self, bg=self.colors['success'], height=40)
        notification.place(relx=0.5, rely=0.1, anchor='center')
        
        # Notification label
        label = tk.Label(notification, text=message,
                        bg=self.colors['success'],
                        fg=self.colors['white'],
                        font=self.fonts['body'])
        label.pack(padx=20, pady=10)
        
        # Auto-remove after 3 seconds
        self.after(3000, notification.destroy)
    
    def on_card_hover(self, card, enter):
        """Handle card hover effects"""
        if enter:
            card.configure(style='Card.TFrame')
            # Slight elevation effect
            card.config(relief='raised', borderwidth=2)
        else:
            card.configure(style='Card.TFrame')
            card.config(relief='solid', borderwidth=1)
    
    def destroy(self):
        """Clean up resources"""
        if hasattr(self, 'auto_refresh_id'):
            self.after_cancel(self.auto_refresh_id)
        super().destroy()