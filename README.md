# NorcsiAgent Dashboard

**Real-time dashboard for monitoring and controlling multiple AI agents simultaneously.**

Built with Flask + SocketIO + SQLite. My daughter wanted to *see* what AI agents are actually doing — so I asked Claude CLI to build it. It works.

---

## What it does

- **Live agent cards** — each agent gets its own card with real-time status
- **State icons** — 🧠 thinking · 🔍 tool call · ✅ done · ❌ error · 💤 idle
- **Typing animation** — the current action animates in, character by character
- **Event timeline** — full log per agent (thinking → tool_call → result)
- **Command panel** — send instructions to each agent independently, in parallel
- **WebSocket** — zero polling, instant updates

---

## Quickstart

```bash
git clone https://github.com/Tozsers/norcsiagent.git
cd norcsiagent
./start.sh
# open http://localhost:8700
```

Requires Python 3.8+

---

## Integrate into your agent

Copy `agent_client.py` to your project:

```python
from agent_client import AgentClient

agent = AgentClient("my-agent", "My Agent Name")

agent.thinking("Analyzing the task...")
agent.tool_call("web_search", query="latest AI news")
agent.result("Found 12 relevant articles.")
agent.error("API timeout, retrying...")
```

Each `.thinking()` / `.tool_call()` / `.result()` call also returns any pending commands sent from the dashboard — so you can interact with running agents in real time.

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/event` | Agent posts its current state |
| GET  | `/api/agents` | List all agents |
| GET  | `/api/agent/<id>/events` | Get event history |
| POST | `/api/agent/<id>/command` | Send command to agent |

### Event payload
```json
{
  "agent_id": "my-agent",
  "name": "My Agent",
  "type": "thinking",
  "message": "Processing...",
  "status": "running"
}
```

Event types: `thinking` · `tool_call` · `result` · `error` · `info`

---

## Stack

- **Backend**: Python, Flask, Flask-SocketIO, SQLite
- **Frontend**: Vanilla JS, Socket.IO client
- **No build step** — just Python and a browser

---

## Why

I run several AI agents locally (search agents, creative writers, schedulers). I wanted one place to see what they're all doing and give them instructions without touching the terminal. My daughter asked "can I see what the AI is thinking?" — so here we are.

---

MIT License
