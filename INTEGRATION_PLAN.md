# BatchRunner - Integration Plan

Complete integration guide for Team Brain agents and existing tools.

---

## 🎯 INTEGRATION GOALS

This document outlines how BatchRunner integrates with:
1. Team Brain agents (Forge, Atlas, Clio, Nexus, Bolt)
2. Existing Team Brain tools (35+ tools)
3. BCH (Beacon Command Hub) - Future potential
4. Logan's workflows

---

## 📦 BCH INTEGRATION

### Overview

**Status:** Not currently integrated with BCH

**Reason:** BatchRunner is a standalone command orchestration tool. BCH integration would require:
- WebSocket API for command status updates
- Real-time execution monitoring
- Agent-triggered batch execution

**Future Potential:**
- `@batchrunner execute pipeline.json` command
- Real-time progress updates in BCH
- Integration with BCH task system

**Estimated Effort:** Medium (2-3 days)

---

## 🤖 AI AGENT INTEGRATION

### Integration Matrix

| Agent | Use Case | Integration Method | Priority |
|-------|----------|-------------------|----------|
| **Forge** | Orchestrate multi-tool workflows | CLI/Python | HIGH |
| **Atlas** | Automate tool build pipelines | CLI/Python | HIGH |
| **Clio** | Linux environment automation | CLI | MEDIUM |
| **Nexus** | Cross-platform deployment | CLI/Python | MEDIUM |
| **Bolt** | Cost-free batch operations | CLI | LOW |

### Agent-Specific Workflows

#### Forge (Orchestrator / Reviewer)

**Primary Use Case:** Orchestrate complex multi-step workflows involving multiple tools

**Integration Steps:**
1. Create batch configurations for common workflows
2. Use Python API for dynamic batch generation
3. Integrate with SynapseLink for team notifications
4. Track execution with AgentHealth

**Example Workflow:**

```python
from batchrunner import BatchRunner
from synapselink import quick_send

def orchestrate_tool_build():
    runner = BatchRunner(verbose=True)
    
    # Multi-phase tool build
    runner.add_command("tests", "python test_tool.py")
    runner.add_command("lint", "python check_unicode.py")
    runner.add_command("docs", "python generate_docs.py")
    runner.add_command(
        "upload",
        "gh repo create DonkRonk17/NewTool --public --source=. --push",
        depends_on=["tests", "lint", "docs"]
    )
    
    result = runner.run()
    
    if result["success"]:
        quick_send("TEAM", "Tool Build Complete", "All phases succeeded")
    else:
        quick_send("ATLAS,LOGAN", "Tool Build Failed", f"{result['failed']} phases failed", priority="HIGH")
    
    return result
```

#### Atlas (Executor / Builder)

**Primary Use Case:** Automate Holy Grail tool build phases

**Integration Steps:**
1. Create standard build pipeline configs
2. Integrate with ToolRegistry for tool verification
3. Use for Phase 2-6 automation
4. Track quality gates with batch status

**Example Workflow:**

```python
from batchrunner import BatchRunner
from pathlib import Path

def holy_grail_build(tool_name):
    runner = BatchRunner(verbose=True)
    
    tool_dir = Path(f"AutoProjects/{tool_name}")
    
    # Phase 2-5: Development and testing
    runner.add_command("tests", f"python {tool_dir}/test_{tool_name.lower()}.py")
    runner.add_command("lint-check", f"python check_no_unicode.py {tool_dir}")
    runner.add_command(
        "docs-check",
        f"python verify_docs.py {tool_dir}",
        depends_on=["tests"]
    )
    runner.add_command(
        "branding-check",
        f"test -f {tool_dir}/branding/BRANDING_PROMPTS.md",
        depends_on=["docs-check"]
    )
    
    result = runner.run(abort_on_failure=True)
    
    if result["success"]:
        print(f"[OK] {tool_name} passed all quality gates")
        return True
    else:
        print(f"[FAIL] {tool_name} failed quality gates")
        return False
```

#### Clio (Linux Agent)

**Primary Use Case:** Server deployment and Linux automation

**Platform Considerations:**
- Full shell compatibility on Linux
- Systemd service management
- Package installation workflows

**Example:**

```bash
# Linux deployment batch
batchrunner run linux-deploy.json --verbose
```

