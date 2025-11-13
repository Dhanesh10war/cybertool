"""
Configuration Management - Application settings and constants
Centralized configuration for easy customization
"""

from pathlib import Path


class Config:
    """
    Application configuration class.
    Modify these values to customize application behavior.
    """
    
    # Application Metadata
    APP_NAME = "CyberTool"
    APP_VERSION = "1.0.0"
    ORGANIZATION = "SecOps"
    
    # Database Configuration
    DATABASE_PATH = "cybertool.db"
    DATABASE_MAX_SIZE_MB = 100  # Maximum database size before warning
    AUTO_BACKUP = True
    BACKUP_RETENTION_DAYS = 30
    
    # Logging Configuration
    LOG_FILE = "cybertool_audit.log"
    LOG_MAX_SIZE_MB = 10
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    CONSOLE_LOGGING = True
    
    # Red Team Configuration
    RED_TEAM_DEFAULT_TIMEOUT = 1.0  # seconds
    RED_TEAM_MAX_PORT_RANGE = 65535
    RED_TEAM_DEFAULT_START_PORT = 1
    RED_TEAM_DEFAULT_END_PORT = 1000
    RED_TEAM_REQUIRE_CONSENT = True  # Enforce authorization checkbox
    
    # Blue Team Configuration
    BLUE_TEAM_DEFAULT_INTERVAL = 5  # seconds
    BLUE_TEAM_MIN_INTERVAL = 1
    BLUE_TEAM_MAX_INTERVAL = 60
    
    # Alert Thresholds
    THRESHOLD_CPU_PERCENT = 80.0
    THRESHOLD_MEMORY_PERCENT = 85.0
    THRESHOLD_DISK_PERCENT = 90.0
    
    # Process Monitoring
    PROCESS_SCAN_INTERVAL = 10  # seconds
    SUSPICIOUS_KEYWORDS = [
        'hack', 'crack', 'exploit', 'backdoor', 'keylog',
        'trojan', 'malware', 'virus', 'rootkit'
    ]
    
    # UI Configuration
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    WINDOW_MIN_WIDTH = 1024
    WINDOW_MIN_HEIGHT = 768
    
    # Theme
    USE_DARK_THEME = True
    
    # Export Configuration
    EXPORT_FOLDER = "exports"
    EXPORT_FORMATS = ["json", "csv", "txt"]
    AUTO_TIMESTAMP_EXPORTS = True
    
    # Session Management
    SESSION_TIMEOUT_MINUTES = 30
    AUTO_CLEANUP_SESSIONS = True
    CLEANUP_AFTER_DAYS = 30
    
    # Memory Management
    MAX_MEMORY_LOGS = 1000  # Maximum logs kept in memory
    MAX_ALERTS_DISPLAY = 500  # Maximum alerts shown in table
    
    # Network Configuration (for future features)
    MAX_CONCURRENT_SCANS = 10
    DEFAULT_USER_AGENT = f"{APP_NAME}/{APP_VERSION}"
    
    # Security Settings
    ENABLE_AUDIT_LOG = True
    REQUIRE_AUTHORIZATION = True
    LOG_ALL_OPERATIONS = True
    MASK_SENSITIVE_DATA = True
    
    @classmethod
    def get_export_path(cls):
        """Get or create export directory path."""
        export_dir = Path(cls.EXPORT_FOLDER)
        export_dir.mkdir(exist_ok=True)
        return export_dir
        
    @classmethod
    def get_database_path(cls):
        """Get absolute database path."""
        return Path(cls.DATABASE_PATH).absolute()
        
    @classmethod
    def validate_config(cls):
        """
        Validate configuration values.
        Returns tuple (valid, errors).
        """
        errors = []
        
        # Validate port ranges
        if cls.RED_TEAM_DEFAULT_START_PORT < 1:
            errors.append("Start port must be >= 1")
        if cls.RED_TEAM_DEFAULT_END_PORT > cls.RED_TEAM_MAX_PORT_RANGE:
            errors.append(f"End port must be <= {cls.RED_TEAM_MAX_PORT_RANGE}")
            
        # Validate intervals
        if cls.BLUE_TEAM_DEFAULT_INTERVAL < cls.BLUE_TEAM_MIN_INTERVAL:
            errors.append(f"Default interval must be >= {cls.BLUE_TEAM_MIN_INTERVAL}")
            
        # Validate thresholds
        if not (0 < cls.THRESHOLD_CPU_PERCENT <= 100):
            errors.append("CPU threshold must be between 0 and 100")
            
        return (len(errors) == 0, errors)
        
    @classmethod
    def get_config_dict(cls):
        """
        Get configuration as dictionary.
        Useful for display or export.
        """
        return {
            'app_name': cls.APP_NAME,
            'version': cls.APP_VERSION,
            'database': cls.DATABASE_PATH,
            'log_file': cls.LOG_FILE,
            'theme': 'dark' if cls.USE_DARK_THEME else 'light',
            'red_team_timeout': cls.RED_TEAM_DEFAULT_TIMEOUT,
            'blue_team_interval': cls.BLUE_TEAM_DEFAULT_INTERVAL,
            'cpu_threshold': cls.THRESHOLD_CPU_PERCENT,
            'memory_threshold': cls.THRESHOLD_MEMORY_PERCENT,
            'disk_threshold': cls.THRESHOLD_DISK_PERCENT
        }


# Common service port mappings (extended list)
COMMON_PORTS = {
    # File Transfer
    20: "FTP-DATA",
    21: "FTP",
    22: "SSH/SFTP",
    69: "TFTP",
    
    # Email
    25: "SMTP",
    110: "POP3",
    143: "IMAP",
    465: "SMTPS",
    587: "SMTP-Submission",
    993: "IMAPS",
    995: "POP3S",
    
    # Web
    80: "HTTP",
    443: "HTTPS",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt",
    8000: "HTTP-Alt",
    
    # Remote Access
    23: "TELNET",
    3389: "RDP",
    5900: "VNC",
    5901: "VNC-1",
    22: "SSH",
    
    # Databases
    1433: "MSSQL",
    1521: "Oracle",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    27017: "MongoDB",
    27018: "MongoDB-Shard",
    
    # Directory Services
    389: "LDAP",
    636: "LDAPS",
    88: "Kerberos",
    
    # File Sharing
    445: "SMB",
    137: "NetBIOS-NS",
    138: "NetBIOS-DGM",
    139: "NetBIOS-SSN",
    2049: "NFS",
    
    # DNS
    53: "DNS",
    
    # Other Common Services
    161: "SNMP",
    162: "SNMP-Trap",
    179: "BGP",
    514: "Syslog",
    515: "LPD",
    631: "IPP",
    1194: "OpenVPN",
    1723: "PPTP",
    3000: "Node.js-Dev",
    5000: "Flask-Dev",
    9200: "Elasticsearch",
    9300: "Elasticsearch-Node",
    11211: "Memcached"
}

# Severity color codes (for UI)
SEVERITY_COLORS = {
    'LOW': '#4a9eff',      # Blue
    'MEDIUM': '#ffb84a',   # Orange
    'HIGH': '#ff6b6b',     # Red
    'CRITICAL': '#ff0000', # Bright Red
    'INFO': '#17a2b8'      # Cyan
}

# Log level colors
LOG_LEVEL_COLORS = {
    'DEBUG': '#888888',
    'INFO': '#4a9eff',
    'WARNING': '#ffb84a',
    'ERROR': '#ff6b6b',
    'CRITICAL': '#ff0000'
}