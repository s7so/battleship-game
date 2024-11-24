# ألوان الثيم الأساسية
COLORS = {
    'primary': '#3498db',
    'primary_dark': '#2980b9',
    'success': '#2ecc71',
    'success_dark': '#27ae60',
    'danger': '#e74c3c',
    'danger_dark': '#c0392b',
    'warning': '#e67e22',
    'warning_dark': '#d35400',
    'water': '#bde0fe',
    'ship': '#495057',
    'hit': '#e74c3c',
    'miss': '#95a5a6',
    'hover': '#2980b9',
    'background': '#ffffff',
    'text': '#2c3e50',
}

# الستايل الأساسي للتطبيق
BASE_STYLE = f"""
* {{
    font-family: Arial, sans-serif;
    background-color: {COLORS['background']};
    color: {COLORS['text']};
}}

QPushButton {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    padding: 10px;
    border-radius: 5px;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:disabled {{
    background-color: {COLORS['miss']};
}}

QLabel {{
    color: {COLORS['text']};
    font-size: 14px;
    padding: 5px;
}}
"""

# ستايل خاص بأزرار الشبكة
GRID_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['water']};
    border: 1px solid {COLORS['primary']};
    min-width: 30px;
    min-height: 30px;
    padding: 0;
}}

QPushButton:hover {{
    border: 2px solid {COLORS['hover']};
}}
"""

# ستايل خاص بالحالات المختلفة للخلايا
CELL_STYLES = {
    'water': f"background-color: {COLORS['water']};",
    'ship': f"background-color: {COLORS['ship']};",
    'hit': f"background-color: {COLORS['hit']};",
    'miss': f"background-color: {COLORS['miss']};",
}

# ستايل خاص بلوحة الحالة
STATUS_STYLES = {
    'player_turn': f"""
        background-color: {COLORS['success']};
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    """,
    'ai_turn': f"""
        background-color: {COLORS['danger']};
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    """,
    'game_over': f"""
        background-color: {COLORS['warning']};
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    """
} 