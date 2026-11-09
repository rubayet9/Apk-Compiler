"""
APK Compiler - UI Package
Exports main application window, pages, reusable widgets, and theme constants.
"""

from src.ui.theme import (
    COLORS,
    LIGHT_COLORS,
    FONTS,
    FONT_FAMILY,
    FONT_FAMILY_FALLBACK,
    FONT_FAMILY_CODE,
    get_colors,
    get_theme_tuple,
    get_font,
)
from src.ui.components import (
    GlassCard,
    ModernButton,
    ModernEntry,
    IconButton,
    StepIndicator,
    FileDropZone,
    ProgressCard,
    InfoCard,
    SectionHeader,
)
GradientFrame = GlassCard
from src.ui.welcome_page import WelcomePage
from src.ui.upload_page import UploadPage
from src.ui.config_page import ConfigPage
from src.ui.build_page import BuildPage
from src.ui.result_page import ResultPage
from src.ui.settings_page import SettingsPage
from src.ui.main_window import MainWindow, HistoryPage

__all__ = [
    # Theme
    "COLORS",
    "LIGHT_COLORS",
    "FONTS",
    "FONT_FAMILY",
    "FONT_FAMILY_FALLBACK",
    "FONT_FAMILY_CODE",
    "get_colors",
    "get_theme_tuple",
    "get_font",
    # Components
    "GradientFrame",
    "ModernButton",
    "ModernEntry",
    "IconButton",
    "StepIndicator",
    "FileDropZone",
    "ProgressCard",
    "InfoCard",
    "SectionHeader",
    # Pages
    "WelcomePage",
    "UploadPage",
    "ConfigPage",
    "BuildPage",
    "ResultPage",
    "SettingsPage",
    "HistoryPage",
    # Main Window
    "MainWindow",
]