```json
{
  "commands": [
    {"name": "update", "command": "sudo apt update"},
    {"name": "install", "command": "sudo apt install -y nginx postgresql", "depends_on": ["update"]},
    {"name": "config", "command": "sudo cp configs/*.conf /etc/nginx/", "depends_on": ["install"]},
    {"name": "restart", "command": "sudo systemctl restart nginx", "depends_on": ["config"]}
  ]
}
```

#### Nexus (Multi-Platform Agent)

**Primary Use Case:** Cross-platform builds and deployments

**Cross-Platform Notes:**
- Commands work on Windows, Linux, macOS
- Use platform-specific commands where needed
- Test on all platforms before deployment

**Example:**

```python
import platform
from batchrunner import BatchRunner

runner = BatchRunner()

if platform.system() == "Windows":
    runner.add_command("build", "msbuild project.sln")
elif platform.system() == "Darwin":  # macOS
    runner.add_command("build", "xcodebuild")
else:  # Linux
    runner.add_command("build", "make")

result = runner.run()
```

#### Bolt (Free Executor)

**Primary Use Case:** Cost-free batch operations without API usage

**Cost Considerations:**
- Zero API calls - pure command execution
- Perfect for repetitive automation
- Bulk file operations

**Example:**

```bash
# Batch file processing (no AI needed)
batchrunner run bulk-convert.json
```

---

## 🔗 INTEGRATION WITH OTHER TEAM BRAIN TOOLS

### With AgentHealth

**Correlation Use Case:** Track batch execution health and performance

**Integration Pattern:**

```python
from agenthealth import AgentHealth
from batchrunner import BatchRunner

health = AgentHealth()
runner = BatchRunner()

session_id = "pipeline_123"
health.start_session("ATLAS", session_id=session_id)

result = runner.run()

health.log_metric("ATLAS", "pipeline_duration", result["duration"])
health.log_metric("ATLAS", "commands_executed", result["executed"])

health.end_session("ATLAS", session_id=session_id, status="success" if result["success"] else "failed")
```

### With SynapseLink

**Notification Use Case:** Alert team on pipeline completion/failure

**Integration Pattern:**

```python
from synapselink import quick_send
from batchrunner import BatchRunner

runner = BatchRunner()
result = runner.run()

if result["success"]:
    quick_send(
        "TEAM",
        "Pipeline Complete",
        f"Batch completed successfully in {result['duration']:.1f}s\n"
        f"{result['successful']} commands succeeded",
        priority="NORMAL"
    )
else:
    quick_send(
        "FORGE,LOGAN",
        "Pipeline Failed - Review Needed",
        f"{result['failed']} commands failed\n"
        f"Duration: {result['duration']:.1f}s",
        priority="HIGH"
    )
```

### With SessionReplay

**Debugging Use Case:** Record batch execution for post-mortem analysis

**Integration Pattern:**

```python
from sessionreplay import SessionReplay
from batchrunner import BatchRunner

replay = SessionReplay()
runner = BatchRunner()

session_id = replay.start_session("ATLAS", task="Build pipeline")
replay.log_input(session_id, "Starting batch execution")

result = runner.run()

replay.log_output(session_id, runner.generate_report(format="json"))
replay.end_session(session_id, status="COMPLETED" if result["success"] else "FAILED")
```

### With ErrorRecovery

**Recovery Use Case:** Auto-retry entire pipelines on failure

**Integration Pattern:**

```python
from errorrecovery import with_recovery
from batchrunner import BatchRunner
from pathlib import Path

@with_recovery(max_attempts=3, strategy="retry", delay=5)
def run_critical_pipeline():
    runner = BatchRunner()
    runner.load_from_file(Path("critical-pipeline.json"))
    result = runner.run()
    
    if not result["success"]:
        raise Exception(f"{result['failed']} commands failed")
    
    return result

result = run_critical_pipeline()
```

### With TokenTracker

**Cost Tracking Use Case:** Track pipeline execution costs

**Integration Pattern:**

```python
from tokentracker import TokenTracker
from batchrunner import BatchRunner

tracker = TokenTracker()
runner = BatchRunner()

# Track execution
start_tokens = tracker.get_usage()
result = runner.run()
end_tokens = tracker.get_usage()

tracker.log_operation(
    "batchrunner_pipeline",
    duration=result["duration"],
    cost=0.0  # BatchRunner itself has no API cost
)
```

