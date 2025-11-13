from flask import Flask, jsonify, request, render_template_string
import threading
import socket
from datetime import datetime
from database import DatabaseManager
from logger import AuditLogger

app = Flask(__name__)

db = DatabaseManager()
logger = AuditLogger()

# In-memory job store: job_id -> {status, results, session_id, started_at}
jobs = {}
jobs_lock = threading.Lock()
job_counter = 0

INDEX_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CyberTool - Web UI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-dark text-light">
    <div class="container py-4">
      <h1>CyberTool - Web Interface</h1>
      <p class="text-muted">Lightweight web UI for interacting with CyberTool core features.</p>

      <div class="row">
        <div class="col-md-6">
          <div class="card bg-secondary mb-3">
            <div class="card-body">
              <h5 class="card-title">Dashboard</h5>
              <pre id="stats">Loading...</pre>
              <button class="btn btn-sm btn-primary" onclick="loadStats()">Refresh</button>
            </div>
          </div>

          <div class="card bg-secondary mb-3">
            <div class="card-body">
              <h5 class="card-title">Recent Logs</h5>
              <pre id="logs" style="height:200px; overflow:auto;">Loading...</pre>
              <button class="btn btn-sm btn-primary" onclick="loadLogs()">Refresh</button>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="card bg-secondary mb-3">
            <div class="card-body">
              <h5 class="card-title">Start Port Scan</h5>
              <div class="mb-2">
                <label class="form-label">Target</label>
                <input id="target" class="form-control" value="localhost">
              </div>
              <div class="mb-2 d-flex gap-2">
                <input id="start_port" class="form-control" value="1">
                <input id="end_port" class="form-control" value="1024">
                <input id="timeout" class="form-control" value="1">
              </div>
              <button class="btn btn-success" onclick="startScan()">Start Scan</button>
              <div class="mt-3">
                <h6>Jobs</h6>
                <ul id="jobs" class="list-group"></ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

<script>
async function loadStats(){
  const res = await fetch('/api/stats');
  const data = await res.json();
  document.getElementById('stats').innerText = JSON.stringify(data, null, 2);
}

async function loadLogs(){
  const res = await fetch('/api/logs');
  const data = await res.json();
  document.getElementById('logs').innerText = data.logs.join('\n');
}

async function startScan(){
  const target = document.getElementById('target').value;
  const start_port = parseInt(document.getElementById('start_port').value);
  const end_port = parseInt(document.getElementById('end_port').value);
  const timeout = parseFloat(document.getElementById('timeout').value);

  const res = await fetch('/api/scan', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({target, start_port, end_port, timeout})
  });
  const job = await res.json();
  addJob(job.job_id);
}

function addJob(job_id){
  const jobsList = document.getElementById('jobs');
  const li = document.createElement('li');
  li.className = 'list-group-item bg-dark text-light';
  li.id = 'job-' + job_id;
  li.innerText = job_id + ': starting...';
  jobsList.prepend(li);
  pollJob(job_id);
}

async function pollJob(job_id){
  const el = document.getElementById('job-' + job_id);
  if(!el) return;
  const res = await fetch('/api/scan/' + job_id);
  const data = await res.json();
  if(data.status === 'running'){
    el.innerText = job_id + ': running (' + data.progress + '%)';
    setTimeout(()=>pollJob(job_id), 1000);
  } else {
    el.innerText = job_id + ': ' + data.status + ' - open_ports: ' + data.open_ports.join(', ');
  }
}

// Initial load
loadStats();
loadLogs();
</script>
  </body>
</html>
"""


SESSIONS_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CyberTool - Sessions</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-dark text-light">
    <div class="container py-4">
      <h1>Sessions</h1>
      <p class="text-muted">Recent sessions stored in the database.</p>
      <ul class="list-group bg-dark" id="sessions-list">
        {% for s in sessions %}
          <li class="list-group-item bg-secondary text-light">
            <a class="text-decoration-none text-light" href="/session/{{ s.id }}?token={{ token }}">Session {{ s.id }} - {{ s.session_type }} - {{ s.target }}</a>
            <div class="small text-muted">{{ s.start_time }} → {{ s.end_time or 'active' }}</div>
          </li>
        {% endfor %}
      </ul>
      <div class="mt-3">
        <a class="btn btn-sm btn-primary" href="/">Back to dashboard</a>
      </div>
    </div>
  </body>
</html>
"""


