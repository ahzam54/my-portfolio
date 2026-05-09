from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = 'submissions.json'
ADMIN_PASSWORD = 'ahzan2026'

def load_submissions():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_submissions(submissions):
    with open(DATA_FILE, 'w') as f:
        json.dump(submissions, f, indent=2)

@app.route('/api/contact', methods=['POST'])
def submit_form():
    data = request.get_json()
    submission = {
        'id': len(load_submissions()) + 1,
        'name': data.get('name', ''),
        'email': data.get('email', ''),
        'message': data.get('message', ''),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ip': request.remote_addr,
        'read': False
    }
    submissions = load_submissions()
    submissions.insert(0, submission)
    save_submissions(submissions)
    return jsonify({'success': True, 'message': 'Submission received!'})

@app.route('/admin')
def admin_login():
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route('/admin/dashboard', methods=['POST'])
def admin_dashboard():
    password = request.form.get('password', '')
    if password != ADMIN_PASSWORD:
        return '<h2 style="color:red;text-align:center;margin-top:50px;">Invalid Password</h2><p style="text-align:center;"><a href="/admin">Go Back</a></p>'
    submissions = load_submissions()
    unread_count = sum(1 for s in submissions if not s.get('read', False))
    rows = ''
    for sub in submissions:
        status = 'New' if not sub.get('read', False) else 'Read'
        rows += '<tr style="border-bottom:1px solid #334155;" id="row-' + str(sub['id']) + '"><td style="padding:12px;">' + str(sub['id']) + '</td><td style="padding:12px;"><strong>' + sub['name'] + '</strong></td><td style="padding:12px;"><a href="mailto:' + sub['email'] + '" style="color:#818cf8;">' + sub['email'] + '</a></td><td style="padding:12px;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="' + sub['message'] + '">' + sub['message'] + '</td><td style="padding:12px;color:#94a3b8;font-size:12px;">' + sub['timestamp'] + '</td><td style="padding:12px;"><span class="status-badge">' + status + '</span></td><td style="padding:12px;"><button onclick="markRead(' + str(sub['id']) + ')" style="background:#6366f1;color:white;border:none;padding:6px 12px;border-radius:6px;cursor:pointer;font-size:12px;">Mark Read</button><button onclick="deleteSub(' + str(sub['id']) + ')" style="background:#ef4444;color:white;border:none;padding:6px 12px;border-radius:6px;cursor:pointer;font-size:12px;margin-left:4px;">Delete</button></td></tr>'
    return render_template_string(DASHBOARD_HTML.replace('{{ROWS}}', rows).replace('{{COUNT}}', str(len(submissions))).replace('{{UNREAD}}', str(unread_count)))

@app.route('/admin/mark-read/<int:id>', methods=['POST'])
def mark_read(id):
    submissions = load_submissions()
    for sub in submissions:
        if sub['id'] == id:
            sub['read'] = True
            break
    save_submissions(submissions)
    return jsonify({'success': True})

@app.route('/admin/delete/<int:id>', methods=['POST'])
def delete_sub(id):
    submissions = load_submissions()
    submissions = [s for s in submissions if s['id'] != id]
    save_submissions(submissions)
    return jsonify({'success': True})

ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login - Ahzan Imam Portfolio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #020617; color: white; font-family: 'Inter', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .login-box { background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(99, 102, 241, 0.2); padding: 40px; border-radius: 16px; width: 100%; max-width: 400px; backdrop-filter: blur(10px); }
        h2 { margin-bottom: 24px; text-align: center; }
        input { width: 100%; padding: 12px 16px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; color: white; margin-bottom: 16px; font-size: 16px; }
        input:focus { outline: none; border-color: #6366f1; }
        button { width: 100%; padding: 12px; background: linear-gradient(135deg, #6366f1, #a855f7); border: none; border-radius: 8px; color: white; font-weight: 600; cursor: pointer; font-size: 16px; }
        button:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Admin Access</h2>
        <form method="POST" action="/admin/dashboard">
            <input type="password" name="password" placeholder="Enter admin password" required autofocus>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - Ahzan Imam Portfolio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #020617; color: #e2e8f0; font-family: 'Inter', sans-serif; padding: 40px 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { margin-bottom: 8px; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }
        .stat-card { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(99, 102, 241, 0.15); padding: 20px; border-radius: 12px; }
        .stat-value { font-size: 32px; font-weight: 700; color: #6366f1; }
        .stat-label { color: #94a3b8; font-size: 14px; margin-top: 4px; }
        table { width: 100%; border-collapse: collapse; background: rgba(15, 23, 42, 0.6); border-radius: 12px; overflow: hidden; border: 1px solid rgba(99, 102, 241, 0.15); }
        th { background: rgba(99, 102, 241, 0.1); padding: 16px 12px; text-align: left; font-weight: 600; color: #818cf8; font-size: 14px; }
        td { padding: 12px; font-size: 14px; }
        tr:hover { background: rgba(99, 102, 241, 0.05); }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; background: rgba(34, 197, 94, 0.2); color: #22c55e; }
        .refresh-btn { position: fixed; bottom: 30px; right: 30px; background: linear-gradient(135deg, #6366f1, #a855f7); color: white; border: none; padding: 14px 24px; border-radius: 50px; cursor: pointer; font-weight: 600; box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3); }
        .refresh-btn:hover { transform: translateY(-2px); }
    </style>
</head>
<body>
    <div class="container">
        <h1>Contact Submissions</h1>
        <p style="color: #64748b; margin-bottom: 24px;">Manage and respond to portfolio inquiries</p>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{{COUNT}}</div>
                <div class="stat-label">Total Submissions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #22c55e;">{{UNREAD}}</div>
                <div class="stat-label">Unread Messages</div>
            </div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Message</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {{ROWS}}
            </tbody>
        </table>
    </div>
    <button class="refresh-btn" onclick="location.reload()">Refresh</button>
    <script>
        function markRead(id) {
            fetch('/admin/mark-read/' + id, { method: 'POST' })
                .then(r => r.json())
                .then(() => location.reload());
        }
        function deleteSub(id) {
            if (confirm('Delete this submission?')) {
                fetch('/admin/delete/' + id, { method: 'POST' })
                    .then(r => r.json())
                    .then(() => location.reload());
            }
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
