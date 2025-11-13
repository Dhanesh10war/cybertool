# CyberTool

CyberTool is a comprehensive cybersecurity platform combining **offensive (Red Team)** and **defensive (Blue Team)** security operations in a unified interface. Built with Python, PyQt6, and Flask, it provides both a native desktop GUI and a lightweight web UI for security assessments and system monitoring.

## Features

### 🔴 Red Team Operations
- **Port Scanning**: Fast, multi-threaded port scanning with service identification
- **Service Detection**: Identify common services by port number
- **Non-Destructive Testing**: Safe reconnaissance without system impact
- **Session Management**: Store and review scan results
- **Export Results**: Save findings in JSON format for reporting

### 🔵 Blue Team Operations
- **Real-time System Monitoring**: CPU, memory, disk, and network metrics
- **Process Monitoring**: Track running processes and detect anomalies
- **Log Collection**: Centralized audit logging with categorization
- **Alert Generation**: Real-time alerts for threshold breaches
- **Anomaly Detection**: Identify suspicious process activity

### 📊 Cross-Platform Interfaces
- **Desktop GUI**: Native PyQt6 application with rich UI (port 5900 via VNC)
- **Web UI**: Lightweight Flask-based dashboard and REST API (port 5000)
- **Unified Database**: SQLite backend shared across both interfaces
- **Comprehensive Logging**: Full audit trail of all operations

## Quick Start

### Prerequisites
- Python 3.12+
- pip or conda package manager
- For desktop GUI: X11 server or VNC setup

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Dhanesh10war/cybertool.git
cd cybertool
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Optional: Install system libraries for GUI:**
```bash
# Ubuntu/Debian
sudo apt-get install -y libgl1 libxkbcommon0 libxcb-cursor0

# For VNC support (remote desktop)
sudo apt-get install -y xvfb x11vnc
```

## Usage

### Option 1: Web UI (Recommended for ease of use)

**Start the server:**
```bash
python web_ui.py
```

**Access in browser:**
- Local: http://localhost:5000
- Codespaces: Check Ports tab → port 5000 → Open in Browser

**Available pages:**
- `/` - Dashboard (stats, logs, scan form)
- `/sessions` - List of all sessions
- `/session/<id>` - Session details and results

**REST API Endpoints:**
```
GET  /api/stats                 # Dashboard statistics
GET  /api/logs                  # Recent audit logs
GET  /api/sessions              # All sessions (JSON)
GET  /api/session/<id>          # Session details (JSON)
POST /api/scan                  # Start new port scan
GET  /api/scan/<job_id>         # Scan job status/results
```

**Example: Start a scan via API**
```bash
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.1","start_port":1,"end_port":1024,"timeout":1.0}'
```

### Option 2: Desktop GUI (Full-featured UI)

**Start with Xvfb (virtual display):**
```bash
xvfb-run -s "-screen 0 1920x1080x24" python main.py
```

**Start with VNC (remote access):**
```bash
# Terminal 1: Start VNC server and GUI
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
x11vnc -display :99 -forever -nopw &
python main.py

# Terminal 2 (on your host): Connect with VNC viewer
vncviewer localhost:5900
# or: vnc://localhost:5900
```

