#!/usr/bin/env python3
"""Query local Codex skill discovery; never start a model turn or subagent."""
import json
from pathlib import Path
import selectors
import subprocess
import sys
import time

cwd = str(Path(sys.argv[1]).resolve())
proc = subprocess.Popen(["codex", "app-server", "--stdio"], stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
selector = selectors.DefaultSelector()
selector.register(proc.stdout, selectors.EVENT_READ)

def send(message):
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()

def response(request_id):
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if not selector.select(timeout=1):
            continue
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("Codex app-server exited before discovery response")
        message = json.loads(line)
        if message.get("id") == request_id:
            if "error" in message:
                raise RuntimeError(str(message["error"]))
            return message["result"]
    raise TimeoutError("Codex discovery response timed out")

try:
    send({"id": 1, "method": "initialize", "params": {
        "clientInfo": {"name": "sailfish-skill-discovery-probe", "version": "1.0"}}})
    response(1)
    send({"method": "initialized"})
    send({"id": 2, "method": "skills/list", "params": {"cwds": [cwd], "forceReload": True}})
    result = response(2)
    entries = []
    for entry in result["data"]:
        skills = [{key: skill[key] for key in ("name", "path", "scope", "enabled")}
                  for skill in entry["skills"] if skill["name"].startswith("speckit-")]
        errors = [error for error in entry["errors"] if error["path"].startswith(cwd)]
        entries.append({"cwd": entry["cwd"], "skills": skills, "errors": errors})
    print(json.dumps({"entries": entries, "model_turns_started": 0}, indent=2))
    expected = {"speckit-" + name for name in (
        "constitution", "specify", "clarify", "plan", "tasks", "analyze", "checklist",
        "implement", "converge", "taskstoissues")}
    actual = {skill["name"] for entry in entries for skill in entry["skills"]
              if skill["enabled"] and skill["scope"] == "repo"}
    if expected != actual or any(entry["errors"] for entry in entries):
        raise RuntimeError("Unexpected local Spec Kit skill discovery result")
finally:
    selector.close()
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
