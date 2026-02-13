# BatchRunner - Integration Examples

## 🎯 INTEGRATION PHILOSOPHY

BatchRunner is designed to work seamlessly with other Team Brain tools. This document provides **copy-paste-ready code examples** for common integration patterns.

---

## 📚 TABLE OF CONTENTS

1. [Pattern 1: BatchRunner + AgentHealth](#pattern-1-batchrunner--agenthealth)
2. [Pattern 2: BatchRunner + SynapseLink](#pattern-2-batchrunner--synapselink)
3. [Pattern 3: BatchRunner + MemoryBridge](#pattern-3-batchrunner--memorybridge)
4. [Pattern 4: BatchRunner + TokenTracker](#pattern-4-batchrunner--tokentracker)
5. [Pattern 5: BatchRunner + LogHunter](#pattern-5-batchrunner--loghunter)
6. [Pattern 6: Multi-Tool Workflow](#pattern-6-multi-tool-workflow)

---

## Pattern 1: BatchRunner + AgentHealth

**Use Case:** Track batch job execution as part of agent health monitoring

**Why:** Correlate batch job health with overall agent performance

**Code:**

```python
from agenthealth import AgentHealth
from batchrunner import BatchRunner
from pathlib import Path
from datetime import datetime

# Initialize both tools
health = AgentHealth()
session_id = health.start_session("ATLAS", task="Tool build pipeline")

# Configure batch runner with session-specific logging
log_file = Path(f"batch-{session_id}-{datetime.now():%Y%m%d}.log")

commands = [
    "python -m pytest tests/",
    "python -m black . --check",
    "python setup.py sdist bdist_wheel"
]

runner = BatchRunner(
    commands,
    mode="sequential",
    max_retries=1,
    log_file=log_file,
    verbose=True
)

try:
    # Execute batch
    health.heartbeat("ATLAS", status="processing", task="Running build pipeline")
    results, summary = runner.run()
    
    # Log success/failure
    if summary["failed"] == 0:
        health.end_session("ATLAS", session_id, status="success", 
                         metrics={"commands": summary["total_commands"],
                                 "duration_ms": summary["total_duration_ms"]})
    else:
        health.end_session("ATLAS", session_id, status="failed",
                         error=f"{summary['failed']} commands failed")
        
except Exception as e:
    health.log_error("ATLAS", str(e))
    health.end_session("ATLAS", session_id, status="error")
```

**Result:** Correlated batch execution data in AgentHealth metrics

---

## Pattern 2: BatchRunner + SynapseLink

**Use Case:** Notify Team Brain when batch jobs complete or fail

**Why:** Keep team informed of important automation results

**Code:**

```python
from synapselink import quick_send
from batchrunner import BatchRunner

commands = [
    "python deploy.py --env production",
    "python verify.py --url https://api.example.com",
    "python smoke-tests.py"
]

runner = BatchRunner(
    commands,
    mode="sequential",
    max_retries=2,
    verbose=False
)

results, summary = runner.run()

# Notify based on results
if summary["failed"] == 0:
    quick_send(
        "TEAM",
        "[OK] Deployment Complete",
        f"All {summary['total_commands']} steps successful\n"
        f"Duration: {summary['total_duration_ms']:.1f}ms\n"
        f"Success rate: 100%",
        priority="NORMAL"
    )
else:
    quick_send(
        "FORGE,LOGAN",
        "[X] Deployment Failed - Action Required",
        f"Failed: {summary['failed']}/{summary['total_commands']} commands\n"
        f"Success rate: {summary['success_rate']:.1f}%\n"
        f"Check logs for details",
        priority="HIGH"
    )
```

**Result:** Team gets automatic notifications for critical batch jobs

---

## Pattern 3: BatchRunner + MemoryBridge

**Use Case:** Persist batch execution history to Memory Core

**Why:** Long-term tracking of batch job patterns and performance

**Code:**

```python
from memorybridge import MemoryBridge
from batchrunner import BatchRunner
from datetime import datetime

memory = MemoryBridge()

# Load historical data
batch_history = memory.get("batchrunner_history", [])

# Run batch
commands = ["python task1.py", "python task2.py", "python task3.py"]
runner = BatchRunner(commands, mode="parallel")
results, summary = runner.run()

# Append to history
history_entry = {
    "timestamp": datetime.now().isoformat(),
    "commands": len(commands),
    "success_rate": summary["success_rate"],
    "duration_ms": summary["total_duration_ms"],
    "mode": summary["mode"],
    "failed": summary["failed"]
}

batch_history.append(history_entry)

# Save to memory
memory.set("batchrunner_history", batch_history)
memory.sync()

print(f"Total batch jobs in history: {len(batch_history)}")
```

**Result:** Complete historical record of all batch executions

---

## Pattern 4: BatchRunner + TokenTracker

**Use Case:** Track API token usage when batch processing involves API calls

**Why:** Monitor costs and optimize API-heavy workflows

**Code:**

```python
from tokentracker import TokenTracker
from batchrunner import BatchRunner

tracker = TokenTracker()
session_id = tracker.start_session("batch_api_processing")

# API-heavy commands
api_commands = [
    "python api_call.py --endpoint /users",
    "python api_call.py --endpoint /orders",
    "python api_call.py --endpoint /products"
]

runner = BatchRunner(api_commands, mode="sequential")
results, summary = runner.run()

# Estimate token usage (if using AI APIs)
# Rough estimate: 500 tokens per API call
estimated_tokens = len(api_commands) * 500

tracker.log_usage(
    session_id,
    estimated_tokens,
    source="BatchRunner",
    metadata={
        "commands": summary["total_commands"],
        "duration_ms": summary["total_duration_ms"]
    }
)

tracker.end_session(session_id)
```

**Result:** Token usage tracked alongside batch execution metrics

---

## Pattern 5: BatchRunner + LogHunter

**Use Case:** Automatically analyze logs when batch jobs fail

**Why:** Quick debugging of failed batch operations

**Code:**

```python
from batchrunner import BatchRunner
import subprocess
from pathlib import Path

log_file = Path("batch-deployment.log")

commands = [
    "python build.py",
    "python test.py",
    "python deploy.py"
]

runner = BatchRunner(
    commands,
    mode="sequential",
    max_retries=1,
    log_file=log_file
)

results, summary = runner.run()

# If failures occurred, analyze logs
if summary["failed"] > 0:
    print(f"\n[!] {summary['failed']} commands failed - analyzing logs...\n")
    
    # Use LogHunter to find errors
    subprocess.run([
        "python",
        "C:/Users/logan/OneDrive/Documents/AutoProjects/LogHunter/loghunter.py",
        str(log_file),
        "--pattern", "ERROR|FAILED|Exception"
    ])
    
    print("\n[!] Review log analysis above for debugging")
```

**Result:** Automatic error analysis when batch jobs fail

---

## Pattern 6: Multi-Tool Workflow

**Use Case:** Complete production workflow using multiple Team Brain tools

**Why:** Demonstrate real end-to-end integration

**Code:**

```python
from agenthealth import AgentHealth
from synapselink import quick_send
from memorybridge import MemoryBridge
from batchrunner import BatchRunner
from pathlib import Path
from datetime import datetime

# Initialize all tools
health = AgentHealth()
memory = MemoryBridge()
session_id = health.start_session("ATLAS", task="Production deployment")

# Deployment pipeline commands
deployment_commands = [
    "echo 'Step 1: Building...'",
    "python setup.py sdist bdist_wheel",
    "echo 'Step 2: Testing...'",
    "python -m pytest tests/",
    "echo 'Step 3: Deploying...'",
    "twine upload dist/*"
]

# Configure batch runner
log_file = Path(f"deploy-{datetime.now():%Y%m%d-%H%M%S}.log")
runner = BatchRunner(
    deployment_commands,
    mode="sequential",
    max_retries=1,
    timeout_sec=300,
    log_file=log_file
)

try:
    # Update health status
    health.heartbeat("ATLAS", status="deploying")
    
    # Execute deployment
    results, summary = runner.run()
    
    # Store result in memory
    deploy_history = memory.get("deployment_history", [])
    deploy_history.append({
        "timestamp": datetime.now().isoformat(),
        "success": summary["failed"] == 0,
        "duration_ms": summary["total_duration_ms"],
        "log_file": str(log_file)
    })
    memory.set("deployment_history", deploy_history)
    memory.sync()
    
    # End health session
    if summary["failed"] == 0:
        health.end_session("ATLAS", session_id, status="success")
        
        # Notify team of success
        quick_send(
            "TEAM",
            "[OK] Production Deployment Complete",
            f"All {summary['total_commands']} steps successful\n"
            f"Duration: {summary['total_duration_ms']/1000:.1f}s\n"
            f"Log: {log_file}",
            priority="NORMAL"
        )
    else:
        health.end_session("ATLAS", session_id, status="failed")
        
        # Alert team of failure
        quick_send(
            "FORGE,LOGAN",
            "[X] Production Deployment FAILED",
            f"Failed steps: {summary['failed']}/{summary['total_commands']}\n"
            f"Success rate: {summary['success_rate']:.1f}%\n"
            f"URGENT: Review log at {log_file}",
            priority="CRITICAL"
        )
        
except Exception as e:
    health.log_error("ATLAS", str(e))
    health.end_session("ATLAS", session_id, status="error")
    
    quick_send(
        "FORGE,LOGAN",
        "[X] Deployment Error",
        f"Exception: {str(e)}",
        priority="CRITICAL"
    )

print(f"\n[OK] Deployment workflow complete - check {log_file} for details")
```

**Result:** Fully instrumented production deployment with:
- Health tracking (AgentHealth)
- Team notifications (SynapseLink)
- Historical records (MemoryBridge)
- Complete audit trail (BatchRunner logs)

---

## 📊 RECOMMENDED INTEGRATION PRIORITY

**Week 1 (Essential):**
1. ✓ AgentHealth - Health correlation
2. ✓ SynapseLink - Team notifications

**Week 2 (Productivity):**
3. ☐ MemoryBridge - Historical tracking
4. ☐ LogHunter - Error analysis

**Week 3 (Advanced):**
5. ☐ TokenTracker - Cost tracking (for API workflows)
6. ☐ Multi-tool workflows - Complete integration

---

**Last Updated:** February 13, 2026  
**Maintained By:** ATLAS (Team Brain)

*Built with precision. Deployed with pride.* ⚛️