**VNC Viewers:**
- macOS: [RealVNC Viewer](https://www.realvnc.com/download/viewer/)
- Windows: [RealVNC](https://www.realvnc.com/) or [UltraVNC](https://www.uvnc.com/)
- Linux: `vncviewer` or [Remmina](https://remmina.org/)
- Browser: [noVNC](https://novnc.com/)

**Features in Desktop GUI:**
- Tabbed interface: Dashboard, Red Team, Blue Team, Logs, Settings
- Real-time monitoring charts
- Interactive session management
- Database backup and optimization
- Settings and configuration panel

## Project Structure

```
cybertool/
├── main.py                 # Desktop GUI entry point (PyQt6)
├── web_ui.py              # Web UI entry point (Flask)
├── red_team.py            # Red team module (port scanning)
├── blue_team.py           # Blue team module (system monitoring)
├── database.py            # SQLite database manager
├── logger.py              # Audit logging system
├── config.py              # Configuration management
├── ui/
│   ├── __init__.py
│   └── styles.py          # PyQt6 dark theme styling
├── requirements.txt       # Python dependencies
├── setup.py              # Installation script
└── README.md             # This file
```

## Architecture

### Database Schema
- **sessions**: Red/Blue team sessions with metadata
- **scan_results**: Port scan findings linked to sessions
- **alerts**: Security alerts with severity and categorization
- **config**: Application configuration key-value pairs

### Threading Model
- **Port Scanner Thread**: Non-blocking background scanning
- **System Monitor Thread**: Continuous monitoring (5s intervals)
- **Process Monitor Thread**: Process tracking and anomaly detection
- **Flask Worker Threads**: API request handling

### Logging
All operations logged to `cybertool_audit.log` with categories:
- SYSTEM: Application lifecycle
- RED_TEAM: Scanning operations
- BLUE_TEAM: Monitoring activities
- USER_ACTION: Manual user interactions
- SECURITY: Security events and alerts

## Configuration

Edit `config.py` or use the Settings tab in the GUI:
```python
# Database location
DB_PATH = "cybertool.db"

# Logging
LOG_FILE = "cybertool_audit.log"
LOG_LEVEL = "INFO"

# GUI Theme
DARK_THEME = True

# Monitoring
CHECK_INTERVAL = 5  # seconds
ALERT_THRESHOLDS = {
    "cpu": 80,      # percent
    "memory": 85,   # percent
    "disk": 90      # percent
}
```

## API Examples

### Start a port scan
```bash
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "target": "example.com",
    "start_port": 1,
    "end_port": 1024,
    "timeout": 1.0
  }'
# Returns: {"job_id":"job-1"}
```

### Check scan status
```bash
curl http://localhost:5000/api/scan/job-1
# Returns: {"status":"running","progress":45,"open_ports":[]}
```

### Get dashboard stats
```bash
curl http://localhost:5000/api/stats
# Returns session counts, total alerts, last activity timestamp
```

### Get session details
```bash
curl http://localhost:5000/api/session/1
# Returns full session data and scan results
```

## Security Considerations

⚠️ **Authorization & Scope**
- Only scan systems you own or have explicit written permission to test
- Unauthorized scanning may be illegal and unethical
- Always obtain proper authorization before assessments

🔐 **Best Practices**
- Run in isolated environments during testing
- Keep audit logs for compliance and review
- Use strong authentication if deploying on shared networks
- Regularly back up your database (see Settings tab)

## Troubleshooting

### Web UI not responding
```bash
# Check if Flask is running
lsof -i :5000

# Restart the server
python web_ui.py
```

### Desktop GUI display errors
```bash
# Install missing X11 libraries
sudo apt-get install -y libgl1 libxkbcommon0 libxcb-cursor0

# Try offscreen mode (no display)
QT_QPA_PLATFORM=offscreen python main.py
```

### VNC connection issues
```bash
# Verify x11vnc is running
ps aux | grep x11vnc

# Check port 5900 availability
lsof -i :5900

# Try different VNC port
x11vnc -display :99 -rfbport 5901 -forever -nopw
```

### Database locked errors
```bash
# Close all connections and clear lock
rm -f cybertool.db-wal cybertool.db-shm

# Backup current database
cp cybertool.db cybertool.db.backup
```

## Development

### Running Tests
```bash
# Future: Unit tests
python -m pytest tests/

# Manual testing of API
curl http://localhost:5000/api/stats
```

### Code Style
```bash
# Format code
python -m black *.py ui/

# Lint
python -m pylint *.py
```

### Build Distribution
```bash
# Create standalone executable
pyinstaller --onefile main.py
```

## Performance

- **Port Scanning**: ~100-500 ports/second (depending on timeout)
- **System Monitoring**: Minimal CPU impact (~1-2%)
- **Database Size**: ~1MB per 10,000 scan results
- **Web UI Response**: <100ms for typical API calls

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review audit logs for error details

## Changelog

### v1.0.0 (Current)
- ✅ Red Team: Port scanning with service detection
- ✅ Blue Team: System monitoring and alerts
- ✅ Desktop GUI: Full PyQt6 interface
- ✅ Web UI: Flask REST API and dashboard
- ✅ Database: SQLite session and result storage
- ✅ Logging: Comprehensive audit trail
- ✅ VNC: Remote desktop access

### Future Roadmap
- [ ] Vulnerability database integration
- [ ] Advanced reporting and visualization
- [ ] Multi-user authentication and RBAC
- [ ] Cloud deployment support
- [ ] Mobile app integration
- [ ] Machine learning anomaly detection
