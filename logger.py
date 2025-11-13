"""
Audit Logger - Unified logging system for security operations
Provides comprehensive audit trail of all application activities
"""

import logging
import threading
from datetime import datetime
from pathlib import Path
import json


class AuditLogger:
    """
    Centralized audit logging system for security operations.
    Provides structured logging with categories, severity levels,
    and persistent storage. Thread-safe implementation.
    """
    
    # Log level mappings
    LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    def __init__(self, log_file="cybertool_audit.log", max_size_mb=10):
        """
        Initialize audit logger with file rotation.
        
        Args:
            log_file: Path to log file
            max_size_mb: Maximum size in MB before rotation
        """
        self.log_file = log_file
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.lock = threading.Lock()
        self.memory_buffer = []
        self.max_memory_logs = 1000
        
        self.setup_logger()
        
    def setup_logger(self):
        """Configure logging system with formatting and handlers."""
        # Create logger
        self.logger = logging.getLogger('CyberToolAudit')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create file handler with rotation
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(category)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log initialization
        self.log_event("SYSTEM", "Audit logger initialized", "INFO")
        
    def log_event(self, category, message, level="INFO", extra_data=None):
        """
        Log an audit event with category and optional metadata.
        
        Args:
            category: Event category (SYSTEM, RED_TEAM, BLUE_TEAM, AUTH, etc.)
            message: Event description
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            extra_data: Optional dictionary with additional context
        """
        with self.lock:
            # Validate level
            if level not in self.LEVELS:
                level = "INFO"
                
            # Create log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'category': category,
                'level': level,
                'message': message,
                'extra_data': extra_data
            }
            
            # Add to memory buffer
            self.memory_buffer.append(log_entry)
            if len(self.memory_buffer) > self.max_memory_logs:
                self.memory_buffer.pop(0)
            
            # Log to file
            self.logger.log(
                self.LEVELS[level],
                message,
                extra={'category': category}
            )
            
            # Check for log rotation
            self.check_rotation()
            
    def log_security_event(self, event_type, details, severity="MEDIUM"):
        """
        Log security-specific events with standardized format.
        
        Args:
            event_type: Type of security event (SCAN, ALERT, INTRUSION, etc.)
            details: Event details
            severity: Event severity (LOW, MEDIUM, HIGH, CRITICAL)
        """
        message = f"Security Event: {event_type} - {details}"
        level_map = {
            'LOW': 'INFO',
            'MEDIUM': 'WARNING',
            'HIGH': 'ERROR',
            'CRITICAL': 'CRITICAL'
        }
        level = level_map.get(severity, 'WARNING')
        
        self.log_event("SECURITY", message, level, {'severity': severity, 'event_type': event_type})
        
    def log_user_action(self, action, user="system", result="success"):
        """
        Log user actions for accountability.
        
        Args:
            action: Description of action taken
            user: User identifier
            result: Action result (success, failure, error)
        """
        extra_data = {
            'user': user,
            'result': result
        }
        
        level = "INFO" if result == "success" else "WARNING"
        self.log_event("USER_ACTION", f"{user}: {action}", level, extra_data)
        
    def log_network_activity(self, activity_type, source, destination, details=None):
        """
        Log network-related activities.
        
        Args:
            activity_type: Type of network activity (SCAN, CONNECTION, etc.)
            source: Source address
            destination: Destination address
            details: Additional details
        """
        message = f"{activity_type}: {source} -> {destination}"
        extra_data = {
            'source': source,
            'destination': destination,
            'activity_type': activity_type
        }
        
        if details:
            extra_data.update(details)
            
        self.log_event("NETWORK", message, "INFO", extra_data)
        
    def log_system_change(self, change_type, description, component="unknown"):
        """
        Log system configuration or state changes.
        
        Args:
            change_type: Type of change (CONFIG, STATE, PERMISSION, etc.)
            description: Change description
            component: System component affected
        """
        extra_data = {
            'change_type': change_type,
            'component': component
        }
        
        self.log_event("SYSTEM_CHANGE", description, "WARNING", extra_data)
        
    def log_error(self, error_type, error_message, stack_trace=None):
        """
        Log application errors with optional stack trace.
        
        Args:
            error_type: Type/category of error
            error_message: Error description
            stack_trace: Optional stack trace string
        """
        extra_data = {
            'error_type': error_type
        }
        
        if stack_trace:
            extra_data['stack_trace'] = stack_trace
            
        self.log_event("ERROR", f"{error_type}: {error_message}", "ERROR", extra_data)
        
    def get_recent_logs(self, limit=100, category=None, level=None):
        """
        Retrieve recent logs from memory buffer.
        
        Args:
            limit: Maximum number of logs to return
            category: Filter by category (optional)
            level: Filter by level (optional)
            
        Returns:
            List of formatted log strings
        """
        with self.lock:
            logs = self.memory_buffer.copy()
            
            # Apply filters
            if category:
                logs = [log for log in logs if log['category'] == category]
            if level:
                logs = [log for log in logs if log['level'] == level]
            
            # Take most recent
            logs = logs[-limit:]
            
            # Format for display
            formatted_logs = []
            for log in logs:
                formatted = f"{log['timestamp']} | {log['level']:<8} | {log['category']:<12} | {log['message']}"
                formatted_logs.append(formatted)
                
            return formatted_logs
            
    def search_logs(self, search_term, category=None, start_date=None, end_date=None):
        """
        Search logs with filters.
        
        Args:
            search_term: Text to search for in messages
            category: Filter by category
            start_date: Start datetime for range
            end_date: End datetime for range
            
        Returns:
            List of matching log entries
        """
        with self.lock:
            results = []
            
            for log in self.memory_buffer:
                # Apply filters
                if search_term and search_term.lower() not in log['message'].lower():
                    continue
                    
                if category and log['category'] != category:
                    continue
                    
                if start_date and log['timestamp'] < start_date:
                    continue
                    
                if end_date and log['timestamp'] > end_date:
                    continue
                    
                results.append(log)
                
            return results
            
    def export_logs(self, output_file, format="json", start_date=None, end_date=None):
        """
        Export logs to file in specified format.
        
        Args:
            output_file: Output file path
            format: Export format (json, csv, txt)
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                logs = self.memory_buffer.copy()
                
                # Apply date filters
                if start_date:
                    logs = [log for log in logs if log['timestamp'] >= start_date]
                if end_date:
                    logs = [log for log in logs if log['timestamp'] <= end_date]
                
            if format == "json":
                with open(output_file, 'w') as f:
                    json.dump(logs, f, indent=2)
                    
            elif format == "csv":
                import csv
                with open(output_file, 'w', newline='') as f:
                    if logs:
                        writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                        writer.writeheader()
                        writer.writerows(logs)
                        
            elif format == "txt":
                with open(output_file, 'w') as f:
                    for log in logs:
                        line = f"{log['timestamp']} | {log['level']:<8} | {log['category']:<12} | {log['message']}\n"
                        f.write(line)
            else:
                return False
                
            self.log_event("SYSTEM", f"Logs exported to {output_file}", "INFO")
            return True
            
        except Exception as e:
            self.log_error("EXPORT", f"Failed to export logs: {str(e)}")
            return False
            
    def clear_logs(self):
        """Clear memory buffer and create new log file."""
        with self.lock:
            self.memory_buffer.clear()
            
            # Archive old log file
            if Path(self.log_file).exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"{self.log_file}.{timestamp}.archive"
                Path(self.log_file).rename(archive_name)
            
            # Reinitialize logger
            self.setup_logger()
            
    def check_rotation(self):
        """Check if log file needs rotation based on size."""
        try:
            if Path(self.log_file).exists():
                size = Path(self.log_file).stat().st_size
                
                if size >= self.max_size_bytes:
                    self.rotate_log_file()
        except Exception as e:
            pass  # Silently handle rotation errors
            
    def rotate_log_file(self):
        """Rotate log file when it exceeds size limit."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_name = f"{self.log_file}.{timestamp}"
        
        try:
            # Close current handlers
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)
            
            # Rename current log file
            if Path(self.log_file).exists():
                Path(self.log_file).rename(rotated_name)
            
            # Setup new logger
            self.setup_logger()
            
            self.log_event("SYSTEM", f"Log file rotated to {rotated_name}", "INFO")
            
        except Exception as e:
            print(f"Log rotation failed: {e}")
            
    def get_statistics(self):
        """
        Get logging statistics.
        
        Returns:
            Dictionary with log counts by category and level
        """
        with self.lock:
            stats = {
                'total_logs': len(self.memory_buffer),
                'by_category': {},
                'by_level': {}
            }
            
            for log in self.memory_buffer:
                # Count by category
                category = log['category']
                stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
                
                # Count by level
                level = log['level']
                stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
                
            return stats
            
    def get_log_file_size(self):
        """Get current log file size in MB."""
        try:
            if Path(self.log_file).exists():
                size_bytes = Path(self.log_file).stat().st_size
                return size_bytes / (1024 * 1024)
            return 0.0
        except:
            return 0.0