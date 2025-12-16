"""
Premium UI Styles and Themes for Business Intelligence System
"""

class Theme:
    """Theme configuration for premium UI"""
    
    LIGHT_THEME = {
        'primary': '#1a237e',
        'primary_light': '#534bae',
        'primary_dark': '#000051',
        'secondary': '#00b0ff',
        'accent': '#ff4081',
        'success': '#00c853',
        'warning': '#ff9100',
        'error': '#ff5252',
        'dark': '#263238',
        'light': '#f5f5f5',
        'lighter': '#fafafa',
        'white': '#ffffff',
        'gray': '#90a4ae',
        'gray_light': '#cfd8dc',
        'border': '#e0e0e0',
        'shadow': 'rgba(0, 0, 0, 0.1)'
    }
    
    DARK_THEME = {
        'primary': '#7986cb',
        'primary_light': '#aab6fe',
        'primary_dark': '#49599a',
        'secondary': '#80deea',
        'accent': '#ff80ab',
        'success': '#69f0ae',
        'warning': '#ffd740',
        'error': '#ff5252',
        'dark': '#121212',
        'light': '#1e1e1e',
        'lighter': '#2d2d2d',
        'white': '#ffffff',
        'gray': '#90a4ae',
        'gray_light': '#37474f',
        'border': '#424242',
        'shadow': 'rgba(0, 0, 0, 0.3)'
    }
    
    @classmethod
    def get_theme(cls, theme_name='light'):
        """Get theme configuration"""
        return cls.LIGHT_THEME if theme_name == 'light' else cls.DARK_THEME


class Fonts:
    """Font configuration"""
    
    SEGOE_UI = {
        'h1': ('Segoe UI', 28, 'bold'),
        'h2': ('Segoe UI', 20, 'bold'),
        'h3': ('Segoe UI', 16, 'bold'),
        'h4': ('Segoe UI', 14, 'bold'),
        'body': ('Segoe UI', 11),
        'body_bold': ('Segoe UI', 11, 'bold'),
        'small': ('Segoe UI', 10),
        'small_bold': ('Segoe UI', 10, 'bold'),
        'caption': ('Segoe UI', 9),
        'mono': ('Consolas', 10)
    }
    
    INTER = {
        'h1': ('Inter', 28, 'bold'),
        'h2': ('Inter', 20, 'bold'),
        'h3': ('Inter', 16, 'bold'),
        'h4': ('Inter', 14, 'bold'),
        'body': ('Inter', 11),
        'body_bold': ('Inter', 11, 'bold'),
        'small': ('Inter', 10),
        'small_bold': ('Inter', 10, 'bold'),
        'caption': ('Inter', 9),
        'mono': ('Roboto Mono', 10)
    }
    
    @classmethod
    def get_fonts(cls, font_family='segoe'):
        """Get font configuration"""
        return cls.SEGOE_UI if font_family == 'segoe' else cls.INTER


class UIConfig:
    """Unified UI configuration"""
    
    def __init__(self, theme='light', font_family='segoe'):
        self.theme = Theme.get_theme(theme)
        self.fonts = Fonts.get_fonts(font_family)
        self.corner_radius = 8
        self.shadow_offset = 4
        self.animation_duration = 200  # ms
    
    def apply_theme(self, widget, bg_color=None, fg_color=None):
        """Apply theme colors to widget"""
        if bg_color:
            widget.config(bg=self.theme.get(bg_color, bg_color))
        if fg_color:
            widget.config(fg=self.theme.get(fg_color, fg_color))
    
    def create_gradient(self, color1, color2, steps=10):
        """Create gradient colors"""
        # This is a simplified version - in production, you'd use PIL
        return [color1, color2]