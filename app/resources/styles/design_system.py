"""
نظام التصميم المتكامل - يحتوي على جميع الألوان والأنماط والتأثيرات.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ColorPalette:
    """لوحة الألوان الكاملة للنظام."""
    
    # الألوان الأساسية - أزرق بالكامل
    PRIMARY = "#1976D3"          # أزرق غامق (أساسي)
    PRIMARY_LIGHT = "#42A5F5"    # أزرق فاتح
    PRIMARY_DARK = "#0D47A1"     # أزرق داكن
    PRIMARY_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1976D3, stop:1 #42A5F5)"
    
    # الألوان الثانوية - أزرق آخر
    SECONDARY = "#1E88E5"        # أزرق متوسط
    SECONDARY_LIGHT = "#64B5F6"  # أزرق فاتح جداً
    SECONDARY_DARK = "#1565C0"   # أزرق داكن
    
    # ألوان النجاح والتحذير
    SUCCESS = "#10B981"
    SUCCESS_LIGHT = "#34D399"
    SUCCESS_DARK = "#059669"
    SUCCESS_BG = "#ECFDF5"
    
    WARNING = "#F59E0B"
    WARNING_LIGHT = "#FBBF24"
    WARNING_DARK = "#D97706"
    WARNING_BG = "#FFFBEB"
    
    DANGER = "#EF4444"
    DANGER_LIGHT = "#F87171"
    DANGER_DARK = "#DC2626"
    DANGER_BG = "#FEF2F2"
    
    INFO = "#3B82F6"
    INFO_LIGHT = "#60A5FA"
    INFO_DARK = "#2563EB"
    INFO_BG = "#EFF6FF"
    
    # ألوان محايدة
    BACKGROUND = "#F8FAFC"
    SURFACE = "#FFFFFF"
    SURFACE_VARIANT = "#F1F5F9"
    BORDER = "#E2E8F0"
    BORDER_LIGHT = "#F1F5F9"
    
    # ألوان النص
    TEXT_PRIMARY = "#0F172A"
    TEXT_SECONDARY = "#475569"
    TEXT_TERTIARY = "#94A3B8"
    TEXT_DISABLED = "#CBD5E1"
    TEXT_ON_PRIMARY = "#FFFFFF"
    TEXT_ON_DARK = "#E2E8F0"
    
    # ألوان داكنة
    DARK_BACKGROUND = "#0F172A"
    DARK_SURFACE = "#1E293B"
    DARK_SURFACE_VARIANT = "#334155"
    DARK_BORDER = "#475569"
    DARK_TEXT_PRIMARY = "#F1F5F9"
    DARK_TEXT_SECONDARY = "#CBD5E1"
    
    # ألوان خاصة للوحات - أزرق بالكامل
    DASHBOARD_CARD_1 = "#1976D3"  # أزرق
    DASHBOARD_CARD_2 = "#10B981"  # أخضر (تم الاحتفاظ به)
    DASHBOARD_CARD_3 = "#F59E0B"  # أصفر (تم الاحتفاظ به)
    DASHBOARD_CARD_4 = "#EF4444"  # أحمر (تم الاحتفاظ به)
    DASHBOARD_CARD_5 = "#1E88E5"  # أزرق
    DASHBOARD_CARD_6 = "#06B6D4"  # سماوي


@dataclass
class Typography:
    """نظام الخطوط."""
    
    # أحجام الخطوط
    SIZE_XS = 10
    SIZE_SM = 11
    SIZE_BASE = 12
    SIZE_MD = 13
    SIZE_LG = 14
    SIZE_XL = 16
    SIZE_2XL = 18
    SIZE_3XL = 20
    SIZE_4XL = 24
    SIZE_5XL = 30
    SIZE_6XL = 36
    
    # أوزان الخطوط
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700
    WEIGHT_EXTRABOLD = 800
    
    # عائلات الخطوط
    FAMILY_ARABIC = "Cairo"
    FAMILY_ENGLISH = "Segoe UI"
    FAMILY_MONO = "Consolas"


@dataclass
class Spacing:
    """نظام المسافات."""
    
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32
    XXXXL = 40
    XXXXXL = 48


@dataclass
class BorderRadius:
    """نظام نصف القطر."""
    
    SM = 4
    MD = 6
    LG = 8
    XL = 12
    XXL = 16
    FULL = 9999


@dataclass
class Shadow:
    """نظام الظلال."""
    
    SM = "0 1px 2px rgba(0, 0, 0, 0.05)"
    MD = "0 4px 6px rgba(0, 0, 0, 0.07)"
    LG = "0 10px 15px rgba(0, 0, 0, 0.1)"
    XL = "0 20px 25px rgba(0, 0, 0, 0.15)"
    XXL = "0 25px 50px rgba(0, 0, 0, 0.25)"


# إنشاء مثيلات النظام
colors = ColorPalette()
typography = Typography()
spacing = Spacing()
radius = BorderRadius()
shadows = Shadow()

# """
# نظام التصميم المتكامل - يحتوي على جميع الألوان والأنماط والتأثيرات.
# """

