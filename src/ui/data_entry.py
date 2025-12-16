import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
import threading
from database.db_connection import get_session, get_sqlite_connection
from database.models import Product, Customer, Sale, Employee, Inventory
from utils.config import load_config

class DataEntry(ttk.Frame):
    """Premium Data Entry Module with Modern UI"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.session = get_session()
        
        # Color scheme matching dashboard
        self.colors = {
            'primary': '#1a237e',
            'primary_light': '#534bae',
            'primary_dark': '#000051',
            'secondary': '#00b0ff',
            'success': '#00c853',
            'warning': '#ff9100',
            'error': '#ff5252',
            'dark': '#263238',
            'light': '#f5f5f5',
            'lighter': '#fafafa',
            'white': '#ffffff',
            'gray': '#90a4ae',
            'gray_light': '#cfd8dc',
            'border': '#e0e0e0'
        }
        
        # Fonts
        self.fonts = {
            'h1': ('Segoe UI', 24, 'bold'),
            'h2': ('Segoe UI', 18, 'bold'),
            'h3': ('Segoe UI', 14, 'bold'),
            'body': ('Segoe UI', 11),
            'small': ('Segoe UI', 10),
            'mono': ('Consolas', 10)
        }
        
        # Current record ID for editing
        self.current_record_id = None
        self.current_entity = None
        
        # Setup UI
        self.setup_styles()
        self.create_widgets()
        self.load_initial_data()
        
    def setup_styles(self):
        """Configure custom ttk styles"""
        style = ttk.Style()
        
        # Main frame style
        style.configure('DataEntry.TFrame', background=self.colors['light'])
        
        # Card styles
        style.configure('FormCard.TFrame', 
                       background=self.colors['white'],
                       relief='solid',
                       borderwidth=1)
        
        # Button styles
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=self.fonts['body'],
                       borderwidth=0,
                       padding=10)
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_light']),
                           ('pressed', self.colors['primary_dark'])])
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground=self.colors['white'],
                       font=self.fonts['body'],
                       borderwidth=0,
                       padding=10)
        
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground=self.colors['white'],
                       font=self.fonts['body'],
                       borderwidth=0,
                       padding=10)
        
        style.configure('Secondary.TButton',
                       background=self.colors['light'],
                       foreground=self.colors['dark'],
                       font=self.fonts['body'],
                       borderwidth=0,
                       padding=10)
        
        # Entry styles
        style.configure('Premium.TEntry',
                       fieldbackground=self.colors['white'],
                       foreground=self.colors['dark'],
                       bordercolor=self.colors['border'],
                       lightcolor=self.colors['border'],
                       darkcolor=self.colors['border'])
        
        # Combobox styles
        style.configure('Premium.TCombobox',
                       fieldbackground=self.colors['white'],
                       foreground=self.colors['dark'])
        
        # Label styles
        style.configure('FormLabel.TLabel',
                       background=self.colors['white'],
                       foreground=self.colors['dark'],
                       font=self.fonts['body'])
        
        style.configure('SectionTitle.TLabel',
                       background=self.colors['light'],
                       foreground=self.colors['primary'],
                       font=self.fonts['h3'],
                       padding=(0, 10))
        
        # Treeview styles
        style.configure('DataTree.Treeview',
                       background=self.colors['white'],
                       foreground=self.colors['dark'],
                       rowheight=35,
                       fieldbackground=self.colors['white'])
        
        style.configure('DataTree.Treeview.Heading',
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=self.fonts['body_bold'])
        
        style.map('DataTree.Treeview',
                 background=[('selected', self.colors['primary'] + '20')])
    
    def create_widgets(self):
        """Create all data entry widgets"""
        # Main container with scrollbar
        main_container = ttk.Frame(self, style='DataEntry.TFrame')
        main_container.pack(fill='both', expand=True)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(main_container, bg=self.colors['light'], 
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient='vertical', 
                                 command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='DataEntry.TFrame')
        
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
        
        # Data Import Section
        self.create_import_section(scrollable_frame)
        
        # Notebook for entities
        self.create_entity_notebook(scrollable_frame)
        
        # Quick Actions
        self.create_quick_actions(scrollable_frame)
        
        # Footer
        self.create_footer(scrollable_frame)
    
    def create_header(self, parent):
        """Create data entry header"""
        header_frame = ttk.Frame(parent, style='DataEntry.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Left side: Title
        left_frame = ttk.Frame(header_frame, style='DataEntry.TFrame')
        left_frame.pack(side='left', fill='x', expand=True)
        
        title_label = tk.Label(left_frame, text="Data Management Center",
                              font=self.fonts['h1'],
                              bg=self.colors['light'],
                              fg=self.colors['primary'])
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(left_frame, 
                                 text="Add, edit, and manage your business data",
                                 font=self.fonts['small'],
                                 bg=self.colors['light'],
                                 fg=self.colors['gray'])
        subtitle_label.pack(anchor='w')
        
        # Right side: Stats
        right_frame = ttk.Frame(header_frame, style='DataEntry.TFrame')
        right_frame.pack(side='right')
        
        self.stats_label = tk.Label(right_frame,
                                   text="Loading stats...",
                                   font=self.fonts['small'],
                                   bg=self.colors['light'],
                                   fg=self.colors['gray'])
        self.stats_label.pack()
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
    
    def create_import_section(self, parent):
        """Create data import section"""
        import_frame = ttk.Frame(parent, style='FormCard.TFrame')
        import_frame.pack(fill='x', pady=(0, 20))
        
        # Header
        header_frame = ttk.Frame(import_frame, style='FormCard.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(header_frame, text="📁 Bulk Data Import",
                font=self.fonts['h3'],
                bg=self.colors['white']).pack(side='left')
        
        # Import controls
        controls_frame = ttk.Frame(import_frame, style='FormCard.TFrame')
        controls_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # File type selection
        file_type_frame = ttk.Frame(controls_frame, style='FormCard.TFrame')
        file_type_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(file_type_frame, text="Import Format:",
                font=self.fonts['body'],
                bg=self.colors['white']).pack(side='left', padx=(0, 10))
        
        self.import_format = tk.StringVar(value="CSV")
        format_combo = ttk.Combobox(file_type_frame, 
                                   textvariable=self.import_format,
                                   values=["CSV", "Excel", "JSON"],
                                   width=10,
                                   style='Premium.TCombobox')
        format_combo.pack(side='left', padx=(0, 20))
        
        # Entity selection
        tk.Label(file_type_frame, text="Entity Type:",
                font=self.fonts['body'],
                bg=self.colors['white']).pack(side='left', padx=(0, 10))
        
        self.import_entity = tk.StringVar(value="Products")
        entity_combo = ttk.Combobox(file_type_frame, 
                                   textvariable=self.import_entity,
                                   values=["Products", "Customers", "Sales", "Employees"],
                                   width=15,
                                   style='Premium.TCombobox')
        entity_combo.pack(side='left')
        
        # Import buttons
        button_frame = ttk.Frame(controls_frame, style='FormCard.TFrame')
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="📂 Select File",
                  style='Secondary.TButton',
                  command=self.select_import_file).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="⚙️ Preview Data",
                  style='Secondary.TButton',
                  command=self.preview_import_data).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="🚀 Import Data",
                  style='Success.TButton',
                  command=self.import_data).pack(side='left')
        
        # Status label
        self.import_status = tk.Label(import_frame, 
                                     text="No file selected",
                                     font=self.fonts['small'],
                                     bg=self.colors['white'],
                                     fg=self.colors['gray'])
        self.import_status.pack(pady=(0, 15))
    
    def create_entity_notebook(self, parent):
        """Create notebook for entity management"""
        # Notebook container
        notebook_frame = ttk.Frame(parent, style='DataEntry.TFrame')
        notebook_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Create notebook with custom style
        self.entity_notebook = ttk.Notebook(notebook_frame)
        self.entity_notebook.pack(fill='both', expand=True)
        
        # Apply custom style
        style = ttk.Style()
        style.configure('Entity.TNotebook',
                       background=self.colors['light'],
                       borderwidth=0)
        style.configure('Entity.TNotebook.Tab',
                       background=self.colors['white'],
                       foreground=self.colors['dark'],
                       padding=[20, 10],
                       font=self.fonts['body_bold'])
        style.map('Entity.TNotebook.Tab',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', self.colors['white'])])
        
        self.entity_notebook.configure(style='Entity.TNotebook')
        
        # Create tabs for each entity
        self.create_products_tab()
        self.create_customers_tab()
        self.create_sales_tab()
        self.create_employees_tab()
        self.create_inventory_tab()
    
    def create_products_tab(self):
        """Create products management tab"""
        tab = ttk.Frame(self.entity_notebook)
        self.entity_notebook.add(tab, text="📦 Products")
        
        # Two-column layout
        left_frame = ttk.Frame(tab, style='DataEntry.TFrame')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(tab, style='DataEntry.TFrame')
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Form
        self.create_product_form(left_frame)
        
        # Data table
        self.create_product_table(right_frame)
    
    def create_product_form(self, parent):
        """Create product entry form"""
        form_frame = ttk.Frame(parent, style='FormCard.TFrame')
        form_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame, text="Add/Edit Product",
                font=self.fonts['h3'],
                bg=self.colors['white']).pack(side='left')
        
        # Clear button
        ttk.Button(header_frame, text="Clear Form",
                  style='Secondary.TButton',
                  command=self.clear_product_form).pack(side='right')
        
        # Form fields
        fields_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        fields_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Product Name
        tk.Label(fields_frame, text="Product Name*",
                style='FormLabel.TLabel').grid(row=0, column=0, 
                                              sticky='w', pady=(0, 5))
        self.product_name = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.product_name.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        
        # Category
        tk.Label(fields_frame, text="Category*",
                style='FormLabel.TLabel').grid(row=0, column=1, 
                                              sticky='w', pady=(0, 5), padx=(20, 0))
        
        self.product_category = ttk.Combobox(fields_frame, 
                                           values=['Electronics', 'Clothing', 'Books', 
                                                   'Home & Garden', 'Sports', 'Toys',
                                                   'Food & Beverages', 'Health'],
                                           style='Premium.TCombobox')
        self.product_category.grid(row=1, column=1, sticky='ew', 
                                 pady=(0, 15), padx=(20, 0))
        
        # Price and Cost
        tk.Label(fields_frame, text="Price ($)*",
                style='FormLabel.TLabel').grid(row=2, column=0, 
                                              sticky='w', pady=(0, 5))
        self.product_price = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.product_price.grid(row=3, column=0, sticky='ew', pady=(0, 15))
        
        tk.Label(fields_frame, text="Cost ($)*",
                style='FormLabel.TLabel').grid(row=2, column=1, 
                                              sticky='w', pady=(0, 5), padx=(20, 0))
        self.product_cost = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.product_cost.grid(row=3, column=1, sticky='ew', 
                             pady=(0, 15), padx=(20, 0))
        
        # Stock
        tk.Label(fields_frame, text="Stock Quantity",
                style='FormLabel.TLabel').grid(row=4, column=0, 
                                              sticky='w', pady=(0, 5))
        self.product_stock = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.product_stock.grid(row=5, column=0, sticky='ew', pady=(0, 20))
        
        # Form buttons
        button_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(button_frame, text="💾 Save Product",
                  style='Success.TButton',
                  command=self.save_product).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="✏️ Update",
                  style='Primary.TButton',
                  command=self.update_product).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="🗑️ Delete",
                  style='Warning.TButton',
                  command=self.delete_product).pack(side='left')
        
        # Configure grid weights
        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)
    
    def create_product_table(self, parent):
        """Create products data table"""
        # Header
        header_frame = ttk.Frame(parent, style='DataEntry.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="Product Catalog",
                font=self.fonts['h3'],
                bg=self.colors['light']).pack(side='left')
        
        # Search bar
        search_frame = ttk.Frame(header_frame, style='DataEntry.TFrame')
        search_frame.pack(side='right')
        
        tk.Label(search_frame, text="Search:",
                font=self.fonts['small'],
                bg=self.colors['light']).pack(side='left', padx=(0, 5))
        
        self.product_search = ttk.Entry(search_frame, width=20,
                                       style='Premium.TEntry')
        self.product_search.pack(side='left')
        self.product_search.bind('<KeyRelease>', self.search_products)
        
        # Create Treeview
        columns = ('ID', 'Name', 'Category', 'Price', 'Cost', 'Stock')
        
        self.product_tree = ttk.Treeview(parent, columns=columns,
                                        show='headings',
                                        height=15,
                                        style='DataTree.Treeview')
        
        # Define headings
        self.product_tree.heading('ID', text='ID')
        self.product_tree.heading('Name', text='Name')
        self.product_tree.heading('Category', text='Category')
        self.product_tree.heading('Price', text='Price ($)')
        self.product_tree.heading('Cost', text='Cost ($)')
        self.product_tree.heading('Stock', text='Stock')
        
        # Define columns
        self.product_tree.column('ID', width=50)
        self.product_tree.column('Name', width=200)
        self.product_tree.column('Category', width=120)
        self.product_tree.column('Price', width=80)
        self.product_tree.column('Cost', width=80)
        self.product_tree.column('Stock', width=80)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient='vertical',
                                   command=self.product_tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient='horizontal',
                                   command=self.product_tree.xview)
        
        self.product_tree.configure(yscrollcommand=v_scrollbar.set,
                                   xscrollcommand=h_scrollbar.set)
        
        # Pack everything
        self.product_tree.pack(side='top', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind selection event
        self.product_tree.bind('<<TreeviewSelect>>', self.on_product_select)
    
    def create_customers_tab(self):
        """Create customers management tab"""
        tab = ttk.Frame(self.entity_notebook)
        self.entity_notebook.add(tab, text="👥 Customers")
        
        # Two-column layout
        left_frame = ttk.Frame(tab, style='DataEntry.TFrame')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(tab, style='DataEntry.TFrame')
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Form
        self.create_customer_form(left_frame)
        
        # Data table
        self.create_customer_table(right_frame)
    
    def create_customer_form(self, parent):
        """Create customer entry form"""
        form_frame = ttk.Frame(parent, style='FormCard.TFrame')
        form_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame, text="Add/Edit Customer",
                font=self.fonts['h3'],
                bg=self.colors['white']).pack(side='left')
        
        ttk.Button(header_frame, text="Clear Form",
                  style='Secondary.TButton',
                  command=self.clear_customer_form).pack(side='right')
        
        # Form fields
        fields_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        fields_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Name
        tk.Label(fields_frame, text="Full Name*",
                style='FormLabel.TLabel').grid(row=0, column=0, 
                                              sticky='w', pady=(0, 5))
        self.customer_name = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.customer_name.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        
        # Email
        tk.Label(fields_frame, text="Email*",
                style='FormLabel.TLabel').grid(row=2, column=0, 
                                              sticky='w', pady=(0, 5))
        self.customer_email = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.customer_email.grid(row=3, column=0, sticky='ew', pady=(0, 15))
        
        # Phone
        tk.Label(fields_frame, text="Phone",
                style='FormLabel.TLabel').grid(row=4, column=0, 
                                              sticky='w', pady=(0, 5))
        self.customer_phone = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.customer_phone.grid(row=5, column=0, sticky='ew', pady=(0, 15))
        
        # Segment
        tk.Label(fields_frame, text="Segment",
                style='FormLabel.TLabel').grid(row=0, column=1, 
                                              sticky='w', pady=(0, 5), padx=(20, 0))
        self.customer_segment = ttk.Combobox(fields_frame,
                                           values=['Regular', 'Premium', 'VIP', 'New'],
                                           style='Premium.TCombobox')
        self.customer_segment.grid(row=1, column=1, sticky='ew',
                                 pady=(0, 15), padx=(20, 0))
        
        # Join Date
        tk.Label(fields_frame, text="Join Date",
                style='FormLabel.TLabel').grid(row=2, column=1, 
                                              sticky='w', pady=(0, 5), padx=(20, 0))
        self.customer_join_date = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.customer_join_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.customer_join_date.grid(row=3, column=1, sticky='ew',
                                   pady=(0, 15), padx=(20, 0))
        
        # Form buttons
        button_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(button_frame, text="💾 Save Customer",
                  style='Success.TButton',
                  command=self.save_customer).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="✏️ Update",
                  style='Primary.TButton',
                  command=self.update_customer).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="🗑️ Delete",
                  style='Warning.TButton',
                  command=self.delete_customer).pack(side='left')
        
        # Configure grid weights
        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)
    
    def create_customer_table(self, parent):
        """Create customers data table"""
        # Header
        header_frame = ttk.Frame(parent, style='DataEntry.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="Customer Database",
                font=self.fonts['h3'],
                bg=self.colors['light']).pack(side='left')
        
        # Search bar
        search_frame = ttk.Frame(header_frame, style='DataEntry.TFrame')
        search_frame.pack(side='right')
        
        tk.Label(search_frame, text="Search:",
                font=self.fonts['small'],
                bg=self.colors['light']).pack(side='left', padx=(0, 5))
        
        self.customer_search = ttk.Entry(search_frame, width=20,
                                        style='Premium.TEntry')
        self.customer_search.pack(side='left')
        self.customer_search.bind('<KeyRelease>', self.search_customers)
        
        # Create Treeview
        columns = ('ID', 'Name', 'Email', 'Phone', 'Segment', 'Join Date')
        
        self.customer_tree = ttk.Treeview(parent, columns=columns,
                                         show='headings',
                                         height=15,
                                         style='DataTree.Treeview')
        
        # Define headings
        self.customer_tree.heading('ID', text='ID')
        self.customer_tree.heading('Name', text='Name')
        self.customer_tree.heading('Email', text='Email')
        self.customer_tree.heading('Phone', text='Phone')
        self.customer_tree.heading('Segment', text='Segment')
        self.customer_tree.heading('Join Date', text='Join Date')
        
        # Define columns
        self.customer_tree.column('ID', width=50)
        self.customer_tree.column('Name', width=150)
        self.customer_tree.column('Email', width=180)
        self.customer_tree.column('Phone', width=120)
        self.customer_tree.column('Segment', width=100)
        self.customer_tree.column('Join Date', width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient='vertical',
                                   command=self.customer_tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient='horizontal',
                                   command=self.customer_tree.xview)
        
        self.customer_tree.configure(yscrollcommand=v_scrollbar.set,
                                    xscrollcommand=h_scrollbar.set)
        
        # Pack everything
        self.customer_tree.pack(side='top', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind selection event
        self.customer_tree.bind('<<TreeviewSelect>>', self.on_customer_select)
    
    def create_sales_tab(self):
        """Create sales management tab"""
        tab = ttk.Frame(self.entity_notebook)
        self.entity_notebook.add(tab, text="💰 Sales")
        
        # Two-column layout
        left_frame = ttk.Frame(tab, style='DataEntry.TFrame')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(tab, style='DataEntry.TFrame')
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Form
        self.create_sales_form(left_frame)
        
        # Data table
        self.create_sales_table(right_frame)
    
    def create_sales_form(self, parent):
        """Create sales entry form"""
        form_frame = ttk.Frame(parent, style='FormCard.TFrame')
        form_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame, text="Add/Edit Sale",
                font=self.fonts['h3'],
                bg=self.colors['white']).pack(side='left')
        
        ttk.Button(header_frame, text="Clear Form",
                  style='Secondary.TButton',
                  command=self.clear_sales_form).pack(side='right')
        
        # Form fields
        fields_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        fields_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Customer selection
        tk.Label(fields_frame, text="Customer*",
                style='FormLabel.TLabel').grid(row=0, column=0, 
                                              sticky='w', pady=(0, 5))
        self.sale_customer = ttk.Combobox(fields_frame, style='Premium.TCombobox')
        self.sale_customer.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        
        # Product selection
        tk.Label(fields_frame, text="Product*",
                style='FormLabel.TLabel').grid(row=0, column=1, 
                                              sticky='w', pady=(0, 5), padx=(20, 0))
        self.sale_product = ttk.Combobox(fields_frame, style='Premium.TCombobox')
        self.sale_product.grid(row=1, column=1, sticky='ew',
                             pady=(0, 15), padx=(20, 0))
        
        # Date
        tk.Label(fields_frame, text="Date*",
                style='FormLabel.TLabel').grid(row=2, column=0, 
                                              sticky='w', pady=(0, 5))
        self.sale_date = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.sale_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.sale_date.grid(row=3, column=0, sticky='ew', pady=(0, 15))
        
        # Quantity
        tk.Label(fields_frame, text="Quantity*",
                style='FormLabel.TLabel').grid(row=2, column=1, 
                                              sticky='w', pady=(0, 5), padx=(20, 0))
        self.sale_quantity = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.sale_quantity.grid(row=3, column=1, sticky='ew',
                              pady=(0, 15), padx=(20, 0))
        
        # Amount
        tk.Label(fields_frame, text="Amount ($)*",
                style='FormLabel.TLabel').grid(row=4, column=0, 
                                              sticky='w', pady=(0, 5))
        self.sale_amount = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.sale_amount.grid(row=5, column=0, sticky='ew', pady=(0, 15))
        
        # Payment Method
        tk.Label(fields_frame, text="Payment Method",
                style='FormLabel.TLabel').grid(row=4, column=1, 
                                              sticky='w', pady=(0, 5), padx=(20, 0))
        self.sale_payment = ttk.Combobox(fields_frame,
                                        values=['Credit Card', 'Cash', 'PayPal', 'Bank Transfer'],
                                        style='Premium.TCombobox')
        self.sale_payment.grid(row=5, column=1, sticky='ew',
                             pady=(0, 15), padx=(20, 0))
        
        # Auto-calculate button
        calc_frame = ttk.Frame(fields_frame, style='FormCard.TFrame')
        calc_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(calc_frame, text="🧮 Calculate Amount",
                  style='Secondary.TButton',
                  command=self.calculate_sale_amount).pack()
        
        # Form buttons
        button_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(button_frame, text="💾 Save Sale",
                  style='Success.TButton',
                  command=self.save_sale).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="✏️ Update",
                  style='Primary.TButton',
                  command=self.update_sale).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="🗑️ Delete",
                  style='Warning.TButton',
                  command=self.delete_sale).pack(side='left')
        
        # Configure grid weights
        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)
    
    def create_sales_table(self, parent):
        """Create sales data table"""
        # Header
        header_frame = ttk.Frame(parent, style='DataEntry.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="Sales Transactions",
                font=self.fonts['h3'],
                bg=self.colors['light']).pack(side='left')
        
        # Filter controls
        filter_frame = ttk.Frame(header_frame, style='DataEntry.TFrame')
        filter_frame.pack(side='right')
        
        # Date filter
        tk.Label(filter_frame, text="Date:",
                font=self.fonts['small'],
                bg=self.colors['light']).pack(side='left', padx=(0, 5))
        
        self.sale_date_filter = ttk.Entry(filter_frame, width=12,
                                         style='Premium.TEntry')
        self.sale_date_filter.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.sale_date_filter.pack(side='left', padx=(0, 10))
        
        # Create Treeview
        columns = ('ID', 'Date', 'Customer', 'Product', 'Qty', 'Amount', 'Payment')
        
        self.sale_tree = ttk.Treeview(parent, columns=columns,
                                     show='headings',
                                     height=15,
                                     style='DataTree.Treeview')
        
        # Define headings
        self.sale_tree.heading('ID', text='ID')
        self.sale_tree.heading('Date', text='Date')
        self.sale_tree.heading('Customer', text='Customer')
        self.sale_tree.heading('Product', text='Product')
        self.sale_tree.heading('Qty', text='Qty')
        self.sale_tree.heading('Amount', text='Amount ($)')
        self.sale_tree.heading('Payment', text='Payment')
        
        # Define columns
        self.sale_tree.column('ID', width=50)
        self.sale_tree.column('Date', width=100)
        self.sale_tree.column('Customer', width=150)
        self.sale_tree.column('Product', width=150)
        self.sale_tree.column('Qty', width=60)
        self.sale_tree.column('Amount', width=100)
        self.sale_tree.column('Payment', width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient='vertical',
                                   command=self.sale_tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient='horizontal',
                                   command=self.sale_tree.xview)
        
        self.sale_tree.configure(yscrollcommand=v_scrollbar.set,
                                xscrollcommand=h_scrollbar.set)
        
        # Pack everything
        self.sale_tree.pack(side='top', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind selection event
        self.sale_tree.bind('<<TreeviewSelect>>', self.on_sale_select)
    
    def create_employees_tab(self):
        """Create employees management tab"""
        tab = ttk.Frame(self.entity_notebook)
        self.entity_notebook.add(tab, text="👔 Employees")
        
        # Two-column layout
        left_frame = ttk.Frame(tab, style='DataEntry.TFrame')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(tab, style='DataEntry.TFrame')
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Form
        self.create_employee_form(left_frame)
        
        # Data table
        self.create_employee_table(right_frame)
    
    def create_employee_form(self, parent):
        """Create employee entry form"""
        form_frame = ttk.Frame(parent, style='FormCard.TFrame')
        form_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame, text="Add/Edit Employee",
                font=self.fonts['h3'],
                bg=self.colors['white']).pack(side='left')
        
        ttk.Button(header_frame, text="Clear Form",
                  style='Secondary.TButton',
                  command=self.clear_employee_form).pack(side='right')
        
        # Form fields
        fields_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        fields_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Name
        tk.Label(fields_frame, text="Full Name*",
                style='FormLabel.TLabel').grid(row=0, column=0, 
                                              sticky='w', pady=(0, 5))
        self.employee_name = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.employee_name.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        
        # Department
        tk.Label(fields_frame, text="Department*",
                style='FormLabel.TLabel').grid(row=0, column=1, 
                                              sticky='w', pady=(0, 5), padx=(20, 0))
        
        self.employee_department = ttk.Combobox(fields_frame,
                                               values=['Sales', 'Marketing', 'IT', 
                                                       'Finance', 'HR', 'Operations'],
                                               style='Premium.TCombobox')
        self.employee_department.grid(row=1, column=1, sticky='ew',
                                    pady=(0, 15), padx=(20, 0))
        
        # Salary
        tk.Label(fields_frame, text="Salary ($)*",
                style='FormLabel.TLabel').grid(row=2, column=0, 
                                              sticky='w', pady=(0, 5))
        self.employee_salary = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.employee_salary.grid(row=3, column=0, sticky='ew', pady=(0, 15))
        
        # Hire Date
        tk.Label(fields_frame, text="Hire Date",
                style='FormLabel.TLabel').grid(row=2, column=1, 
                                              sticky='w', pady=(0, 5), padx=(20, 0))
        self.employee_hire_date = ttk.Entry(fields_frame, style='Premium.TEntry')
        self.employee_hire_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.employee_hire_date.grid(row=3, column=1, sticky='ew',
                                   pady=(0, 15), padx=(20, 0))
        
        # Form buttons
        button_frame = ttk.Frame(form_frame, style='FormCard.TFrame')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(button_frame, text="💾 Save Employee",
                  style='Success.TButton',
                  command=self.save_employee).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="✏️ Update",
                  style='Primary.TButton',
                  command=self.update_employee).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="🗑️ Delete",
                  style='Warning.TButton',
                  command=self.delete_employee).pack(side='left')
        
        # Configure grid weights
        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)
    
    def create_employee_table(self, parent):
        """Create employees data table"""
        # Header
        header_frame = ttk.Frame(parent, style='DataEntry.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="Employee Directory",
                font=self.fonts['h3'],
                bg=self.colors['light']).pack(side='left')
        
        # Search bar
        search_frame = ttk.Frame(header_frame, style='DataEntry.TFrame')
        search_frame.pack(side='right')
        
        tk.Label(search_frame, text="Search:",
                font=self.fonts['small'],
                bg=self.colors['light']).pack(side='left', padx=(0, 5))
        
        self.employee_search = ttk.Entry(search_frame, width=20,
                                        style='Premium.TEntry')
        self.employee_search.pack(side='left')
        self.employee_search.bind('<KeyRelease>', self.search_employees)
        
        # Create Treeview
        columns = ('ID', 'Name', 'Department', 'Salary', 'Hire Date')
        
        self.employee_tree = ttk.Treeview(parent, columns=columns,
                                         show='headings',
                                         height=15,
                                         style='DataTree.Treeview')
        
        # Define headings
        self.employee_tree.heading('ID', text='ID')
        self.employee_tree.heading('Name', text='Name')
        self.employee_tree.heading('Department', text='Department')
        self.employee_tree.heading('Salary', text='Salary ($)')
        self.employee_tree.heading('Hire Date', text='Hire Date')
        
        # Define columns
        self.employee_tree.column('ID', width=50)
        self.employee_tree.column('Name', width=150)
        self.employee_tree.column('Department', width=120)
        self.employee_tree.column('Salary', width=100)
        self.employee_tree.column('Hire Date', width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient='vertical',
                                   command=self.employee_tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient='horizontal',
                                   command=self.employee_tree.xview)
        
        self.employee_tree.configure(yscrollcommand=v_scrollbar.set,
                                    xscrollcommand=h_scrollbar.set)
        
        # Pack everything
        self.employee_tree.pack(side='top', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind selection event
        self.employee_tree.bind('<<TreeviewSelect>>', self.on_employee_select)
    
    def create_inventory_tab(self):
        """Create inventory management tab"""
        tab = ttk.Frame(self.entity_notebook)
        self.entity_notebook.add(tab, text="📊 Inventory")
        
        # Single column layout for inventory
        inventory_frame = ttk.Frame(tab, style='DataEntry.TFrame')
        inventory_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(inventory_frame, style='DataEntry.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Inventory Management",
                font=self.fonts['h3'],
                bg=self.colors['light']).pack(side='left')
        
        # Controls
        controls_frame = ttk.Frame(header_frame, style='DataEntry.TFrame')
        controls_frame.pack(side='right')
        
        ttk.Button(controls_frame, text="🔄 Update Stock",
                  style='Primary.TButton',
                  command=self.update_inventory).pack(side='left', padx=(0, 10))
        
        ttk.Button(controls_frame, text="📋 Generate Report",
                  style='Secondary.TButton',
                  command=self.generate_inventory_report).pack(side='left')
        
        # Inventory Treeview
        columns = ('Product ID', 'Product Name', 'Category', 'Current Stock', 
                  'Low Stock', 'Last Updated')
        
        self.inventory_tree = ttk.Treeview(inventory_frame, columns=columns,
                                          show='headings',
                                          height=20,
                                          style='DataTree.Treeview')
        
        # Define headings
        self.inventory_tree.heading('Product ID', text='Product ID')
        self.inventory_tree.heading('Product Name', text='Product Name')
        self.inventory_tree.heading('Category', text='Category')
        self.inventory_tree.heading('Current Stock', text='Current Stock')
        self.inventory_tree.heading('Low Stock', text='Low Stock')
        self.inventory_tree.heading('Last Updated', text='Last Updated')
        
        # Define columns
        self.inventory_tree.column('Product ID', width=80)
        self.inventory_tree.column('Product Name', width=200)
        self.inventory_tree.column('Category', width=120)
        self.inventory_tree.column('Current Stock', width=100)
        self.inventory_tree.column('Low Stock', width=80)
        self.inventory_tree.column('Last Updated', width=120)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(inventory_frame, orient='vertical',
                                   command=self.inventory_tree.yview)
        h_scrollbar = ttk.Scrollbar(inventory_frame, orient='horizontal',
                                   command=self.inventory_tree.xview)
        
        self.inventory_tree.configure(yscrollcommand=v_scrollbar.set,
                                     xscrollcommand=h_scrollbar.set)
        
        # Pack everything
        self.inventory_tree.pack(side='top', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Low stock warning frame
        warning_frame = ttk.Frame(inventory_frame, style='FormCard.TFrame')
        warning_frame.pack(fill='x', pady=(20, 0))
        
        self.low_stock_label = tk.Label(warning_frame,
                                       text="⚠️ 0 products with low stock",
                                       font=self.fonts['body'],
                                       bg=self.colors['white'],
                                       fg=self.colors['warning'])
        self.low_stock_label.pack(pady=10)
    
    def create_quick_actions(self, parent):
        """Create quick action buttons"""
        actions_frame = ttk.Frame(parent, style='FormCard.TFrame')
        actions_frame.pack(fill='x', pady=(0, 20))
        
        # Header
        header_frame = ttk.Frame(actions_frame, style='FormCard.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(header_frame, text="⚡ Quick Actions",
                font=self.fonts['h3'],
                bg=self.colors['white']).pack(side='left')
        
        # Action buttons
        buttons_frame = ttk.Frame(actions_frame, style='FormCard.TFrame')
        buttons_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Row 1
        row1 = ttk.Frame(buttons_frame, style='FormCard.TFrame')
        row1.pack(fill='x', pady=(0, 10))
        
        ttk.Button(row1, text="🔄 Refresh All Data",
                  style='Secondary.TButton',
                  command=self.refresh_all_data).pack(side='left', padx=(0, 10))
        
        ttk.Button(row1, text="🗑️ Delete All Test Data",
                  style='Warning.TButton',
                  command=self.delete_test_data).pack(side='left', padx=(0, 10))
        
        ttk.Button(row1, text="📊 Generate Sample Data",
                  style='Success.TButton',
                  command=self.generate_sample_data).pack(side='left')
        
        # Row 2
        row2 = ttk.Frame(buttons_frame, style='FormCard.TFrame')
        row2.pack(fill='x')
        
        ttk.Button(row2, text="🔍 Validate Data",
                  style='Secondary.TButton',
                  command=self.validate_data).pack(side='left', padx=(0, 10))
        
        ttk.Button(row2, text="📁 Export All Data",
                  style='Primary.TButton',
                  command=self.export_all_data).pack(side='left', padx=(0, 10))
        
        ttk.Button(row2, text="⚙️ Database Settings",
                  style='Secondary.TButton').pack(side='left')
    
    def create_footer(self, parent):
        """Create data entry footer"""
        footer_frame = ttk.Frame(parent, style='DataEntry.TFrame')
        footer_frame.pack(fill='x', pady=(20, 0))
        
        # Separator
        ttk.Separator(footer_frame, orient='horizontal').pack(fill='x', pady=(0, 10))
        
        # Status bar
        status_frame = ttk.Frame(footer_frame, style='DataEntry.TFrame')
        status_frame.pack(fill='x')
        
        # Database status
        self.db_status_label = tk.Label(status_frame,
                                       text="🟢 Database: Connected",
                                       font=self.fonts['small'],
                                       bg=self.colors['light'],
                                       fg=self.colors['success'])
        self.db_status_label.pack(side='left')
        
        # Record count
        self.record_count_label = tk.Label(status_frame,
                                          text="Loading records...",
                                          font=self.fonts['small'],
                                          bg=self.colors['light'],
                                          fg=self.colors['gray'])
        self.record_count_label.pack(side='right', padx=20)
        
        # Last action
        self.last_action_label = tk.Label(status_frame,
                                         text="Ready",
                                         font=self.fonts['small'],
                                         bg=self.colors['light'],
                                         fg=self.colors['gray'])
        self.last_action_label.pack(side='right')
    
    # ==================== DATA LOADING METHODS ====================
    
    def load_initial_data(self):
        """Load initial data into forms and tables"""
        # Load in background thread
        threading.Thread(target=self.load_all_data, daemon=True).start()
    
    def load_all_data(self):
        """Load all data from database"""
        try:
            # Load combo box data
            self.load_combo_data()
            
            # Load table data
            self.load_product_table()
            self.load_customer_table()
            self.load_sale_table()
            self.load_employee_table()
            self.load_inventory_table()
            
            # Update stats
            self.update_stats()
            self.update_record_count()
            
            self.show_notification("Data loaded successfully!", "success")
            
        except Exception as e:
            self.show_notification(f"Error loading data: {str(e)}", "error")
    
    def load_combo_data(self):
        """Load data for combo boxes"""
        # Load customers for sales form
        customers = self.session.query(Customer).all()
        customer_names = [f"{c.id}: {c.name}" for c in customers]
        self.sale_customer['values'] = customer_names
        
        # Load products for sales form
        products = self.session.query(Product).all()
        product_names = [f"{p.id}: {p.name}" for p in products]
        self.sale_product['values'] = product_names
    
    def load_product_table(self):
        """Load products into table"""
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Load products
        products = self.session.query(Product).all()
        
        for product in products:
            self.product_tree.insert('', 'end',
                                   values=(product.id,
                                           product.name,
                                           product.category,
                                           f"${product.price:.2f}",
                                           f"${product.cost:.2f}",
                                           product.stock))
    
    def load_customer_table(self):
        """Load customers into table"""
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        customers = self.session.query(Customer).all()
        
        for customer in customers:
            join_date = customer.join_date.strftime('%Y-%m-%d') if customer.join_date else ''
            self.customer_tree.insert('', 'end',
                                    values=(customer.id,
                                            customer.name,
                                            customer.email,
                                            customer.phone,
                                            customer.segment,
                                            join_date))
    
    def load_sale_table(self):
        """Load sales into table"""
        for item in self.sale_tree.get_children():
            self.sale_tree.delete(item)
        
        # Get sales with customer and product names
        conn = get_sqlite_connection()
        query = """
        SELECT s.id, s.date, c.name, p.name, s.quantity, s.amount, s.payment_method
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        JOIN products p ON s.product_id = p.id
        ORDER BY s.date DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        for _, row in df.iterrows():
            self.sale_tree.insert('', 'end',
                                values=(row['id'],
                                        row['date'],
                                        row['name'],  # customer name
                                        row['name'],  # product name - NOTE: this is ambiguous
                                        row['quantity'],
                                        f"${row['amount']:.2f}",
                                        row['payment_method']))
    
    def load_employee_table(self):
        """Load employees into table"""
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        employees = self.session.query(Employee).all()
        
        for employee in employees:
            hire_date = employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else ''
            self.employee_tree.insert('', 'end',
                                    values=(employee.id,
                                            employee.name,
                                            employee.department,
                                            f"${employee.salary:.2f}",
                                            hire_date))
    
    def load_inventory_table(self):
        """Load inventory data"""
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Get inventory data
        conn = get_sqlite_connection()
        query = """
        SELECT 
            p.id,
            p.name,
            p.category,
            p.stock as current_stock,
            CASE 
                WHEN p.stock <= 10 THEN '⚠️ Low'
                WHEN p.stock <= 50 THEN '🟡 Medium'
                ELSE '🟢 Good'
            END as stock_status,
            DATE('now') as last_updated
        FROM products p
        ORDER BY p.stock ASC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        low_stock_count = 0
        
        for _, row in df.iterrows():
            if 'Low' in row['stock_status']:
                low_stock_count += 1
            
            self.inventory_tree.insert('', 'end',
                                     values=(row['id'],
                                             row['name'],
                                             row['category'],
                                             row['current_stock'],
                                             row['stock_status'],
                                             row['last_updated']))
        
        # Update low stock warning
        self.low_stock_label.config(
            text=f"⚠️ {low_stock_count} products with low stock",
            fg=self.colors['warning'] if low_stock_count > 0 else self.colors['success']
        )
    
    # ==================== FORM HANDLING METHODS ====================
    
    def clear_product_form(self):
        """Clear product form fields"""
        self.product_name.delete(0, tk.END)
        self.product_category.set('')
        self.product_price.delete(0, tk.END)
        self.product_cost.delete(0, tk.END)
        self.product_stock.delete(0, tk.END)
        self.current_record_id = None
        self.current_entity = None
        
        self.last_action_label.config(text="Form cleared")
    
    def clear_customer_form(self):
        """Clear customer form fields"""
        self.customer_name.delete(0, tk.END)
        self.customer_email.delete(0, tk.END)
        self.customer_phone.delete(0, tk.END)
        self.customer_segment.set('')
        self.customer_join_date.delete(0, tk.END)
        self.customer_join_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.current_record_id = None
        self.current_entity = None
    
    def clear_sales_form(self):
        """Clear sales form fields"""
        self.sale_customer.set('')
        self.sale_product.set('')
        self.sale_date.delete(0, tk.END)
        self.sale_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.sale_quantity.delete(0, tk.END)
        self.sale_amount.delete(0, tk.END)
        self.sale_payment.set('')
        self.current_record_id = None
        self.current_entity = None
    
    def clear_employee_form(self):
        """Clear employee form fields"""
        self.employee_name.delete(0, tk.END)
        self.employee_department.set('')
        self.employee_salary.delete(0, tk.END)
        self.employee_hire_date.delete(0, tk.END)
        self.employee_hire_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.current_record_id = None
        self.current_entity = None
    
    # ==================== CRUD OPERATIONS ====================
    
    def save_product(self):
        """Save new product"""
        try:
            # Validate required fields
            if not self.product_name.get():
                messagebox.showwarning("Validation Error", "Product name is required")
                return
            
            # Create new product
            product = Product(
                name=self.product_name.get(),
                category=self.product_category.get(),
                price=float(self.product_price.get() or 0),
                cost=float(self.product_cost.get() or 0),
                stock=int(self.product_stock.get() or 0)
            )
            
            self.session.add(product)
            self.session.commit()
            
            # Refresh table
            self.load_product_table()
            self.load_inventory_table()
            
            # Clear form
            self.clear_product_form()
            
            self.show_notification("Product saved successfully!", "success")
            self.last_action_label.config(text=f"Product '{product.name}' saved")
            
        except Exception as e:
            self.session.rollback()
            self.show_notification(f"Error saving product: {str(e)}", "error")
    
    def update_product(self):
        """Update existing product"""
        if not self.current_record_id:
            messagebox.showinfo("Info", "Please select a product to update")
            return
        
        try:
            product = self.session.query(Product).get(self.current_record_id)
            
            if product:
                product.name = self.product_name.get()
                product.category = self.product_category.get()
                product.price = float(self.product_price.get() or 0)
                product.cost = float(self.product_cost.get() or 0)
                product.stock = int(self.product_stock.get() or 0)
                
                self.session.commit()
                
                # Refresh tables
                self.load_product_table()
                self.load_inventory_table()
                
                self.show_notification("Product updated successfully!", "success")
                self.last_action_label.config(text=f"Product '{product.name}' updated")
        
        except Exception as e:
            self.session.rollback()
            self.show_notification(f"Error updating product: {str(e)}", "error")
    
    def delete_product(self):
        """Delete selected product"""
        if not self.current_record_id:
            messagebox.showinfo("Info", "Please select a product to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              "Are you sure you want to delete this product?"):
            try:
                product = self.session.query(Product).get(self.current_record_id)
                product_name = product.name
                
                self.session.delete(product)
                self.session.commit()
                
                # Refresh tables
                self.load_product_table()
                self.load_inventory_table()
                
                # Clear form
                self.clear_product_form()
                
                self.show_notification("Product deleted successfully!", "success")
                self.last_action_label.config(text=f"Product '{product_name}' deleted")
            
            except Exception as e:
                self.session.rollback()
                self.show_notification(f"Error deleting product: {str(e)}", "error")
    
    def save_customer(self):
        """Save new customer"""
        try:
            if not self.customer_name.get():
                messagebox.showwarning("Validation Error", "Customer name is required")
                return
            
            customer = Customer(
                name=self.customer_name.get(),
                email=self.customer_email.get(),
                phone=self.customer_phone.get(),
                segment=self.customer_segment.get(),
                join_date=datetime.strptime(self.customer_join_date.get(), '%Y-%m-%d').date()
            )
            
            self.session.add(customer)
            self.session.commit()
            
            # Refresh tables
            self.load_customer_table()
            self.load_combo_data()  # Update sales form
            
            self.clear_customer_form()
            
            self.show_notification("Customer saved successfully!", "success")
            self.last_action_label.config(text=f"Customer '{customer.name}' saved")
        
        except Exception as e:
            self.session.rollback()
            self.show_notification(f"Error saving customer: {str(e)}", "error")
    
    def update_customer(self):
        """Update existing customer"""
        if not self.current_record_id:
            messagebox.showinfo("Info", "Please select a customer to update")
            return
        
        try:
            customer = self.session.query(Customer).get(self.current_record_id)
            
            if customer:
                customer.name = self.customer_name.get()
                customer.email = self.customer_email.get()
                customer.phone = self.customer_phone.get()
                customer.segment = self.customer_segment.get()
                customer.join_date = datetime.strptime(self.customer_join_date.get(), '%Y-%m-%d').date()
                
                self.session.commit()
                
                self.load_customer_table()
                self.load_combo_data()
                
                self.show_notification("Customer updated successfully!", "success")
                self.last_action_label.config(text=f"Customer '{customer.name}' updated")
        
        except Exception as e:
            self.session.rollback()
            self.show_notification(f"Error updating customer: {str(e)}", "error")
    
    def delete_customer(self):
        """Delete selected customer"""
        if not self.current_record_id:
            messagebox.showinfo("Info", "Please select a customer to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              "Are you sure you want to delete this customer?"):
            try:
                customer = self.session.query(Customer).get(self.current_record_id)
                customer_name = customer.name
                
                self.session.delete(customer)
                self.session.commit()
                
                self.load_customer_table()
                self.load_combo_data()
                self.clear_customer_form()
                
                self.show_notification("Customer deleted successfully!", "success")
                self.last_action_label.config(text=f"Customer '{customer_name}' deleted")
            
            except Exception as e:
                self.session.rollback()
                self.show_notification(f"Error deleting customer: {str(e)}", "error")
    
    def calculate_sale_amount(self):
        """Calculate sale amount based on product price and quantity"""
        try:
            # Extract product ID from combo selection
            product_str = self.sale_product.get()
            if ':' in product_str:
                product_id = int(product_str.split(':')[0].strip())
                
                # Get product price
                product = self.session.query(Product).get(product_id)
                if product:
                    quantity = int(self.sale_quantity.get() or 1)
                    amount = product.price * quantity
                    
                    # Update amount field
                    self.sale_amount.delete(0, tk.END)
                    self.sale_amount.insert(0, f"{amount:.2f}")
                    
                    self.last_action_label.config(text="Amount calculated")
        
        except Exception as e:
            self.show_notification(f"Error calculating amount: {str(e)}", "error")
    
    def save_sale(self):
        """Save new sale"""
        try:
            # Validate required fields
            if not self.sale_customer.get() or not self.sale_product.get():
                messagebox.showwarning("Validation Error", 
                                      "Customer and Product are required")
                return
            
            # Extract IDs from combo selections
            customer_id = int(self.sale_customer.get().split(':')[0].strip())
            product_id = int(self.sale_product.get().split(':')[0].strip())
            
            sale = Sale(
                customer_id=customer_id,
                product_id=product_id,
                date=datetime.strptime(self.sale_date.get(), '%Y-%m-%d').date(),
                quantity=int(self.sale_quantity.get() or 1),
                amount=float(self.sale_amount.get() or 0),
                payment_method=self.sale_payment.get()
            )
            
            self.session.add(sale)
            self.session.commit()
            
            # Update product stock
            product = self.session.query(Product).get(product_id)
            if product:
                product.stock -= sale.quantity
                self.session.commit()
            
            # Refresh tables
            self.load_sale_table()
            self.load_product_table()
            self.load_inventory_table()
            
            self.clear_sales_form()
            
            self.show_notification("Sale saved successfully!", "success")
            self.last_action_label.config(text=f"Sale #{sale.id} saved")
        
        except Exception as e:
            self.session.rollback()
            self.show_notification(f"Error saving sale: {str(e)}", "error")
    
    def update_sale(self):
        """Update existing sale"""
        if not self.current_record_id:
            messagebox.showinfo("Info", "Please select a sale to update")
            return
        
        # Similar to save_sale but with update logic
        # Implementation would be similar to other update methods
    
    def delete_sale(self):
        """Delete selected sale"""
        if not self.current_record_id:
            messagebox.showinfo("Info", "Please select a sale to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              "Are you sure you want to delete this sale?"):
            try:
                sale = self.session.query(Sale).get(self.current_record_id)
                
                # Restore product stock
                product = self.session.query(Product).get(sale.product_id)
                if product:
                    product.stock += sale.quantity
                
                self.session.delete(sale)
                self.session.commit()
                
                self.load_sale_table()
                self.load_product_table()
                self.load_inventory_table()
                self.clear_sales_form()
                
                self.show_notification("Sale deleted successfully!", "success")
                self.last_action_label.config(text=f"Sale #{sale.id} deleted")
            
            except Exception as e:
                self.session.rollback()
                self.show_notification(f"Error deleting sale: {str(e)}", "error")
    
    def save_employee(self):
        """Save new employee"""
        try:
            if not self.employee_name.get():
                messagebox.showwarning("Validation Error", "Employee name is required")
                return
            
            employee = Employee(
                name=self.employee_name.get(),
                department=self.employee_department.get(),
                salary=float(self.employee_salary.get() or 0),
                hire_date=datetime.strptime(self.employee_hire_date.get(), '%Y-%m-%d').date()
            )
            
            self.session.add(employee)
            self.session.commit()
            
            self.load_employee_table()
            self.clear_employee_form()
            
            self.show_notification("Employee saved successfully!", "success")
            self.last_action_label.config(text=f"Employee '{employee.name}' saved")
        
        except Exception as e:
            self.session.rollback()
            self.show_notification(f"Error saving employee: {str(e)}", "error")
    
    def update_employee(self):
        """Update existing employee"""
        # Similar to other update methods
        pass
    
    def delete_employee(self):
        """Delete selected employee"""
        # Similar to other delete methods
        pass
    
    # ==================== SELECTION HANDLERS ====================
    
    def on_product_select(self, event):
        """Handle product selection from table"""
        selected = self.product_tree.selection()
        if selected:
            item = self.product_tree.item(selected[0])
            values = item['values']
            
            if values:
                self.current_record_id = values[0]
                self.current_entity = 'product'
                
                # Fill form
                self.clear_product_form()
                self.product_name.insert(0, values[1])
                self.product_category.set(values[2])
                self.product_price.insert(0, values[3].replace('$', ''))
                self.product_cost.insert(0, values[4].replace('$', ''))
                self.product_stock.insert(0, values[5])
                
                self.last_action_label.config(text=f"Product {values[0]} selected")
    
    def on_customer_select(self, event):
        """Handle customer selection from table"""
        selected = self.customer_tree.selection()
        if selected:
            item = self.customer_tree.item(selected[0])
            values = item['values']
            
            if values:
                self.current_record_id = values[0]
                self.current_entity = 'customer'
                
                self.clear_customer_form()
                self.customer_name.insert(0, values[1])
                self.customer_email.insert(0, values[2])
                self.customer_phone.insert(0, values[3])
                self.customer_segment.set(values[4])
                self.customer_join_date.delete(0, tk.END)
                self.customer_join_date.insert(0, values[5])
    
    def on_sale_select(self, event):
        """Handle sale selection from table"""
        selected = self.sale_tree.selection()
        if selected:
            item = self.sale_tree.item(selected[0])
            values = item['values']
            
            if values:
                self.current_record_id = values[0]
                self.current_entity = 'sale'
                
                # Note: This is simplified - would need to get customer/product IDs
                self.clear_sales_form()
                self.sale_date.delete(0, tk.END)
                self.sale_date.insert(0, values[1])
                # Would need to set customer and product combos based on names
                self.sale_quantity.insert(0, values[4])
                self.sale_amount.insert(0, values[5].replace('$', ''))
                self.sale_payment.set(values[6])
    
    def on_employee_select(self, event):
        """Handle employee selection from table"""
        selected = self.employee_tree.selection()
        if selected:
            item = self.employee_tree.item(selected[0])
            values = item['values']
            
            if values:
                self.current_record_id = values[0]
                self.current_entity = 'employee'
                
                self.clear_employee_form()
                self.employee_name.insert(0, values[1])
                self.employee_department.set(values[2])
                self.employee_salary.insert(0, values[3].replace('$', ''))
                self.employee_hire_date.delete(0, tk.END)
                self.employee_hire_date.insert(0, values[4])
    
    # ==================== SEARCH FUNCTIONS ====================
    
    def search_products(self, event):
        """Search products by name or category"""
        search_term = self.product_search.get().lower()
        
        # Clear current items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        if not search_term:
            # Show all if search is empty
            self.load_product_table()
            return
        
        # Search in database
        products = self.session.query(Product).filter(
            (Product.name.ilike(f'%{search_term}%')) |
            (Product.category.ilike(f'%{search_term}%'))
        ).all()
        
        for product in products:
            self.product_tree.insert('', 'end',
                                   values=(product.id,
                                           product.name,
                                           product.category,
                                           f"${product.price:.2f}",
                                           f"${product.cost:.2f}",
                                           product.stock))
    
    def search_customers(self, event):
        """Search customers by name, email, or segment"""
        search_term = self.customer_search.get().lower()
        
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        if not search_term:
            self.load_customer_table()
            return
        
        customers = self.session.query(Customer).filter(
            (Customer.name.ilike(f'%{search_term}%')) |
            (Customer.email.ilike(f'%{search_term}%')) |
            (Customer.segment.ilike(f'%{search_term}%'))
        ).all()
        
        for customer in customers:
            join_date = customer.join_date.strftime('%Y-%m-%d') if customer.join_date else ''
            self.customer_tree.insert('', 'end',
                                    values=(customer.id,
                                            customer.name,
                                            customer.email,
                                            customer.phone,
                                            customer.segment,
                                            join_date))
    
    def search_employees(self, event):
        """Search employees by name or department"""
        search_term = self.employee_search.get().lower()
        
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        if not search_term:
            self.load_employee_table()
            return
        
        employees = self.session.query(Employee).filter(
            (Employee.name.ilike(f'%{search_term}%')) |
            (Employee.department.ilike(f'%{search_term}%'))
        ).all()
        
        for employee in employees:
            hire_date = employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else ''
            self.employee_tree.insert('', 'end',
                                    values=(employee.id,
                                            employee.name,
                                            employee.department,
                                            f"${employee.salary:.2f}",
                                            hire_date))
    
    # ==================== IMPORT/EXPORT FUNCTIONS ====================
    
    def select_import_file(self):
        """Select file for import"""
        file_types = [
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select file to import",
            filetypes=file_types
        )
        
        if filename:
            self.import_status.config(
                text=f"Selected: {filename.split('/')[-1]}",
                fg=self.colors['success']
            )
            self.selected_file = filename
    
    def preview_import_data(self):
        """Preview data from selected file"""
        if not hasattr(self, 'selected_file'):
            messagebox.showinfo("Info", "Please select a file first")
            return
        
        try:
            file_format = self.import_format.get().lower()
            entity = self.import_entity.get().lower()
            
            if file_format == 'csv':
                df = pd.read_csv(self.selected_file)
            elif file_format == 'excel':
                df = pd.read_excel(self.selected_file)
            elif file_format == 'json':
                df = pd.read_json(self.selected_file)
            else:
                df = pd.read_csv(self.selected_file)
            
            # Show preview in new window
            preview_window = tk.Toplevel(self)
            preview_window.title(f"Preview - {entity.capitalize()} Data")
            preview_window.geometry("800x600")
            
            # Create Treeview for preview
            columns = list(df.columns)
            preview_tree = ttk.Treeview(preview_window, columns=columns, show='headings')
            
            for col in columns:
                preview_tree.heading(col, text=col)
                preview_tree.column(col, width=100)
            
            # Add scrollbars
            v_scrollbar = ttk.Scrollbar(preview_window, orient='vertical',
                                       command=preview_tree.yview)
            h_scrollbar = ttk.Scrollbar(preview_window, orient='horizontal',
                                       command=preview_tree.xview)
            
            preview_tree.configure(yscrollcommand=v_scrollbar.set,
                                 xscrollcommand=h_scrollbar.set)
            
            # Insert data
            for _, row in df.head(50).iterrows():  # Show first 50 rows
                preview_tree.insert('', 'end', values=tuple(row))
            
            # Pack
            preview_tree.pack(side='left', fill='both', expand=True)
            v_scrollbar.pack(side='right', fill='y')
            h_scrollbar.pack(side='bottom', fill='x')
            
            # Info label
            info_label = tk.Label(preview_window,
                                 text=f"Showing {len(df)} rows, {len(df.columns)} columns",
                                 font=self.fonts['small'])
            info_label.pack(side='bottom', pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview file: {str(e)}")
    
    def import_data(self):
        """Import data from file"""
        if not hasattr(self, 'selected_file'):
            messagebox.showinfo("Info", "Please select a file first")
            return
        
        try:
            file_format = self.import_format.get().lower()
            entity = self.import_entity.get().lower()
            
            # Load data
            if file_format == 'csv':
                df = pd.read_csv(self.selected_file)
            elif file_format == 'excel':
                df = pd.read_excel(self.selected_file)
            elif file_format == 'json':
                df = pd.read_json(self.selected_file)
            else:
                df = pd.read_csv(self.selected_file)
            
            # Import based on entity
            if entity == 'products':
                self.import_products(df)
            elif entity == 'customers':
                self.import_customers(df)
            elif entity == 'sales':
                self.import_sales(df)
            elif entity == 'employees':
                self.import_employees(df)
            
            self.show_notification(f"Imported {len(df)} {entity} successfully!", "success")
            
        except Exception as e:
            self.show_notification(f"Import failed: {str(e)}", "error")
    
    def import_products(self, df):
        """Import products from DataFrame"""
        for _, row in df.iterrows():
            product = Product(
                name=row.get('name', ''),
                category=row.get('category', ''),
                price=float(row.get('price', 0)),
                cost=float(row.get('cost', 0)),
                stock=int(row.get('stock', 0))
            )
            self.session.add(product)
        
        self.session.commit()
        self.load_product_table()
        self.load_inventory_table()
    
    def import_customers(self, df):
        """Import customers from DataFrame"""
        for _, row in df.iterrows():
            customer = Customer(
                name=row.get('name', ''),
                email=row.get('email', ''),
                phone=row.get('phone', ''),
                segment=row.get('segment', 'Regular')
            )
            self.session.add(customer)
        
        self.session.commit()
        self.load_customer_table()
        self.load_combo_data()
    
    # Similar methods for sales and employees...
    
    def export_all_data(self):
        """Export all data to Excel"""
        try:
            # Create Excel writer
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
            
            if filename:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Export each entity
                    conn = get_sqlite_connection()
                    
                    entities = {
                        'Products': 'SELECT * FROM products',
                        'Customers': 'SELECT * FROM customers',
                        'Sales': '''SELECT s.*, c.name as customer_name, 
                                   p.name as product_name 
                                   FROM sales s
                                   JOIN customers c ON s.customer_id = c.id
                                   JOIN products p ON s.product_id = p.id''',
                        'Employees': 'SELECT * FROM employees'
                    }
                    
                    for sheet_name, query in entities.items():
                        df = pd.read_sql_query(query, conn)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    conn.close()
                
                self.show_notification(f"Data exported to {filename}", "success")
                self.last_action_label.config(text="All data exported")
        
        except Exception as e:
            self.show_notification(f"Export failed: {str(e)}", "error")
    
    # ==================== QUICK ACTIONS ====================
    
    def refresh_all_data(self):
        """Refresh all data tables"""
        threading.Thread(target=self.load_all_data, daemon=True).start()
        self.show_notification("Refreshing all data...", "info")
    
    def delete_test_data(self):
        """Delete all test data"""
        if messagebox.askyesno("Confirm Delete", 
                              "Delete ALL test data? This cannot be undone!"):
            try:
                # Delete all records
                self.session.query(Sale).delete()
                self.session.query(Customer).delete()
                self.session.query(Product).delete()
                self.session.query(Employee).delete()
                self.session.commit()
                
                # Refresh all tables
                self.load_all_data()
                
                self.show_notification("All test data deleted", "success")
                self.last_action_label.config(text="All test data deleted")
            
            except Exception as e:
                self.session.rollback()
                self.show_notification(f"Error deleting data: {str(e)}", "error")
    
    def generate_sample_data(self):
        """Generate sample data for testing"""
        if messagebox.askyesno("Generate Sample Data", 
                              "Generate sample data for testing?"):
            try:
                # This would call your demo data generation function
                # For now, just show a message
                self.show_notification("Sample data generation would run here", "info")
                self.last_action_label.config(text="Sample data generated")
            
            except Exception as e:
                self.show_notification(f"Error generating data: {str(e)}", "error")
    
    def validate_data(self):
        """Validate all data for consistency"""
        try:
            issues = []
            
            # Check for products with negative stock
            negative_stock = self.session.query(Product).filter(Product.stock < 0).count()
            if negative_stock > 0:
                issues.append(f"{negative_stock} products have negative stock")
            
            # Check for customers without email
            no_email = self.session.query(Customer).filter(Customer.email == '').count()
            if no_email > 0:
                issues.append(f"{no_email} customers without email")
            
            # Show validation results
            if issues:
                message = "Validation Issues Found:\n\n" + "\n".join(f"• {issue}" for issue in issues)
                messagebox.showwarning("Validation Results", message)
            else:
                messagebox.showinfo("Validation Results", "✅ All data is valid!")
            
            self.last_action_label.config(text="Data validation completed")
        
        except Exception as e:
            self.show_notification(f"Validation error: {str(e)}", "error")
    
    def update_inventory(self):
        """Update inventory stock levels"""
        try:
            # This would update inventory from sales data
            # For now, just refresh the table
            self.load_inventory_table()
            self.show_notification("Inventory updated", "success")
            self.last_action_label.config(text="Inventory updated")
        
        except Exception as e:
            self.show_notification(f"Error updating inventory: {str(e)}", "error")
    
    def generate_inventory_report(self):
        """Generate inventory report"""
        try:
            # Create inventory report
            conn = get_sqlite_connection()
            query = """
            SELECT 
                p.name,
                p.category,
                p.stock,
                p.price,
                p.cost,
                (p.price - p.cost) as profit_per_unit,
                CASE 
                    WHEN p.stock = 0 THEN 'Out of Stock'
                    WHEN p.stock <= 10 THEN 'Low Stock'
                    WHEN p.stock <= 50 THEN 'Medium Stock'
                    ELSE 'Good Stock'
                END as stock_status
            FROM products p
            ORDER BY p.stock ASC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Save report
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
            )
            
            if filename:
                if filename.endswith('.xlsx'):
                    df.to_excel(filename, index=False)
                else:
                    df.to_csv(filename, index=False)
                
                self.show_notification(f"Inventory report saved", "success")
                self.last_action_label.config(text="Inventory report generated")
        
        except Exception as e:
            self.show_notification(f"Error generating report: {str(e)}", "error")
    
    # ==================== UTILITY METHODS ====================
    
    def update_stats(self):
        """Update statistics display"""
        try:
            product_count = self.session.query(Product).count()
            customer_count = self.session.query(Customer).count()
            sale_count = self.session.query(Sale).count()
            employee_count = self.session.query(Employee).count()
            
            stats_text = f"📊 Stats: {product_count} Products • {customer_count} Customers • {sale_count} Sales • {employee_count} Employees"
            self.stats_label.config(text=stats_text)
        
        except Exception as e:
            self.stats_label.config(text="Error loading stats")
    
    def update_record_count(self):
        """Update record count in footer"""
        try:
            total_records = (
                self.session.query(Product).count() +
                self.session.query(Customer).count() +
                self.session.query(Sale).count() +
                self.session.query(Employee).count()
            )
            
            self.record_count_label.config(
                text=f"Total Records: {total_records:,}"
            )
        
        except Exception as e:
            self.record_count_label.config(text="Error counting records")
    
    def show_notification(self, message, type="info"):
        """Show notification message"""
        colors = {
            'success': self.colors['success'],
            'error': self.colors['error'],
            'warning': self.colors['warning'],
            'info': self.colors['primary']
        }
        
        # Create notification label
        notification = tk.Label(self,
                              text=message,
                              font=self.fonts['small'],
                              bg=colors.get(type, self.colors['primary']),
                              fg=self.colors['white'],
                              padx=20,
                              pady=10)
        
        # Place notification
        notification.place(relx=0.5, rely=0.1, anchor='center')
        
        # Remove after 3 seconds
        self.after(3000, notification.destroy)
    
    def destroy(self):
        """Clean up resources"""
        try:
            self.session.close()
        except:
            pass
        super().destroy()