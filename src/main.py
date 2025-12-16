import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ui.main_window import MainWindow
from database.db_connection import create_database
from utils.config import load_config

class BusinessIntelligenceApp:
    def __init__(self):
        # Initialize database
        print("Initializing database...")
        create_database()
        
        # Load configuration
        self.config = load_config()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Business Intelligence System")
        self.root.geometry("1400x800")
        
        # Apply theme
        self.setup_theme()
        
        # Create main application
        self.app = MainWindow(self.root, self.config)
        
    def setup_theme(self):
        """Configure application theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('TButton', font=('Arial', 10))
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BusinessIntelligenceApp()
    app.run()