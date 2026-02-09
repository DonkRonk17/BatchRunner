# BatchRunner - Integration Examples

Copy-paste-ready integration patterns with Team Brain tools.

---

## 🎯 INTEGRATION PHILOSOPHY

BatchRunner is designed to work seamlessly with other Team Brain tools. This document provides **working code examples** for common integration patterns.

---

## 📚 TABLE OF CONTENTS

1. [Pattern 1: BatchRunner + AgentHealth](#pattern-1-batchrunner--agenthealth)
2. [Pattern 2: BatchRunner + SynapseLink](#pattern-2-batchrunner--synapselink)
3. [Pattern 3: BatchRunner + SessionReplay](#pattern-3-batchrunner--sessionreplay)
4. [Pattern 4: BatchRunner + ErrorRecovery](#pattern-4-batchrunner--errorrecovery)
5. [Pattern 5: BatchRunner + TokenTracker](#pattern-5-batchrunner--tokentracker)
6. [Pattern 6: BatchRunner + MemoryBridge](#pattern-6-batchrunner--memorybridge)
7. [Pattern 7: BatchRunner + ConfigManager](#pattern-7-batchrunner--configmanager)
8. [Pattern 8: Multi-Tool Workflow](#pattern-8-multi-tool-workflow)
9. [Pattern 9: Full Team Brain Stack](#pattern-9-full-team-brain-stack)
10. [Pattern 10: BCH Integration (Future)](#pattern-10-bch-integration-future)

---

## Pattern 1: BatchRunner + AgentHealth

**Use Case:** Track pipeline execution health and performance

**Why:** Monitor how pipelines affect agent health, track execution metrics

**Code:**

```python
from agenthealth import AgentHealth
from batchrunner import BatchRunner
from pathlib import Path

def execute_with_health_tracking(config_file: Path, agent_name: str):
    """Execute batch with full health tracking."""
    health = AgentHealth()
    runner = BatchRunner(verbose=True)
    
    # Load configuration
    runner.load_from_file(config_file)
    
    # Start health session
    session_id = f"batch_{config_file.stem}_{int(time.time())}"
    health.start_session(agent_name, session_id=session_id)
    
    try:
        # Execute batch
        result = runner.run()
        
        # Log metrics
        health.log_metric(agent_name, "pipeline_duration", result["duration"])
        health.log_metric(agent_name, "commands_executed", result["executed"])
        health.log_metric(agent_name, "commands_successful", result["successful"])
        health.log_metric(agent_name, "commands_failed", result["failed"])
        
        # Heartbeat
        health.heartbeat(agent_name, status="active")
        
        # End session
        health.end_session(
            agent_name,
            session_id=session_id,
            status="success" if result["success"] else "failed"
        )
        
        return result
        
    except Exception as e:
        health.log_error(agent_name, str(e))
        health.end_session(agent_name, session_id=session_id, status="error")
        raise

# Usage
if __name__ == "__main__":
    result = execute_with_health_tracking(
        Path("build-pipeline.json"),
        "ATLAS"
    )
```

**Result:** Full health correlation with pipeline execution

---

## Pattern 2: BatchRunner + SynapseLink

**Use Case:** Notify Team Brain on pipeline completion/failure

**Why:** Keep team informed without manual status updates

**Code:**

```python
from synapselink import quick_send
from batchrunner import BatchRunner
from pathlib import Path

def execute_with_notifications(config_file: Path, notify_on_success: bool = True):
    """Execute batch with automatic team notifications."""
    runner = BatchRunner(verbose=True)
    runner.load_from_file(config_file)
    
    # Notify start
    quick_send(
        "TEAM",
        f"Pipeline Started: {config_file.stem}",
        f"Executing {len(runner.commands)} commands...",
        priority="NORMAL"
    )
    
    # Execute
    result = runner.run()
    
    # Notify completion/failure
    if result["success"]:
        if notify_on_success:
            quick_send(
                "TEAM",
                f"Pipeline Complete: {config_file.stem}",
                f"All {result['successful']} commands succeeded\\n"
                f"Duration: {result['duration']:.1f}s",
                priority="NORMAL"
            )
    else:
        quick_send(
            "FORGE,LOGAN",
            f"Pipeline Failed: {config_file.stem}",
            f"{result['failed']}/{result['executed']} commands failed\\n"
            f"Duration: {result['duration']:.1f}s\\n"
            f"Review required",
            priority="HIGH"
        )
    
    return result

# Usage
result = execute_with_notifications(Path("deploy-pipeline.json"))
```

**Result:** Team automatically notified of pipeline status

---

## Pattern 3: BatchRunner + SessionReplay

**Use Case:** Record pipeline execution for debugging and analysis

**Why:** Replay failed pipelines step-by-step to understand what went wrong

**Code:**

```python
from sessionreplay import SessionReplay
from batchrunner import BatchRunner
from pathlib import Path
import json

def execute_with_replay_recording(config_file: Path, agent_name: str):
    """Execute batch with full session replay recording."""
    replay = SessionReplay()
    runner = BatchRunner(verbose=True)
    
    # Load configuration
    runner.load_from_file(config_file)
    
    # Start replay session
    session_id = replay.start_session(
        agent_name,
        task=f"Execute pipeline: {config_file.stem}"
    )
    
    # Log input (configuration)
    replay.log_input(session_id, f"Loading configuration from {config_file}")
    replay.log_input(session_id, f"Commands: {len(runner.commands)}")
    
    # Execute batch
    result = runner.run()
    
    # Log each command result
    for cmd_result in runner.results:
        replay.log_output(
            session_id,
            f"[{'OK' if cmd_result.success else 'FAIL'}] {cmd_result.command}\\n"
            f"Exit Code: {cmd_result.exit_code}\\n"
            f"Duration: {cmd_result.duration:.2f}s"
        )
    
    # Log final report
    replay.log_output(session_id, runner.generate_report(format="json"))
    
    # End session
    replay.end_session(
        session_id,
        status="COMPLETED" if result["success"] else "FAILED"
    )
    
    print(f"Session recorded: {session_id}")
    print(f"Replay with: sessionreplay replay {session_id}")
    
    return result

# Usage
result = execute_with_replay_recording(
    Path("test-pipeline.json"),
    "ATLAS"
)
```

**Result:** Full pipeline execution recorded for replay and analysis

---

## Pattern 4: BatchRunner + ErrorRecovery

**Use Case:** Auto-retry entire pipelines on transient failures

**Why:** Recover from flaky network/service failures automatically

**Code:**

```python
from errorrecovery import with_recovery
from batchrunner import BatchRunner
from pathlib import Path

@with_recovery(max_attempts=3, strategy="retry", delay=5)
def run_critical_pipeline(config_file: Path):
    """Run pipeline with automatic retry on failure."""
    runner = BatchRunner(verbose=True)
    runner.load_from_file(config_file)
    
    result = runner.run()
    
    if not result["success"]:
        raise Exception(
            f"Pipeline failed: {result['failed']}/{result['executed']} commands failed"
        )
    
    return result

# Usage - automatically retries up to 3 times with 5s delay
try:
    result = run_critical_pipeline(Path("critical-deploy.json"))
    print(f"[OK] Pipeline succeeded after {result.get('attempt', 1)} attempt(s)")
except Exception as e:
    print(f"[FAIL] Pipeline failed after 3 attempts: {e}")
```

**Result:** Pipeline automatically retried on failures

---

## Pattern 5: BatchRunner + TokenTracker

**Use Case:** Track pipeline execution costs and duration

**Why:** Monitor resource usage and optimize workflows

**Code:**

```python
from tokentracker import TokenTracker
from batchrunner import BatchRunner
from pathlib import Path

def execute_with_cost_tracking(config_file: Path):
    """Execute batch with cost tracking."""
    tracker = TokenTracker()
    runner = BatchRunner(verbose=True)
    
    # Track start
    start_usage = tracker.get_usage()
    
    # Execute
    runner.load_from_file(config_file)
    result = runner.run()
    
    # Track end
    end_usage = tracker.get_usage()
    
    # Log operation (BatchRunner itself costs $0)
    tracker.log_operation(
        f"batchrunner_{config_file.stem}",
        duration=result["duration"],
        cost=0.0,
        metadata={
            "commands_executed": result["executed"],
            "commands_successful": result["successful"],
            "commands_failed": result["failed"]
        }
    )
    
    print(f"\\n[COST] BatchRunner execution: $0.00 (zero API costs)")
    print(f"[TIME] Duration: {result['duration']:.1f}s")
    print(f"[SAVED] Estimated manual time saved: {result['executed'] * 30}s")
    
    return result

# Usage
result = execute_with_cost_tracking(Path("build-pipeline.json"))
```

**Result:** Pipeline costs and duration tracked for analysis

---

## Pattern 6: BatchRunner + MemoryBridge

**Use Case:** Store pipeline execution history for future reference

**Why:** Maintain long-term record of pipeline executions

**Code:**

```python
from memorybridge import MemoryBridge
from batchrunner import BatchRunner
from pathlib import Path
import json

def execute_with_memory_storage(config_file: Path):
    """Execute batch and store results in memory bridge."""
    memory = MemoryBridge()
    runner = BatchRunner(verbose=True)
    
    # Load historical data
    history_key = f"batchrunner_history_{config_file.stem}"
    history = memory.get(history_key, default=[])
    
    # Execute
    runner.load_from_file(config_file)
    result = runner.run()
    
    # Store execution record
    record = {
        "timestamp": result.get("timestamp", datetime.now().isoformat()),
        "config_file": str(config_file),
        "success": result["success"],
        "duration": result["duration"],
        "commands_executed": result["executed"],
        "commands_successful": result["successful"],
        "commands_failed": result["failed"]
    }
    
    history.append(record)
    
    # Save to memory
    memory.set(history_key, history)
    memory.sync()
    
    print(f"\\n[MEMORY] Execution record saved")
    print(f"[HISTORY] Total executions: {len(history)}")
    
    return result

# Usage
result = execute_with_memory_storage(Path("deploy-pipeline.json"))
```

**Result:** Pipeline execution history persisted in memory bridge

---

## Pattern 7: BatchRunner + ConfigManager

**Use Case:** Centralize pipeline configurations

**Why:** Share configs across tools and agents

**Code:**

```python
from configmanager import ConfigManager
from batchrunner import BatchRunner
from pathlib import Path

def execute_from_shared_config(pipeline_name: str):
    """Execute batch using shared configuration."""
    config_mgr = ConfigManager()
    runner = BatchRunner(verbose=True)
    
    # Load pipeline config from ConfigManager
    pipeline_config = config_mgr.get(
        f"batchrunner.pipelines.{pipeline_name}",
        default=f"{pipeline_name}.json"
    )
    
    # Execute
    runner.load_from_file(Path(pipeline_config))
    result = runner.run()
    
    # Update last execution time in config
    config_mgr.set(
        f"batchrunner.last_execution.{pipeline_name}",
        {
            "timestamp": datetime.now().isoformat(),
            "success": result["success"],
            "duration": result["duration"]
        }
    )
    config_mgr.save()
    
    return result

# Usage
result = execute_from_shared_config("ci-pipeline")
```

**Result:** Centralized configuration management

---

## Pattern 8: Multi-Tool Workflow

**Use Case:** Complex workflow using multiple Team Brain tools

**Why:** Demonstrate real production scenario

**Code:**

```python
from agenthealth import AgentHealth
from sessionreplay import SessionReplay
from synapselink import quick_send
from tokentracker import TokenTracker
from batchrunner import BatchRunner
from pathlib import Path

def execute_full_workflow(config_file: Path, agent_name: str):
    """Execute batch with full Team Brain integration."""
    # Initialize all tools
    health = AgentHealth()
    replay = SessionReplay()
    tracker = TokenTracker()
    runner = BatchRunner(verbose=True)
    
    # Start tracking
    session_id = f"workflow_{int(time.time())}"
    health.start_session(agent_name, session_id=session_id)
    replay_id = replay.start_session(agent_name, task=f"Pipeline: {config_file.stem}")
    
    try:
        # Load and execute
        runner.load_from_file(config_file)
        replay.log_input(replay_id, f"Loaded {len(runner.commands)} commands")
        
        result = runner.run()
        
        # Log to all tools
        health.log_metric(agent_name, "pipeline_duration", result["duration"])
        replay.log_output(replay_id, runner.generate_report(format="json"))
        tracker.log_operation("pipeline", duration=result["duration"], cost=0.0)
        
        # Notify team
        if result["success"]:
            quick_send("TEAM", "Workflow Complete", f"{result['successful']} commands succeeded")
        else:
            quick_send("FORGE,LOGAN", "Workflow Failed", f"{result['failed']} failed", priority="HIGH")
        
        # End tracking
        health.end_session(agent_name, session_id=session_id, status="success")
        replay.end_session(replay_id, status="COMPLETED")
        
        return result
        
    except Exception as e:
        health.log_error(agent_name, str(e))
        replay.log_error(replay_id, str(e))
        health.end_session(agent_name, session_id=session_id, status="error")
        replay.end_session(replay_id, status="FAILED")
        raise

# Usage
result = execute_full_workflow(Path("production-deploy.json"), "ATLAS")
```

**Result:** Fully instrumented, coordinated workflow across all tools

---

## Pattern 9: Full Team Brain Stack

**Use Case:** Ultimate integration - all tools working together

**Why:** Production-grade agent operation with full observability

See [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) for complete documentation.

---

## Pattern 10: BCH Integration (Future)

**Use Case:** Execute pipelines via BCH commands

**Why:** Trigger batch execution from BCH interface

**Planned Code (v1.1+):**

```python
# Future BCH integration
@bch_command("batchrunner execute")
def execute_via_bch(pipeline_name: str, agent_name: str):
    """Execute pipeline via BCH command."""
    runner = BatchRunner(verbose=True)
    runner.load_from_file(Path(f"pipelines/{pipeline_name}.json"))
    
    result = runner.run()
    
    return {
        "success": result["success"],
        "message": f"{result['successful']}/{result['executed']} commands succeeded",
        "duration": result["duration"]
    }

# Usage in BCH:
# @batchrunner execute ci-pipeline ATLAS
```

---

## 📊 INTEGRATION PRIORITY

**Week 1 (Essential):**
1. ✅ AgentHealth - Health correlation
2. ✅ SynapseLink - Team notifications
3. ✅ SessionReplay - Debugging

**Week 2 (Productivity):**
4. ☐ ErrorRecovery - Retry logic
5. ☐ TokenTracker - Cost tracking
6. ☐ MemoryBridge - History storage

**Week 3 (Advanced):**
7. ☐ ConfigManager - Centralized config
8. ☐ Full Stack Integration
9. ☐ BCH Integration (future)

---

## 🔧 TROUBLESHOOTING INTEGRATIONS

**Import Errors:**

```python
# Ensure all tools are in Python path
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "OneDrive/Documents/AutoProjects"))

# Then import
from batchrunner import BatchRunner
```

**Version Conflicts:**

```bash
# Check versions
python batchrunner.py --version
python agenthealth.py --version

# Update if needed
cd AutoProjects/BatchRunner
git pull origin main
```

---

**Last Updated:** February 9, 2026  
**Maintained By:** ATLAS (Team Brain)
