"""
Database Manager - SQLite session and data storage
Handles all database operations for the application
"""

import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
import threading


class DatabaseManager:
    """
    Manages SQLite database for storing sessions, scan results,
    alerts, and application data. Thread-safe implementation.
    """
    
    def __init__(self, db_path="cybertool.db"):
        """Initialize database connection and create tables."""
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
        
    def init_database(self):
        """Create database tables if they don't exist."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    config TEXT,
                    results TEXT,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Scan results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    port INTEGER,
                    service TEXT,
                    status TEXT,
                    details TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    message TEXT NOT NULL,
                    acknowledged INTEGER DEFAULT 0
                )
            ''')
            
            # Configuration table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
    def create_session(self, session_type, target, config=None):
        """
        Create a new session record.
        Returns session ID.
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_time = datetime.now().isoformat()
            config_json = json.dumps(config) if config else None
            
            cursor.execute('''
                INSERT INTO sessions (session_type, target, start_time, config)
                VALUES (?, ?, ?, ?)
            ''', (session_type, target, start_time, config_json))
            
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return session_id
            
    def update_session(self, session_id, results):
        """Update session with results and end time."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            end_time = datetime.now().isoformat()
            results_json = json.dumps(results)
            
            cursor.execute('''
                UPDATE sessions
                SET end_time = ?, results = ?, status = 'completed'
                WHERE id = ?
            ''', (end_time, results_json, session_id))
            
            conn.commit()
            conn.close()
            
    def store_scan_result(self, session_id, port, service, status, details=None):
        """Store individual scan result."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            details_json = json.dumps(details) if details else None
            
            cursor.execute('''
                INSERT INTO scan_results 
                (session_id, timestamp, port, service, status, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, timestamp, port, service, status, details_json))
            
            conn.commit()
            conn.close()
            
    def store_alert(self, severity, category, message):
        """Store security alert."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO alerts (timestamp, severity, category, message)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, severity, category, message))
            
            conn.commit()
            conn.close()
            
    def get_session_statistics(self):
        """
        Get aggregate statistics for dashboard.
        Returns dictionary with session counts and activity.
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total sessions
            cursor.execute('SELECT COUNT(*) FROM sessions')
            total_sessions = cursor.fetchone()[0]
            
            # Red team sessions
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE session_type = 'red_team'")
            red_team_sessions = cursor.fetchone()[0]
            
            # Blue team sessions
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE session_type = 'blue_team'")
            blue_team_sessions = cursor.fetchone()[0]
            
            # Total alerts
            cursor.execute('SELECT COUNT(*) FROM alerts')
            total_alerts = cursor.fetchone()[0]
            
            # Last activity
            cursor.execute('SELECT MAX(start_time) FROM sessions')
            last_activity = cursor.fetchone()[0] or "No activity yet"
            
            conn.close()
            
            return {
                'total_sessions': total_sessions,
                'red_team_sessions': red_team_sessions,
                'blue_team_sessions': blue_team_sessions,
                'total_alerts': total_alerts,
                'last_activity': last_activity
            }
            
    def get_recent_sessions(self, limit=10):
        """Get most recent sessions."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, session_type, target, start_time, end_time, status
                FROM sessions
                ORDER BY start_time DESC
                LIMIT ?
            ''', (limit,))
            
            sessions = cursor.fetchall()
            conn.close()
            
            return sessions
            
    def get_recent_alerts(self, limit=50):
        """Get most recent alerts."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, severity, category, message
                FROM alerts
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            alerts = cursor.fetchall()
            conn.close()
            
            return alerts
            
    def get_session_results(self, session_id):
        """Get all scan results for a session."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, port, service, status, details
                FROM scan_results
                WHERE session_id = ?
                ORDER BY timestamp
            ''', (session_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return results

    def get_session_by_id(self, session_id):
        """Get a single session row by id as a dict, or None if not found."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM sessions WHERE id = ?
            ''', (session_id,))

            row = cursor.fetchone()
            conn.close()

            return dict(row) if row else None
            
    def search_sessions(self, session_type=None, target=None, start_date=None, end_date=None):
        """
        Search sessions with optional filters.
        Returns list of matching sessions.
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM sessions WHERE 1=1'
            params = []
            
            if session_type:
                query += ' AND session_type = ?'
                params.append(session_type)
                
            if target:
                query += ' AND target LIKE ?'
                params.append(f'%{target}%')
                
            if start_date:
                query += ' AND start_time >= ?'
                params.append(start_date)
                
            if end_date:
                query += ' AND start_time <= ?'
                params.append(end_date)
                
            query += ' ORDER BY start_time DESC'
            
            cursor.execute(query, params)
            sessions = cursor.fetchall()
            conn.close()
            
            return sessions
            
    def backup_database(self):
        """
        Create backup of database file.
        Returns True if successful, False otherwise.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"cybertool_backup_{timestamp}.db"
            
            with self.lock:
                shutil.copy2(self.db_path, backup_path)
                
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
            
    def optimize_database(self):
        """Run VACUUM to optimize database."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute('VACUUM')
            conn.close()
            
    def delete_old_sessions(self, days=30):
        """
        Delete sessions older than specified days.
        Returns number of sessions deleted.
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now().replace(day=datetime.now().day - days).isoformat()
            
            # Delete old scan results first (foreign key constraint)
            cursor.execute('''
                DELETE FROM scan_results
                WHERE session_id IN (
                    SELECT id FROM sessions WHERE start_time < ?
                )
            ''', (cutoff_date,))
            
            # Delete old sessions
            cursor.execute('DELETE FROM sessions WHERE start_time < ?', (cutoff_date,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            return deleted_count
            
    def get_config(self, key, default=None):
        """Get configuration value."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else default
            
    def set_config(self, key, value):
        """Set configuration value."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updated_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO config (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, str(value), updated_at))
            
            conn.commit()
            conn.close()
            
    def export_to_json(self, output_file):
        """
        Export entire database to JSON file.
        Returns True if successful.
        """
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                export_data = {}
                
                # Export all tables
                for table in ['sessions', 'scan_results', 'alerts', 'config']:
                    cursor.execute(f'SELECT * FROM {table}')
                    rows = cursor.fetchall()
                    export_data[table] = [dict(row) for row in rows]
                
                conn.close()
                
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
            
    def get_statistics_summary(self):
        """
        Get comprehensive statistics summary.
        Returns dictionary with detailed metrics.
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Session statistics
            cursor.execute('SELECT COUNT(*), MIN(start_time), MAX(start_time) FROM sessions')
            total, first, last = cursor.fetchone()
            stats['total_sessions'] = total
            stats['first_session'] = first
            stats['last_session'] = last
            
            # Scan statistics
            cursor.execute('SELECT COUNT(*) FROM scan_results WHERE status = "open"')
            stats['open_ports_found'] = cursor.fetchone()[0]
            
            # Alert statistics by severity
            cursor.execute('''
                SELECT severity, COUNT(*) 
                FROM alerts 
                GROUP BY severity
            ''')
            stats['alerts_by_severity'] = dict(cursor.fetchall())
            
            # Active sessions
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'active'")
            stats['active_sessions'] = cursor.fetchone()[0]
            
            conn.close()
            
            return stats
            
    def close(self):
        """Close database connection and cleanup."""
        # SQLite connections are per-thread, so we just need to ensure
        # no active operations are running
        with self.lock:
            pass  # Lock ensures all operations complete