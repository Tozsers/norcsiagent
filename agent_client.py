"""
SasAgent client — importáld bármely agentedbe.

Használat:
    from agent_client import AgentClient

    agent = AgentClient("my-agent-id", "Kereső Agent", base_url="http://localhost:8700")
    agent.thinking("Elemzem a feladatot...")
    agent.tool_call("web_search", query="claude code")
    agent.result("Megtaláltam 5 releváns forrást.")

Az agent automatikusan lekéri a pending parancsokat minden eventnél.
Ha van pending parancs, visszaadja listaként.
"""

import requests
import socket

SASAGENT_URL = "http://localhost:8700"

class AgentClient:
    def __init__(self, agent_id: str, name: str, base_url: str = SASAGENT_URL):
        self.agent_id = agent_id
        self.name = name
        self.base_url = base_url.rstrip('/')

    def _send(self, event_type: str, message: str, status: str = "running", meta: dict = None):
        try:
            r = requests.post(f"{self.base_url}/api/event", json={
                "agent_id": self.agent_id,
                "name": self.name,
                "type": event_type,
                "message": message,
                "status": status,
                "meta": meta or {}
            }, timeout=3)
            data = r.json()
            return data.get("commands", [])
        except Exception:
            return []

    def thinking(self, message: str):
        return self._send("thinking", message)

    def tool_call(self, tool: str, **kwargs):
        msg = f"{tool}({', '.join(f'{k}={v}' for k,v in kwargs.items())})"
        return self._send("tool_call", msg, meta={"tool": tool, **kwargs})

    def result(self, message: str):
        return self._send("result", message, status="done")

    def error(self, message: str):
        return self._send("error", message, status="error")

    def info(self, message: str):
        return self._send("info", message)

    def idle(self):
        return self._send("info", "Várakozás...", status="idle")

    def approval_needed(self, message: str):
        """Jóváhagyási kérés — megjelenik a dashboardon Approve/Reject gombokkal."""
        return self._send("approval", message, status="approval_needed")
