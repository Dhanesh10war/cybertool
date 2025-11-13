"""
CyberTool - Modular Red/Blue Team Desktop Application
Main entry point with PyQt6 GUI
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTextEdit, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont
from datetime import datetime

# Import custom modules
from red_team import RedTeamModule
from blue_team import BlueTeamModule
from database import DatabaseManager
from logger import AuditLogger
from ui.styles import DARK_THEME


class MainWindow(QMainWindow):
    """
    Main application window with tabbed interface for Red Team, Blue Team,
    Settings, and Logs functionality.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberTool v1.0 - Red/Blue Team Platform")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize core components
        self.db_manager = DatabaseManager()
        self.audit_logger = AuditLogger()
        
        # Log application startup
        self.audit_logger.log_event("SYSTEM", "Application started", "INFO")
        
        # Setup UI
        self.init_ui()
        
        # Apply dark theme
        self.setStyleSheet(DARK_THEME)
        
        # Setup status bar updates
        self.setup_status_updates()
        
    def init_ui(self):
        """Initialize the user interface components."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create tabbed interface
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        # Dashboard tab
        self.dashboard_tab = self.create_dashboard()
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        
        # Red Team tab
        self.red_team_module = RedTeamModule(self.db_manager, self.audit_logger)
        self.tabs.addTab(self.red_team_module, "🔴 Red Team")
        
        # Blue Team tab
        self.blue_team_module = BlueTeamModule(self.db_manager, self.audit_logger)
        self.tabs.addTab(self.blue_team_module, "🔵 Blue Team")
        
        # Logs tab
        self.logs_tab = self.create_logs_tab()
        self.tabs.addTab(self.logs_tab, "📋 Audit Logs")
        
        # Settings tab
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, "⚙️ Settings")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def create_header(self):
        """Create application header with branding."""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        title_label = QLabel("🛡️ CyberTool Platform")
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        title_label.setFont(title_font)
        
        subtitle_label = QLabel("Integrated Red Team & Blue Team Operations")
        subtitle_label.setStyleSheet("color: #888; font-size: 12px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        
        return header
        
    def create_dashboard(self):
        """Create dashboard overview tab."""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        
        # Welcome section
        welcome_label = QLabel("Welcome to CyberTool")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(welcome_label)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(200)
        info_text.setPlainText(
            "CyberTool is a modular cybersecurity platform for:\n\n"
            "🔴 RED TEAM Operations:\n"
            "   • Safe reconnaissance and port scanning\n"
            "   • Service fingerprinting\n"
            "   • Credential validation (non-destructive)\n"
            "   • Vulnerability verification\n\n"
            "🔵 BLUE TEAM Operations:\n"
            "   • Local system monitoring\n"
            "   • Log collection and analysis\n"
            "   • Process scanning\n"
            "   • Anomaly detection and alerting\n\n"
            "⚠️ Always obtain proper authorization before conducting any security assessments."
        )
        layout.addWidget(info_text)
        
        # Quick stats section
        stats_label = QLabel("Session Statistics")
        stats_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(stats_label)
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(150)
        self.update_dashboard_stats()
        layout.addWidget(self.stats_display)
        
        layout.addStretch()
        
        return dashboard
        
    def create_logs_tab(self):
        """Create audit logs viewing tab."""
        logs_widget = QWidget()
        layout = QVBoxLayout(logs_widget)
        
        # Header
        header_layout = QHBoxLayout()
        logs_label = QLabel("Audit Logs")
        logs_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(logs_label)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_logs)
        header_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("🗑️ Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(clear_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Logs display
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        self.logs_display.setFont(QFont("Courier", 9))
        layout.addWidget(self.logs_display)
        
        self.refresh_logs()
        
        return logs_widget
        
    def create_settings_tab(self):
        """Create settings and configuration tab."""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        settings_label = QLabel("Settings & Configuration")
        settings_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(settings_label)
        
        settings_text = QTextEdit()
        settings_text.setReadOnly(True)
        settings_text.setPlainText(
            "Application Settings:\n\n"
            "Database: SQLite (cybertool.db)\n"
            "Log Level: INFO\n"
            "Theme: Dark Mode\n"
            "Auto-save: Enabled\n\n"
            "Security Settings:\n"
            "• Scope enforcement: Enabled\n"
            "• Consent verification: Required\n"
            "• Audit logging: Enabled\n"
            "• Session timeout: 30 minutes\n\n"
            "Export Formats: CSV, JSON\n"
        )
        layout.addWidget(settings_text)
        
        # Database management
        db_label = QLabel("Database Management")
        db_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(db_label)
        
        db_layout = QHBoxLayout()
        
        backup_btn = QPushButton("💾 Backup Database")
        backup_btn.clicked.connect(self.backup_database)
        db_layout.addWidget(backup_btn)
        
        optimize_btn = QPushButton("⚡ Optimize Database")
        optimize_btn.clicked.connect(self.optimize_database)
        db_layout.addWidget(optimize_btn)
        
        db_layout.addStretch()
        layout.addLayout(db_layout)
        
        layout.addStretch()
        
        return settings_widget
        
    def setup_status_updates(self):
        """Setup periodic status bar updates."""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_bar)
        self.status_timer.start(5000)  # Update every 5 seconds
        
    def update_status_bar(self):
        """Update status bar with current information."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_bar.showMessage(f"Ready | {current_time}")
        
    def update_dashboard_stats(self):
        """Update dashboard statistics."""
        stats = self.db_manager.get_session_statistics()
        stats_text = (
            f"Total Sessions: {stats['total_sessions']}\n"
            f"Red Team Scans: {stats['red_team_sessions']}\n"
            f"Blue Team Monitors: {stats['blue_team_sessions']}\n"
            f"Total Alerts: {stats['total_alerts']}\n"
            f"Last Activity: {stats['last_activity']}"
        )
        self.stats_display.setPlainText(stats_text)
        
    def refresh_logs(self):
        """Refresh audit logs display."""
        logs = self.audit_logger.get_recent_logs(limit=100)
        self.logs_display.setPlainText("\n".join(logs))
        self.logs_display.verticalScrollBar().setValue(
            self.logs_display.verticalScrollBar().maximum()
        )
        
    def clear_logs(self):
        """Clear audit logs with confirmation."""
        reply = QMessageBox.question(
            self, "Clear Logs",
            "Are you sure you want to clear all audit logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.audit_logger.clear_logs()
            self.refresh_logs()
            self.audit_logger.log_event("SYSTEM", "Audit logs cleared by user", "WARNING")
            
    def backup_database(self):
        """Backup database to file."""
        success = self.db_manager.backup_database()
        if success:
            QMessageBox.information(self, "Backup", "Database backed up successfully!")
            self.audit_logger.log_event("SYSTEM", "Database backup created", "INFO")
        else:
            QMessageBox.warning(self, "Backup", "Database backup failed!")
            
    def optimize_database(self):
        """Optimize database performance."""
        self.db_manager.optimize_database()
        QMessageBox.information(self, "Optimize", "Database optimized successfully!")
        self.audit_logger.log_event("SYSTEM", "Database optimized", "INFO")
        
    def closeEvent(self, event):
        """Handle application closure."""
        self.audit_logger.log_event("SYSTEM", "Application closing", "INFO")
        
        # Clean up resources
        self.red_team_module.cleanup()
        self.blue_team_module.cleanup()
        self.db_manager.close()
        
        event.accept()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("CyberTool")
    app.setOrganizationName("SecOps")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()