# from dataclasses import dataclass
# from typing import Dict, List, Tuple


# @dataclass
# class ColorPalette:
#     """لوحة الألوان الكاملة للنظام."""
    
#     # الألوان الأساسية
#     PRIMARY = "#6366F1"          # بنفسجي عصري
#     PRIMARY_LIGHT = "#818CF8"
#     PRIMARY_DARK = "#4F46E5"
#     PRIMARY_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366F1, stop:1 #8B5CF6)"
    
#     # الألوان الثانوية
#     SECONDARY = "#8B5CF6"
#     SECONDARY_LIGHT = "#A78BFA"
#     SECONDARY_DARK = "#7C3AED"
    
#     # ألوان النجاح والتحذير
#     SUCCESS = "#10B981"
#     SUCCESS_LIGHT = "#34D399"
#     SUCCESS_DARK = "#059669"
#     SUCCESS_BG = "#ECFDF5"
    
#     WARNING = "#F59E0B"
#     WARNING_LIGHT = "#FBBF24"
#     WARNING_DARK = "#D97706"
#     WARNING_BG = "#FFFBEB"
    
#     DANGER = "#EF4444"
#     DANGER_LIGHT = "#F87171"
#     DANGER_DARK = "#DC2626"
#     DANGER_BG = "#FEF2F2"
    
#     INFO = "#3B82F6"
#     INFO_LIGHT = "#60A5FA"
#     INFO_DARK = "#2563EB"
#     INFO_BG = "#EFF6FF"
    
#     # ألوان محايدة
#     BACKGROUND = "#F8FAFC"
#     SURFACE = "#FFFFFF"
#     SURFACE_VARIANT = "#F1F5F9"
#     BORDER = "#E2E8F0"
#     BORDER_LIGHT = "#F1F5F9"
    
#     # ألوان النص
#     TEXT_PRIMARY = "#0F172A"
#     TEXT_SECONDARY = "#475569"
#     TEXT_TERTIARY = "#94A3B8"
#     TEXT_DISABLED = "#CBD5E1"
#     TEXT_ON_PRIMARY = "#FFFFFF"
#     TEXT_ON_DARK = "#E2E8F0"
    
#     # ألوان داكنة
#     DARK_BACKGROUND = "#0F172A"
#     DARK_SURFACE = "#1E293B"
#     DARK_SURFACE_VARIANT = "#334155"
#     DARK_BORDER = "#475569"
#     DARK_TEXT_PRIMARY = "#F1F5F9"
#     DARK_TEXT_SECONDARY = "#CBD5E1"
    
#     # ألوان خاصة للوحات
#     DASHBOARD_CARD_1 = "#6366F1"
#     DASHBOARD_CARD_2 = "#10B981"
#     DASHBOARD_CARD_3 = "#F59E0B"
#     DASHBOARD_CARD_4 = "#EF4444"
#     DASHBOARD_CARD_5 = "#8B5CF6"
#     DASHBOARD_CARD_6 = "#06B6D4"


# @dataclass
# class Typography:
#     """نظام الخطوط."""
    
#     # أحجام الخطوط
#     SIZE_XS = 10
#     SIZE_SM = 11
#     SIZE_BASE = 12
#     SIZE_MD = 13
#     SIZE_LG = 14
#     SIZE_XL = 16
#     SIZE_2XL = 18
#     SIZE_3XL = 20
#     SIZE_4XL = 24
#     SIZE_5XL = 30
#     SIZE_6XL = 36
    
#     # أوزان الخطوط
#     WEIGHT_NORMAL = 400
#     WEIGHT_MEDIUM = 500
#     WEIGHT_SEMIBOLD = 600
#     WEIGHT_BOLD = 700
#     WEIGHT_EXTRABOLD = 800
    
#     # عائلات الخطوط
#     FAMILY_ARABIC = "Cairo"
#     FAMILY_ENGLISH = "Segoe UI"
#     FAMILY_MONO = "Consolas"


# @dataclass
# class Spacing:
#     """نظام المسافات."""
    
#     XS = 4
#     SM = 8
#     MD = 12
#     LG = 16
#     XL = 20
#     XXL = 24
#     XXXL = 32
#     XXXXL = 40
#     XXXXXL = 48


# @dataclass
# class BorderRadius:
#     """نظام نصف القطر."""
    
#     SM = 4
#     MD = 6
#     LG = 8
#     XL = 12
#     XXL = 16
#     FULL = 9999


# @dataclass
# class Shadow:
#     """نظام الظلال."""
    
#     SM = "0 1px 2px rgba(0, 0, 0, 0.05)"
#     MD = "0 4px 6px rgba(0, 0, 0, 0.07)"
#     LG = "0 10px 15px rgba(0, 0, 0, 0.1)"
#     XL = "0 20px 25px rgba(0, 0, 0, 0.15)"
#     XXL = "0 25px 50px rgba(0, 0, 0, 0.25)"


# # إنشاء مثيلات النظام
# colors = ColorPalette()
# typography = Typography()
# spacing = Spacing()
# radius = BorderRadius()
# shadows = Shadow()

