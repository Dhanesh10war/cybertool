"""
Red Team Module - Offensive Security Operations
Includes port scanning, service detection, and reconnaissance tools
"""

import socket
import threading
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QProgressBar, QSpinBox, QCheckBox, QMessageBox, QGroupBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
import json


class PortScannerThread(QThread):
    """
    Threaded port scanner to prevent UI blocking.
    Emits signals for progress updates and results.
    """
    
    # Signals for thread-safe UI updates
    progress_update = pyqtSignal(int)
    result_update = pyqtSignal(str, int, str)
    scan_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, target, start_port, end_port, timeout=1.0):
        super().__init__()
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.is_running = True
        self.open_ports = []
        
    def run(self):
        """Execute port scan in separate thread."""
        try:
            total_ports = self.end_port - self.start_port + 1
            scanned = 0
            
            for port in range(self.start_port, self.end_port + 1):
                if not self.is_running:
                    break
                    
                status = self.scan_port(self.target, port)
                
                if status == "open":
                    self.open_ports.append(port)
                    service = self.identify_service(port)
                    self.result_update.emit(self.target, port, service)
                
                scanned += 1
                progress = int((scanned / total_ports) * 100)
                self.progress_update.emit(progress)
            
            # Emit completion signal with results
            results = {
                "target": self.target,
                "start_port": self.start_port,
                "end_port": self.end_port,
                "open_ports": self.open_ports,
                "scan_time": datetime.now().isoformat()
            }
            self.scan_complete.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(f"Scan error: {str(e)}")
    
    def scan_port(self, host, port):
        """
        Scan a single port on target host.
        Returns 'open' if port is accessible, 'closed' otherwise.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return "open" if result == 0 else "closed"
        except socket.gaierror:
            return "error"
        except Exception:
            return "closed"
    
    def identify_service(self, port):
        """
        Identify common services by port number.
        Returns service name or 'unknown'.
        """
        common_ports = {
            20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET",
            25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
            143: "IMAP", 443: "HTTPS", 445: "SMB", 3306: "MySQL",
            3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
            6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
            27017: "MongoDB"
        }
        return common_ports.get(port, "unknown")
    
    def stop(self):
        """Stop the scanning thread gracefully."""
        self.is_running = False


class RedTeamModule(QWidget):
    """
    Red Team operations interface with port scanning,
    service detection, and result export capabilities.
    """
    
    def __init__(self, db_manager, audit_logger):
        super().__init__()
        self.db_manager = db_manager
        self.audit_logger = audit_logger
        self.scanner_thread = None
        self.current_session_id = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize Red Team interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("🔴 Red Team Operations")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Consent and scope section
        consent_group = self.create_consent_section()
        layout.addWidget(consent_group)
        
        # Scanner configuration
        config_group = self.create_config_section()
        layout.addWidget(config_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start Scan")
        self.start_btn.clicked.connect(self.start_scan)
        self.start_btn.setEnabled(False)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop Scan")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.export_btn = QPushButton("💾 Export Results")
        self.export_btn.clicked.connect(self.export_results)
        control_layout.addWidget(self.export_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Results display
        results_label = QLabel("Scan Results:")
        results_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(results_label)
        
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setFont(QFont("Courier", 9))
        layout.addWidget(self.results_display)
        
    def create_consent_section(self):
        """Create scope and consent verification section."""
        group = QGroupBox("⚠️ Authorization & Scope")
        layout = QVBoxLayout()
        
        warning_label = QLabel(
            "WARNING: Only scan systems you own or have explicit written permission to test.\n"
            "Unauthorized scanning may be illegal and unethical."
        )
        warning_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)
        
        self.consent_checkbox = QCheckBox(
            "I confirm I have authorization to scan the specified target"
        )
        self.consent_checkbox.stateChanged.connect(self.update_start_button)
        layout.addWidget(self.consent_checkbox)
        
        group.setLayout(layout)
        return group
        
    def create_config_section(self):
        """Create scanner configuration section."""
        group = QGroupBox("Scanner Configuration")
        layout = QVBoxLayout()
        
        # Target input
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target IP/Host:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("e.g., 192.168.1.1 or localhost")
        self.target_input.textChanged.connect(self.update_start_button)
        target_layout.addWidget(self.target_input)
        layout.addLayout(target_layout)
        
        # Port range
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port Range:"))
        
        self.start_port = QSpinBox()
        self.start_port.setRange(1, 65535)
        self.start_port.setValue(1)
        port_layout.addWidget(self.start_port)
        
        port_layout.addWidget(QLabel("to"))
        
        self.end_port = QSpinBox()
        self.end_port.setRange(1, 65535)
        self.end_port.setValue(1000)
        port_layout.addWidget(self.end_port)
        
        port_layout.addStretch()
        layout.addLayout(port_layout)
        
        # Timeout setting
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout (seconds):"))
        
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(1, 10)
        self.timeout_input.setValue(1)
        timeout_layout.addWidget(self.timeout_input)
        
        timeout_layout.addStretch()
        layout.addLayout(timeout_layout)
        
        group.setLayout(layout)
        return group
        
    def update_start_button(self):
        """Enable/disable start button based on consent and target."""
        has_consent = self.consent_checkbox.isChecked()
        has_target = len(self.target_input.text().strip()) > 0
        self.start_btn.setEnabled(has_consent and has_target)
        
    def start_scan(self):
        """Initiate port scan with validation."""
        target = self.target_input.text().strip()
        start_port = self.start_port.value()
        end_port = self.end_port.value()
        timeout = self.timeout_input.value()
        
        # Validate port range
        if start_port > end_port:
            QMessageBox.warning(self, "Invalid Range", 
                              "Start port must be less than or equal to end port!")
            return
        
        # Clear previous results
        self.results_display.clear()
        self.progress_bar.setValue(0)
        
        # Create session in database
        self.current_session_id = self.db_manager.create_session(
            "red_team", target, {"start_port": start_port, "end_port": end_port}
        )
        
        # Log scan start
        self.audit_logger.log_event(
            "RED_TEAM", 
            f"Port scan started: {target} ports {start_port}-{end_port}",
            "INFO"
        )
        
        # Create and start scanner thread
        self.scanner_thread = PortScannerThread(target, start_port, end_port, timeout)
        self.scanner_thread.progress_update.connect(self.update_progress)
        self.scanner_thread.result_update.connect(self.display_result)
        self.scanner_thread.scan_complete.connect(self.scan_finished)
        self.scanner_thread.error_occurred.connect(self.handle_error)
        self.scanner_thread.start()
        
        # Update UI state
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.results_display.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning {target}...\n")
        
    def stop_scan(self):
        """Stop running scan."""
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.stop()
            self.scanner_thread.wait()
            self.results_display.append(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scan stopped by user\n")
            self.audit_logger.log_event("RED_TEAM", "Port scan stopped by user", "WARNING")
            
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def update_progress(self, value):
        """Update progress bar (thread-safe via signal)."""
        self.progress_bar.setValue(value)
        
    def display_result(self, target, port, service):
        """Display scan result (thread-safe via signal)."""
        result_text = f"[OPEN] {target}:{port} - {service}"
        self.results_display.append(result_text)
        
        # Store result in database
        if self.current_session_id:
            self.db_manager.store_scan_result(
                self.current_session_id, port, service, "open"
            )
        
    def scan_finished(self, results):
        """Handle scan completion."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        summary = (
            f"\n{'='*50}\n"
            f"Scan Complete!\n"
            f"Target: {results['target']}\n"
            f"Ports Scanned: {results['start_port']}-{results['end_port']}\n"
            f"Open Ports Found: {len(results['open_ports'])}\n"
            f"Time: {results['scan_time']}\n"
            f"{'='*50}\n"
        )
        self.results_display.append(summary)
        
        # Update session in database
        if self.current_session_id:
            self.db_manager.update_session(self.current_session_id, results)
        
        self.audit_logger.log_event(
            "RED_TEAM",
            f"Port scan completed: {results['target']} - {len(results['open_ports'])} open ports",
            "INFO"
        )
        
    def handle_error(self, error_msg):
        """Handle scan errors."""
        self.results_display.append(f"\n[ERROR] {error_msg}\n")
        self.audit_logger.log_event("RED_TEAM", f"Scan error: {error_msg}", "ERROR")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def export_results(self):
        """Export scan results to JSON file."""
        results_text = self.results_display.toPlainText()
        
        if not results_text.strip():
            QMessageBox.warning(self, "Export", "No results to export!")
            return
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"redteam_scan_{timestamp}.json"
        
        # Prepare export data
        export_data = {
            "scan_type": "port_scan",
            "timestamp": datetime.now().isoformat(),
            "target": self.target_input.text().strip(),
            "results": results_text
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            QMessageBox.information(self, "Export", f"Results exported to {filename}")
            self.audit_logger.log_event("RED_TEAM", f"Results exported to {filename}", "INFO")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")
            
    def cleanup(self):
        """Clean up resources on module close."""
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.stop()
            self.scanner_thread.wait()