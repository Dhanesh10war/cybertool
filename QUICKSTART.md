# CyberTool - Quick Start Guide

Get CyberTool running in **2 minutes**.

## 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

**Optional (for desktop GUI):**
```bash
sudo apt-get install -y libgl1 libxkbcommon0 libxcb-cursor0
```

## 2️⃣ Choose Your Interface

### Option A: Web UI (Easiest) 🌐

Start the server:
```bash
python web_ui.py
```

Open in browser:
- **Local**: http://localhost:5000
- **Codespaces**: Check Ports tab → click port 5000

✅ You're ready! Scan, view sessions, check logs.

### Option B: Desktop GUI (Full Features) 🖥️

Start with virtual display:
```bash
xvfb-run -s "-screen 0 1920x1080x24" python main.py
```

Or with VNC (remote access):
```bash
# Terminal 1
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
x11vnc -display :99 -forever -nopw &
python main.py

# Terminal 2 - Connect with VNC viewer
vncviewer localhost:5900
```

## 3️⃣ Run a Scan

### Via Web UI (Browser)
1. Open http://localhost:5000
2. Fill in Target: `localhost`
3. Click "Start Scan"
4. Watch progress in real-time

### Via API (Terminal)
```bash
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"target":"localhost","start_port":1,"end_port":100,"timeout":1.0}'
```

### Via Desktop GUI
1. Click "Red Team" tab
2. Check authorization box
3. Enter target and port range
4. Click "▶️ Start Scan"

## Common Commands

```bash
# Check if Flask is running
lsof -i :5000

# View audit logs
tail -f cybertool_audit.log

# Access database directly
sqlite3 cybertool.db

# Restart everything
pkill -f "python main.py"
python web_ui.py
```

## Features at a Glance

| Feature | Web UI | Desktop GUI |
|---------|--------|-------------|
| Port Scanning | ✅ | ✅ |
| Sessions List | ✅ | ✅ |
| System Monitoring | API only | ✅ Full UI |
| Real-time Logs | ✅ | ✅ |
| Export Results | ✅ | ✅ |

## Troubleshooting

**Port 5000 already in use?**
```bash
lsof -i :5000  # Find process
kill -9 <PID>  # Kill it
```

**Missing libraries?**
```bash
sudo apt-get install -y libgl1 libxkbcommon0 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0
```

**Database issues?**
```bash
rm cybertool.db cybertool.db-wal cybertool.db-shm
# Database will be recreated on next run
```

## Next Steps

- 📖 Read [README.md](README.md) for detailed documentation
- 🔍 Explore the REST API: http://localhost:5000/api/stats
- 📊 Check sessions: http://localhost:5000/sessions
- 🛠️ Configure settings in `config.py`

## Support

- Issues? Check `cybertool_audit.log`
- API docs? See README.md "API Examples" section
- Architecture? See README.md "Architecture" section

---

**That's it!** You're now running CyberTool. Happy securing! 🛡️
