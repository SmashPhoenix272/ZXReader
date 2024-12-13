import os
from PyQt5.QtGui import QFont, QFontDatabase
from enum import Enum, auto

class FontType(Enum):
    UI = auto()          # For interface elements
    CHINESE = auto()     # For Chinese text
    VIETNAMESE = auto()  # For Vietnamese translations

class FontWeight:
    """Font weight definitions matching common font file naming."""
    THIN = QFont.Thin
    EXTRA_LIGHT = QFont.ExtraLight
    LIGHT = QFont.Light
    REGULAR = QFont.Normal
    MEDIUM = QFont.Medium
    SEMI_BOLD = QFont.DemiBold
    BOLD = QFont.Bold
    EXTRA_BOLD = QFont.ExtraBold
    BLACK = QFont.Black

    @staticmethod
    def from_name(name):
        """Convert weight name to QFont weight value."""
        weights = {
            'thin': QFont.Thin,
            'extralight': QFont.ExtraLight,
            'light': QFont.Light,
            'regular': QFont.Normal,
            'medium': QFont.Medium,
            'semibold': QFont.DemiBold,
            'bold': QFont.Bold,
            'extrabold': QFont.ExtraBold,
            'black': QFont.Black
        }
        return weights.get(name.lower().replace('-', '').replace('_', ''), QFont.Normal)

class FontFamily:
    def __init__(self, name, font_type=FontType.UI):
        self.name = name
        self.font_type = font_type
        self.variable_fonts = {}  # style -> path (e.g., 'regular', 'italic')
        self.static_fonts = {}    # (weight, style) -> path
        self.loaded_ids = set()   # Set of loaded font IDs
        self.loaded = False

    def add_variable_font(self, path, style='regular'):
        """Add a variable font file."""
        self.variable_fonts[style] = path

    def add_static_font(self, path, weight=FontWeight.REGULAR, style='regular'):
        """Add a static font file."""
        self.static_fonts[(weight, style)] = path

    def get_font_path(self, weight=FontWeight.REGULAR, style='regular'):
        """Get the most appropriate font file path for the requested weight and style."""
        # Try variable font first
        if style in self.variable_fonts:
            return self.variable_fonts[style]
        
        # Fall back to static font
        return self.static_fonts.get((weight, style))

class FontManager:
    def __init__(self):
        self.font_families = {}  # name -> FontFamily
        self.current_fonts = {
            FontType.UI: None,
            FontType.CHINESE: None,
            FontType.VIETNAMESE: None
        }

    def scan_font_directory(self, directory, font_type=None):
        """Scan a directory for fonts and add them to the manager."""
        if not os.path.exists(directory):
            return False

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                self._scan_font_family(item_path, item, font_type)

        return True

    def _scan_font_family(self, directory, family_name, font_type=None):
        """Scan a font family directory and add its fonts."""
        family = FontFamily(family_name, font_type)

        # Check for variable fonts in main directory
        for file in os.listdir(directory):
            if 'variable' in file.lower() and file.endswith(('.ttf', '.otf')):
                style = 'italic' if 'italic' in file.lower() else 'regular'
                family.add_variable_font(os.path.join(directory, file), style)

        # Check for static fonts
        static_dir = os.path.join(directory, 'static')
        if os.path.exists(static_dir):
            for file in os.listdir(static_dir):
                if file.endswith(('.ttf', '.otf')):
                    path = os.path.join(static_dir, file)
                    style = 'italic' if 'italic' in file.lower() else 'regular'
                    weight = self._detect_weight_from_filename(file)
                    family.add_static_font(path, weight, style)

        self.font_families[family_name] = family

    def _detect_weight_from_filename(self, filename):
        """Detect font weight from filename."""
        filename = filename.lower()
        if 'thin' in filename: return FontWeight.THIN
        if 'extralight' in filename: return FontWeight.EXTRA_LIGHT
        if 'light' in filename: return FontWeight.LIGHT
        if 'medium' in filename: return FontWeight.MEDIUM
        if 'semibold' in filename: return FontWeight.SEMI_BOLD
        if 'bold' in filename:
            if 'extra' in filename or 'ultra' in filename:
                return FontWeight.EXTRA_BOLD
            return FontWeight.BOLD
        if 'black' in filename: return FontWeight.BLACK
        return FontWeight.REGULAR

    def add_font_file(self, path, family_name=None, weight=None, style='regular', font_type=None):
        """Add a single font file to the manager."""
        if not os.path.exists(path):
            return False

        # Use filename as family name if not provided
        if not family_name:
            family_name = os.path.splitext(os.path.basename(path))[0]
            family_name = family_name.split('-')[0]  # Remove weight/style suffixes

        # Create family if it doesn't exist
        if family_name not in self.font_families:
            self.font_families[family_name] = FontFamily(family_name, font_type)

        family = self.font_families[family_name]
        
        # Detect if it's a variable font
        if 'variable' in path.lower():
            family.add_variable_font(path, style)
        else:
            if weight is None:
                weight = self._detect_weight_from_filename(os.path.basename(path))
            family.add_static_font(path, weight, style)

        return True

    def load_font_family(self, family_name):
        """Load a font family into the system."""
        if family_name not in self.font_families:
            return False

        family = self.font_families[family_name]
        if family.loaded:
            return True

        try:
            # Load variable fonts
            for path in family.variable_fonts.values():
                font_id = QFontDatabase.addApplicationFont(path)
                if font_id != -1:
                    family.loaded_ids.add(font_id)
                    family.loaded = True

            # Load static fonts if no variable fonts were loaded
            if not family.loaded:
                for path in family.static_fonts.values():
                    font_id = QFontDatabase.addApplicationFont(path)
                    if font_id != -1:
                        family.loaded_ids.add(font_id)
                        family.loaded = True

            return family.loaded

        except Exception as e:
            print(f"Error loading font family {family_name}: {e}")
            return False

    def create_font(self, family_name, size=10, weight=FontWeight.REGULAR):
        """Create a QFont object for the specified family."""
        if family_name not in self.font_families:
            return QFont()

        # Load font if not already loaded
        if not self.font_families[family_name].loaded:
            if not self.load_font_family(family_name):
                return QFont()

        font = QFont(family_name)
        font.setPointSize(size)
        font.setWeight(weight)
        return font

    def set_font(self, font_type, family_name, size=10, weight=FontWeight.REGULAR):
        """Set the current font for a specific type."""
        if family_name not in self.font_families:
            return False

        font = self.create_font(family_name, size, weight)
        if font:
            self.current_fonts[font_type] = font
            return True
        return False

    def get_current_font(self, font_type):
        """Get the current font for a specific type."""
        return self.current_fonts.get(font_type)

    def apply_font_to_widget(self, widget, font_type):
        """Apply the current font of a specific type to a widget."""
        font = self.current_fonts.get(font_type)
        if font:
            widget.setFont(font)
            return True
        return False

    def get_font_families(self, font_type=None):
        """Get list of available font families, optionally filtered by type."""
        if font_type is None:
            return list(self.font_families.keys())
        return [name for name, family in self.font_families.items() 
                if family.font_type == font_type]