---

## 🚀 ADOPTION ROADMAP

### Phase 1: Core Adoption (Week 1)

**Goal:** All agents aware and can use basic features

**Steps:**
1. ✅ Tool deployed to GitHub
2. ☐ Quick-start guides sent via Synapse
3. ☐ Each agent tests basic workflow
4. ☐ Feedback collected

**Success Criteria:**
- All 5 agents have used BatchRunner at least once
- No blocking issues reported

### Phase 2: Integration (Week 2-3)

**Goal:** Integrated into daily workflows

**Steps:**
1. ☐ Create standard configs for common workflows
2. ☐ Integrate with AgentHealth, SynapseLink, SessionReplay
3. ☐ Update agent startup routines to include BatchRunner
4. ☐ Monitor usage patterns

**Success Criteria:**
- Used daily by at least 3 agents
- 5+ standard configs created
- Integration examples tested

### Phase 3: Optimization (Week 4+)

**Goal:** Optimized and fully adopted

**Steps:**
1. ☐ Collect efficiency metrics (time saved)
2. ☐ Implement v1.1 improvements based on feedback
3. ☐ Create advanced workflow examples
4. ☐ Full Team Brain ecosystem integration

**Success Criteria:**
- Measurable time savings (5+ min per use)
- Positive feedback from all agents
- v1.1 feature requests identified

---

## 📊 SUCCESS METRICS

**Adoption Metrics:**
- Number of agents using tool: [Track]
- Daily usage count: [Track]
- Number of standard configs created: [Track]

**Efficiency Metrics:**
- Time saved per pipeline: ~5-10 minutes
- Reduction in manual command execution: 80%+
- Error reduction through automation: 50%+

**Quality Metrics:**
- Bug reports: [Track]
- Feature requests: [Track]
- User satisfaction: [Qualitative feedback]

---

## 🛠️ TECHNICAL INTEGRATION DETAILS

### Import Paths

```python
# Standard import
from batchrunner import BatchRunner

# Import result/command classes
from batchrunner import CommandResult, Command
```

### Configuration Integration

**Shared Config Pattern:**

```python
from configmanager import ConfigManager
from batchrunner import BatchRunner
from pathlib import Path

config = ConfigManager()
batch_config = config.get("batchrunner.default_pipeline", "build.json")

runner = BatchRunner()
runner.load_from_file(Path(batch_config))
result = runner.run()
```

### Error Handling Integration

**Standardized Error Codes:**
- 0: Success (all commands succeeded)
- 1: Failure (one or more commands failed)
- 2: Validation error (invalid configuration)

**Error Pattern:**

```python
result = runner.run()

if result["success"]:
    return 0  # Success
elif "error" in result:
    print(f"[X] Configuration error: {result['error']}")
    return 2
else:
    print(f"[X] Execution failed: {result['failed']} commands failed")
    return 1
```

---

## 🔧 MAINTENANCE & SUPPORT

### Update Strategy
- Minor updates (v1.x): As needed based on feedback
- Major updates (v2.0+): Quarterly if significant features needed
- Bug fixes: Immediate

### Support Channels
- GitHub Issues: Bug reports and feature requests
- Synapse: Team Brain discussions and coordination
- Direct to ATLAS: Complex integration issues

### Known Limitations
- Commands run non-interactively (no stdin support)
- Shell-specific syntax varies by platform
- No built-in secret management (use env vars)

### Planned Improvements (v1.1+)
- Watch mode (re-run on file changes)
- Command templates/aliases
- Graphical dependency visualization
- Integration with BCH WebSocket API

---

## 📚 ADDITIONAL RESOURCES

- [README.md](README.md) - Main documentation
- [EXAMPLES.md](EXAMPLES.md) - 12 comprehensive examples
- [QUICK_START_GUIDES.md](QUICK_START_GUIDES.md) - Agent-specific guides
- [INTEGRATION_EXAMPLES.md](INTEGRATION_EXAMPLES.md) - Copy-paste integration patterns
- [CHEAT_SHEET.txt](CHEAT_SHEET.txt) - Quick reference
- GitHub: https://github.com/DonkRonk17/BatchRunner

---

**Last Updated:** February 9, 2026  
**Maintained By:** ATLAS (Team Brain)
