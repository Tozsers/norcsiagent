import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import database as db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sasagent-secret'
CORS(app)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')

db.init_db()

# ─────────────────────────────────────────────
# REST API — agenteknek
# ─────────────────────────────────────────────

@app.route('/api/event', methods=['POST'])
def receive_event():
    """Agent ide POST-ol állapotot."""
    data = request.json
    agent_id = data.get('agent_id', 'unknown')
    name = data.get('name', agent_id)
    event_type = data.get('type', 'info')      # thinking | tool_call | result | error | info
    message = data.get('message', '')
    meta = data.get('meta', {})
    status = data.get('status', 'running')

    db.upsert_agent(agent_id, name, status, meta)
    db.add_event(agent_id, event_type, message, meta)

    payload = {
        'agent_id': agent_id,
        'name': name,
        'type': event_type,
        'message': message,
        'status': status,
        'meta': meta
    }
    socketio.emit('agent_event', payload)

    # Visszaadjuk a pending parancsokat
    commands = db.get_pending_commands(agent_id)
    return jsonify({'ok': True, 'commands': commands})

@app.route('/api/agents', methods=['GET'])
def list_agents():
    return jsonify(db.get_agents())

@app.route('/api/agent/<agent_id>/events', methods=['GET'])
def agent_events(agent_id):
    return jsonify(db.get_agent_events(agent_id))

@app.route('/api/agent/<agent_id>/command', methods=['POST'])
def send_command(agent_id):
    """Dashboard-ból parancs küldése agentnek."""
    command = request.json.get('command', '')
    if not command:
        return jsonify({'error': 'empty command'}), 400
    cmd_id = db.add_command(agent_id, command)
    socketio.emit('command_queued', {'agent_id': agent_id, 'command': command, 'id': cmd_id})
    return jsonify({'ok': True, 'id': cmd_id})

@app.route('/api/command/<int:cmd_id>/done', methods=['POST'])
def command_done(cmd_id):
    db.mark_command_done(cmd_id)
    return jsonify({'ok': True})

# ─────────────────────────────────────────────
# Frontend
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print("NorcsiAgent fut: http://localhost:8700")
    socketio.run(app, host='0.0.0.0', port=8700, debug=False)
