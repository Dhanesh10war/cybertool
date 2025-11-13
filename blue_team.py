"""
Blue Team Module - Defensive Security Operations
Includes system monitoring, log collection, and anomaly detection
"""

import psutil
import platform
import threading
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QCheckBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
import json


class SystemMonitorThread(QThread):
    """
    Background thread for continuous system monitoring.
    Emits signals for real-time UI updates.
    """
    
    # Signals for thread-safe updates
    stats_update = pyqtSignal(dict)
    alert_generated = pyqtSignal(str, str, str)  # severity, category, message
    
    def __init__(self, check_interval=5):
        super().__init__()
        self.check_interval = check_interval
        self.is_running = True
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0
        }
        
    def run(self):
        """Execute monitoring loop in separate thread."""
        while self.is_running:
            try:
                stats = self.collect_system_stats()
                self.stats_update.emit(stats)
                
                # Check for anomalies
                self.check_thresholds(stats)
                
                # Sleep for interval
                self.msleep(self.check_interval * 1000)
                
            except Exception as e:
                self.alert_generated.emit("ERROR", "Monitor", f"Monitoring error: {str(e)}")
                
    def collect_system_stats(self):
        """Collect current system statistics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_connections": len(psutil.net_connections()),
            "running_processes": len(psutil.pids()),
            "timestamp": datetime.now().isoformat()
        }
        
    def check_thresholds(self, stats):
        """Check if any metrics exceed thresholds and generate alerts."""
        if stats["cpu_percent"] > self.thresholds["cpu_percent"]:
            self.alert_generated.emit(
                "HIGH",
                "CPU",
                f"CPU usage critical: {stats['cpu_percent']:.1f}%"
            )
            
        if stats["memory_percent"] > self.thresholds["memory_percent"]:
            self.alert_generated.emit(
                "HIGH",
                "Memory",
                f"Memory usage critical: {stats['memory_percent']:.1f}%"
            )
            
        if stats["disk_percent"] > self.thresholds["disk_percent"]:
            self.alert_generated.emit(
                "CRITICAL",
                "Disk",
                f"Disk usage critical: {stats['disk_percent']:.1f}%"
            )
            
    def update_thresholds(self, thresholds):
        """Update alert thresholds."""
        self.thresholds = thresholds
        
    def stop(self):
        """Stop monitoring gracefully."""
        self.is_running = False


class ProcessMonitorThread(QThread):
    """
    Thread for monitoring running processes and detecting suspicious activity.
    """
    
    process_list_update = pyqtSignal(list)
    suspicious_process = pyqtSignal(str, str)  # process name, reason
    
    def __init__(self, scan_interval=10):
        super().__init__()
        self.scan_interval = scan_interval
        self.is_running = True
        self.known_processes = set()
        
    def run(self):
        """Execute process monitoring loop."""
        while self.is_running:
            try:
                processes = self.scan_processes()
                self.process_list_update.emit(processes)
                
                # Detect new processes
                self.detect_new_processes(processes)
                
                self.msleep(self.scan_interval * 1000)
                
            except Exception as e:
                pass  # Silently handle errors in background
                
    def scan_processes(self):
        """Scan and return list of running processes."""
        process_list = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent']):
            try:
                process_list.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'user': proc.info['username'] or 'N/A',
                    'memory': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return process_list
        
    def detect_new_processes(self, processes):
        """Detect and alert on new processes."""
        current_pids = {p['pid'] for p in processes}
        new_pids = current_pids - self.known_processes
        
        if self.known_processes and new_pids:  # Skip first run
            for pid in new_pids:
                for proc in processes:
                    if proc['pid'] == pid:
                        # Check for suspicious indicators (placeholder logic)
                        if self.is_suspicious(proc['name']):
                            self.suspicious_process.emit(
                                proc['name'],
                                "New process detected"
                            )
                        break
                        
        self.known_processes = current_pids
        
    def is_suspicious(self, process_name):
        """
        Basic heuristic for suspicious process names.
        This is a placeholder - real detection would be more sophisticated.
        """
        suspicious_keywords = ['hack', 'crack', 'exploit', 'backdoor', 'keylog']
        return any(keyword in process_name.lower() for keyword in suspicious_keywords)
        
    def stop(self):
        """Stop process monitoring."""
        self.is_running = False


class BlueTeamModule(QWidget):
    """
    Blue Team operations interface with system monitoring,
    log collection, and real-time alerting.
    """
    
    def __init__(self, db_manager, audit_logger):
        super().__init__()
        self.db_manager = db_manager
        self.audit_logger = audit_logger
        self.monitor_thread = None
        self.process_thread = None
        self.alerts = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize Blue Team interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("🔵 Blue Team Operations")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # System info section
        sysinfo_group = self.create_system_info_section()
        layout.addWidget(sysinfo_group)
        
        # Control section
        control_group = self.create_control_section()
        layout.addWidget(control_group)
        
        # Real-time stats display
        stats_group = self.create_stats_section()
        layout.addWidget(stats_group)
        
        # Alerts display
        alerts_group = self.create_alerts_section()
        layout.addWidget(alerts_group)
        
    def create_system_info_section(self):
        """Create system information display."""
        group = QGroupBox("System Information")
        layout = QVBoxLayout()
        
        info_text = (
            f"Platform: {platform.system()} {platform.release()}\n"
            f"Machine: {platform.machine()}\n"
            f"Processor: {platform.processor()}\n"
            f"Python: {platform.python_version()}"
        )
        
        info_label = QLabel(info_text)
        info_label.setFont(QFont("Courier", 9))
        layout.addWidget(info_label)
        
        group.setLayout(layout)
        return group
        
    def create_control_section(self):
        """Create monitoring control section."""
        group = QGroupBox("Monitoring Controls")
        layout = QVBoxLayout()
        
        # Monitoring toggle
        toggle_layout = QHBoxLayout()
        
        self.monitor_active = QCheckBox("Enable Real-time Monitoring")
        self.monitor_active.stateChanged.connect(self.toggle_monitoring)
        toggle_layout.addWidget(self.monitor_active)
        
        self.process_monitor = QCheckBox("Enable Process Monitoring")
        self.process_monitor.stateChanged.connect(self.toggle_process_monitoring)
        toggle_layout.addWidget(self.process_monitor)
        
        toggle_layout.addStretch()
        layout.addLayout(toggle_layout)
        
        # Interval settings
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Check Interval (seconds):"))
        
        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 60)
        self.interval_input.setValue(5)
        interval_layout.addWidget(self.interval_input)
        
        interval_layout.addStretch()
        layout.addLayout(interval_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("💾 Export Alerts")
        export_btn.clicked.connect(self.export_alerts)
        button_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("🗑️ Clear Alerts")
        clear_btn.clicked.connect(self.clear_alerts)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        return group
        
    def create_stats_section(self):
        """Create real-time statistics display."""
        group = QGroupBox("Real-time System Statistics")
        layout = QVBoxLayout()
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(150)
        self.stats_display.setFont(QFont("Courier", 9))
        self.stats_display.setPlainText("Monitoring inactive. Enable monitoring to see real-time stats.")
        layout.addWidget(self.stats_display)
        
        group.setLayout(layout)
        return group
        
    def create_alerts_section(self):
        """Create alerts display section."""
        group = QGroupBox("Security Alerts")
        layout = QVBoxLayout()
        
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(4)
        self.alerts_table.setHorizontalHeaderLabels(["Time", "Severity", "Category", "Message"])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.alerts_table.setAlternatingRowColors(True)
        layout.addWidget(self.alerts_table)
        
        group.setLayout(layout)
        return group
        
    def toggle_monitoring(self, state):
        """Start or stop system monitoring."""
        if state == 2:  # Checked
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def toggle_process_monitoring(self, state):
        """Start or stop process monitoring."""
        if state == 2:  # Checked
            self.start_process_monitoring()
        else:
            self.stop_process_monitoring()
            
    def start_monitoring(self):
        """Start system monitoring thread."""
        interval = self.interval_input.value()
        
        self.monitor_thread = SystemMonitorThread(check_interval=interval)
        self.monitor_thread.stats_update.connect(self.update_stats)
        self.monitor_thread.alert_generated.connect(self.add_alert)
        self.monitor_thread.start()
        
        self.audit_logger.log_event("BLUE_TEAM", "System monitoring started", "INFO")
        self.stats_display.setPlainText("Monitoring active...\n")
        
    def stop_monitoring(self):
        """Stop system monitoring thread."""
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            
        self.audit_logger.log_event("BLUE_TEAM", "System monitoring stopped", "INFO")
        self.stats_display.setPlainText("Monitoring stopped.")
        
    def start_process_monitoring(self):
        """Start process monitoring thread."""
        self.process_thread = ProcessMonitorThread()
        self.process_thread.suspicious_process.connect(self.handle_suspicious_process)
        self.process_thread.start()
        
        self.audit_logger.log_event("BLUE_TEAM", "Process monitoring started", "INFO")
        
    def stop_process_monitoring(self):
        """Stop process monitoring thread."""
        if self.process_thread and self.process_thread.isRunning():
            self.process_thread.stop()
            self.process_thread.wait()
            
        self.audit_logger.log_event("BLUE_TEAM", "Process monitoring stopped", "INFO")
        
    def update_stats(self, stats):
        """Update statistics display (thread-safe via signal)."""
        stats_text = (
            f"{'='*50}\n"
            f"System Statistics - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{'='*50}\n"
            f"CPU Usage: {stats['cpu_percent']:.1f}%\n"
            f"Memory Usage: {stats['memory_percent']:.1f}%\n"
            f"Disk Usage: {stats['disk_percent']:.1f}%\n"
            f"Network Connections: {stats['network_connections']}\n"
            f"Running Processes: {stats['running_processes']}\n"
        )
        self.stats_display.setPlainText(stats_text)
        
    def add_alert(self, severity, category, message):
        """Add alert to table (thread-safe via signal)."""
        row = self.alerts_table.rowCount()
        self.alerts_table.insertRow(row)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Set color based on severity
        severity_colors = {
            "LOW": QColor("#4a9eff"),
            "MEDIUM": QColor("#ffb84a"),
            "HIGH": QColor("#ff6b6b"),
            "CRITICAL": QColor("#ff0000")
        }
        
        time_item = QTableWidgetItem(timestamp)
        severity_item = QTableWidgetItem(severity)
        category_item = QTableWidgetItem(category)
        message_item = QTableWidgetItem(message)
        
        # Apply color to severity
        if severity in severity_colors:
            severity_item.setForeground(severity_colors[severity])
            
        self.alerts_table.setItem(row, 0, time_item)
        self.alerts_table.setItem(row, 1, severity_item)
        self.alerts_table.setItem(row, 2, category_item)
        self.alerts_table.setItem(row, 3, message_item)
        
        # Store alert
        alert_data = {
            "timestamp": timestamp,
            "severity": severity,
            "category": category,
            "message": message
        }
        self.alerts.append(alert_data)
        
        # Store in database
        self.db_manager.store_alert(severity, category, message)
        
        # Log to audit
        self.audit_logger.log_event("BLUE_TEAM", f"Alert: [{severity}] {category} - {message}", "WARNING")
        
        # Scroll to bottom
        self.alerts_table.scrollToBottom()
        
    def handle_suspicious_process(self, process_name, reason):
        """Handle detection of suspicious process."""
        self.add_alert("HIGH", "Process", f"Suspicious: {process_name} - {reason}")
        
    def export_alerts(self):
        """Export alerts to JSON file."""
        if not self.alerts:
            QMessageBox.warning(self, "Export", "No alerts to export!")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blueteam_alerts_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.alerts, f, indent=2)
                
            QMessageBox.information(self, "Export", f"Alerts exported to {filename}")
            self.audit_logger.log_event("BLUE_TEAM", f"Alerts exported to {filename}", "INFO")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
            
    def clear_alerts(self):
        """Clear all alerts from display."""
        reply = QMessageBox.question(
            self, "Clear Alerts",
            "Clear all alerts from display?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.alerts_table.setRowCount(0)
            self.alerts.clear()
            self.audit_logger.log_event("BLUE_TEAM", "Alerts cleared by user", "INFO")
            
    def cleanup(self):
        """Clean up resources on module close."""
        self.stop_monitoring()
        self.stop_process_monitoring()