SESSION_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CyberTool - Session {{ session.id }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-dark text-light">
    <div class="container py-4">
      <h1>Session {{ session.id }}</h1>
      <p class="text-muted">Type: {{ session.session_type }} — Target: {{ session.target }}</p>

      <div class="card bg-secondary mb-3">
        <div class="card-body">
          <h5>Config</h5>
          <pre>{{ session.config }}</pre>
          <h5>Results</h5>
          <pre id="results">{{ results_text }}</pre>
          <a class="btn btn-sm btn-primary" href="/sessions?token={{ token }}">Back</a>
        </div>
      </div>
    </div>
  </body>
</html>
"""


def scan_worker(job_id, session_id, target, start_port, end_port, timeout):
    open_ports = []
    total = end_port - start_port + 1
    scanned = 0

    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            if result == 0:
                # store result
                db.store_scan_result(session_id, port, 'unknown', 'open')
                open_ports.append(port)
        except Exception as e:
            logger.log_event('RED_TEAM', f'Scan error {e}', 'ERROR')

        scanned += 1
        progress = int((scanned / total) * 100)
        with jobs_lock:
            jobs[job_id]['progress'] = progress

    with jobs_lock:
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['open_ports'] = open_ports
        jobs[job_id]['finished_at'] = datetime.now().isoformat()

    logger.log_event('RED_TEAM', f'Port scan completed: {target} - {len(open_ports)} open ports', 'INFO')


@app.route('/')
def index():
    return render_template_string(INDEX_HTML)


@app.route('/api/stats')
def api_stats():
    try:
        stats = db.get_session_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/logs')
def api_logs():
    logs = logger.get_recent_logs(limit=200)
    return jsonify({'logs': logs})


@app.route('/api/sessions')
def api_sessions():
    sessions = db.get_recent_sessions(limit=50)
    # Convert tuples to dicts
    keys = ['id', 'session_type', 'target', 'start_time', 'end_time', 'status']
    result = [dict(zip(keys, s)) for s in sessions]
    return jsonify({'sessions': result})


@app.route('/sessions')
def sessions_page():
    token = request.args.get('token', '')
    sessions = db.get_recent_sessions(limit=100)
    keys = ['id', 'session_type', 'target', 'start_time', 'end_time', 'status']
    result = [dict(zip(keys, s)) for s in sessions]
    return render_template_string(SESSIONS_HTML, sessions=result, token=token)


@app.route('/session/<int:session_id>')
def session_page(session_id):
    token = request.args.get('token', '')
    session = db.get_session_by_id(session_id)
    if not session:
        return ("Session not found", 404)

    results = db.get_session_results(session_id)
    # Format results into readable text
    lines = []
    for r in results:
        ts, port, service, status, details = r
        lines.append(f"{ts} | {port} | {service} | {status} | {details}")

    results_text = "\n".join(lines) if lines else "No results"
    return render_template_string(SESSION_HTML, session=session, results_text=results_text, token=token)


@app.route('/api/session/<int:session_id>')
def api_session(session_id):
    session = db.get_session_by_id(session_id)
    if not session:
        return jsonify({'error': 'not found'}), 404
    results = db.get_session_results(session_id)
    return jsonify({'session': session, 'results': results})


@app.route('/api/scan', methods=['POST'])
def api_start_scan():
    global job_counter
    body = request.get_json()
    target = body.get('target')
    start_port = int(body.get('start_port', 1))
    end_port = int(body.get('end_port', 1024))
    timeout = float(body.get('timeout', 1.0))

    if not target:
        return jsonify({'error': 'target required'}), 400

    # Create DB session
    session_id = db.create_session('red_team', target, {'start_port': start_port, 'end_port': end_port})

    with jobs_lock:
        job_counter += 1
        job_id = f'job-{job_counter}'
        jobs[job_id] = {
            'status': 'running',
            'progress': 0,
            'open_ports': [],
            'session_id': session_id,
            'started_at': datetime.now().isoformat()
        }

    # Start worker thread
    t = threading.Thread(target=scan_worker, args=(job_id, session_id, target, start_port, end_port, timeout), daemon=True)
    t.start()

    logger.log_event('RED_TEAM', f'Port scan started: {target} ports {start_port}-{end_port}', 'INFO')

    return jsonify({'job_id': job_id})


@app.route('/api/scan/<job_id>')
def api_scan_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            return jsonify({'error': 'job not found'}), 404
        return jsonify({
            'status': job['status'],
            'progress': job.get('progress', 0),
            'open_ports': job.get('open_ports', [])
        })


if __name__ == '__main__':
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
