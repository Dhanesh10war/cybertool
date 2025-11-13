"""
UI Styles - Modern dark theme for the application
Professional cybersecurity aesthetic with clean design
"""

DARK_THEME = """
/* Main Application Styling */
QMainWindow {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #3d3d3d;
    background-color: #252525;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #b0b0b0;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border: 1px solid #3d3d3d;
}

QTabBar::tab:selected {
    background-color: #252525;
    color: #ffffff;
    border-bottom: 2px solid #4a9eff;
}

QTabBar::tab:hover {
    background-color: #353535;
}

/* Buttons */
QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #3d3d3d;
    border: 1px solid #4a9eff;
}

QPushButton:pressed {
    background-color: #1d1d1d;
}

QPushButton:disabled {
    background-color: #1d1d1d;
    color: #666666;
    border: 1px solid #2d2d2d;
}

/* Input Fields */
QLineEdit, QSpinBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    padding: 6px;
    border-radius: 4px;
    selection-background-color: #4a9eff;
}

QLineEdit:focus, QSpinBox:focus {
    border: 1px solid #4a9eff;
}

QLineEdit:disabled, QSpinBox:disabled {
    background-color: #1d1d1d;
    color: #666666;
}

/* Text Areas */
QTextEdit {
    background-color: #1a1a1a;
    color: #e0e0e0;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 8px;
    selection-background-color: #4a9eff;
}

/* Progress Bar */
QProgressBar {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    text-align: center;
    color: #e0e0e0;
    height: 24px;
}

QProgressBar::chunk {
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #4a9eff,
        stop:1 #357abd
    );
    border-radius: 3px;
}

/* Group Boxes */
QGroupBox {
    background-color: #252525;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    color: #4a9eff;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #e0e0e0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    background-color: #2d2d2d;
}

QCheckBox::indicator:hover {
    border: 1px solid #4a9eff;
}

QCheckBox::indicator:checked {
    background-color: #4a9eff;
    border: 1px solid #4a9eff;
}

QCheckBox::indicator:checked:hover {
    background-color: #357abd;
}

/* Labels */
QLabel {
    color: #e0e0e0;
    background-color: transparent;
}

/* Status Bar */
QStatusBar {
    background-color: #1a1a1a;
    color: #b0b0b0;
    border-top: 1px solid #3d3d3d;
}

/* Tables */
QTableWidget {
    background-color: #1a1a1a;
    alternate-background-color: #222222;
    gridline-color: #3d3d3d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    selection-background-color: #4a9eff;
}

QTableWidget::item {
    padding: 6px;
    color: #e0e0e0;
}

QTableWidget::item:selected {
    background-color: #4a9eff;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #e0e0e0;
    padding: 8px;
    border: none;
    border-right: 1px solid #3d3d3d;
    border-bottom: 1px solid #3d3d3d;
    font-weight: 600;
}

QHeaderView::section:first {
    border-left: none;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #4d4d4d;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5d5d5d;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #4d4d4d;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #5d5d5d;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Spin Box Buttons */
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #3d3d3d;
    border: none;
    width: 16px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #4a9eff;
}

QSpinBox::up-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 4px solid #e0e0e0;
}

QSpinBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #e0e0e0;
}

/* Message Boxes */
QMessageBox {
    background-color: #1e1e1e;
}

QMessageBox QLabel {
    color: #e0e0e0;
}

/* Tooltips */
QToolTip {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #4a9eff;
    padding: 4px;
    border-radius: 4px;
}

/* Menu Bar (if added later) */
QMenuBar {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border-bottom: 1px solid #3d3d3d;
}

QMenuBar::item:selected {
    background-color: #2d2d2d;
}

QMenu {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
}

QMenu::item {
    padding: 6px 24px;
    color: #e0e0e0;
}

QMenu::item:selected {
    background-color: #4a9eff;
}
"""

# Alternative color schemes that can be used
LIGHT_THEME = """
/* Light theme alternative (for future use) */
QWidget {
    background-color: #f5f5f5;
    color: #1e1e1e;
}
"""

# Custom color palette
COLORS = {
    'primary': '#4a9eff',
    'success': '#4caf50',
    'warning': '#ffb84a',
    'danger': '#ff6b6b',
    'info': '#17a2b8',
    'dark': '#1e1e1e',
    'light': '#e0e0e0'
}

# Severity -> color mapping used across the UI for alerts/logs
SEVERITY_COLORS = {
    'low': COLORS['success'],
    'medium': COLORS['warning'],
    'high': COLORS['danger'],
    'critical': '#c62828'
}

# Log level -> color mapping for display of logs
LOG_LEVEL_COLORS = {
    'DEBUG': '#9e9e9e',
    'INFO': COLORS['primary'],
    'WARNING': COLORS['warning'],
    'ERROR': COLORS['danger'],
    'CRITICAL': '#b71c1c'
}