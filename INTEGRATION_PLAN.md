# BatchRunner - Integration Plan

## 🎯 INTEGRATION GOALS

This document outlines how BatchRunner integrates with:
1. Team Brain agents (Forge, Atlas, Clio, Nexus, Bolt)
2. Existing Team Brain tools
3. Logan's workflows
4. CI/CD pipelines

---

## 📦 BCH INTEGRATION

**Status:** Not currently integrated with BCH (standalone CLI tool)

**Rationale:** BatchRunner is a general-purpose utility that operates independently. Future BCH integration could add:
- `@batchrunner run <file>` command
- Status monitoring in BCH dashboard
- Result notifications via BCH

---

## 🤖 AI AGENT INTEGRATION

### Integration Matrix

| Agent | Use Case | Integration Method | Priority |
|-------|----------|-------------------|----------|
| **Forge** | Build orchestration, code quality checks | Python API | HIGH |
| **Atlas** | Tool builds, testing automation | CLI + Python | HIGH |
| **Clio** | System administration, batch ops | CLI | MEDIUM |
| **Nexus** | Cross-platform testing | CLI | MEDIUM |
| **Bolt** | Automated task execution | CLI | LOW |

### Agent-Specific Workflows

#### Forge (Orchestrator / Reviewer)
**Primary Use Case:** Orchestrate multi-step code quality workflows

**Integration Example:**
```python
from batchrunner import BatchRunner

# Quality gate pipeline
commands = [
    "python -m black . --check",
    "python -m isort . --check",
    "python -m mypy .",
    "python -m pytest tests/",
    "python -m bandit -r src/"
]

runner = BatchRunner(commands, mode="sequential", verbose=True)
results, summary = runner.run()

if summary["success_rate"] < 100:
    print(f"[!] Quality gates failed: {summary['failed']} checks")
    sys.exit(1)
```

#### Atlas (Executor / Builder)
**Primary Use Case:** Automate tool build and testing

**Integration Example:**
```python
# In tool build workflow
test_commands = [
    "python test_module1.py",
    "python test_module2.py",
    "python test_integration.py"
]

runner = BatchRunner(
    test_commands,
    mode="parallel",
    max_retries=1,
    log_file=Path(f"test-{datetime.now():%Y%m%d}.log")
)

results, summary = runner.run()

if summary["failed"] == 0:
    print("[OK] All tests passing - ready for deployment")
else:
    print(f"[X] {summary['failed']} tests failed - fix before deploying")
```

#### Clio (Linux / Ubuntu Agent)
**Primary Use Case:** System administration batch operations

**Example:**
```bash
# Create system-maintenance.txt
echo "Updating package lists..."
apt-get update
echo "Upgrading packages..."
apt-get upgrade -y
echo "Cleaning package cache..."
apt-get autoremove -y
apt-get autoclean

# Run with retries
python batchrunner.py -f system-maintenance.txt --retries 2 -l maintenance.log
```

---

## 🔗 INTEGRATION WITH OTHER TEAM BRAIN TOOLS

### With AgentHealth
**Use Case:** Track batch job health metrics

```python
from agenthealth import AgentHealth
from batchrunner import BatchRunner

health = AgentHealth()
session_id = health.start_session("ATLAS", task="Build pipeline")

runner = BatchRunner(commands, log_file=f"batch-{session_id}.log")
results, summary = runner.run()

health.end_session("ATLAS", session_id, 
    status="success" if summary["failed"] == 0 else "failed",
    metrics={"commands_run": summary["total_commands"], 
             "success_rate": summary["success_rate"]}
)
```

### With SynapseLink
**Use Case:** Notify team of batch job results

```python
from synapselink import quick_send
from batchrunner import BatchRunner

runner = BatchRunner(critical_commands, max_retries=3)
results, summary = runner.run()

if summary["failed"] > 0:
    quick_send("FORGE,LOGAN", 
        "Batch Job Failed",
        f"{summary['failed']}/{summary['total_commands']} commands failed\n"
        f"Success rate: {summary['success_rate']:.1f}%",
        priority="HIGH"
    )
```

### With TokenTracker
**Use Case:** Track costs for API-heavy batch jobs

```python
from tokentracker import TokenTracker
from batchrunner import BatchRunner

tracker = TokenTracker()
session_id = tracker.start_session("batch_api_calls")

# Run batch of API calls
runner = BatchRunner(api_commands)
results, summary = runner.run()

# Estimate token usage (if applicable)
estimated_tokens = len(api_commands) * 500  # rough estimate
tracker.log_usage(session_id, estimated_tokens, "BatchRunner API calls")
```

---

## 🚀 ADOPTION ROADMAP

### Phase 1: Core Adoption (Week 1)
**Goal:** All agents know about BatchRunner and can use basic features

**Steps:**
1. ✓ Tool deployed to GitHub
2. ☐ Quick-start sent via Synapse to all agents
3. ☐ Each agent tests basic workflow
4. ☐ Feedback collected

**Success Criteria:**
- All 5 agents have used BatchRunner at least once
- No blocking issues reported

### Phase 2: Integration (Week 2-3)
**Goal:** Integrated into daily workflows

**Steps:**
1. ☐ Add to agent startup routines where appropriate
2. ☐ Create integration examples with existing tools
3. ☐ Document best practices per agent
4. ☐ Monitor usage patterns

**Success Criteria:**
- Used by at least 3 agents weekly
- Integration examples tested and working

### Phase 3: Optimization (Week 4+)
**Goal:** Optimized and fully adopted

**Steps:**
1. ☐ Collect efficiency metrics
2. ☐ Implement v1.1 improvements based on feedback
3. ☐ Create advanced workflow examples
4. ☐ Full Team Brain ecosystem integration

**Success Criteria:**
- Measurable time savings documented
- Positive feedback from all users
- v1.1 roadmap defined

---

## 📊 SUCCESS METRICS

**Adoption Metrics:**
- Number of agents using tool: Track weekly
- Daily batch job count: Track via logs
- Integration with other tools: Count implementations

**Efficiency Metrics:**
- Time saved per batch job: Compare manual vs automated
- Error reduction: Track failure rates with retries
- Standardization: Measure workflow consistency

**Quality Metrics:**
- Bug reports: Track GitHub issues
- Feature requests: Track and prioritize
- User satisfaction: Qualitative feedback

---

## 🛠️ TECHNICAL INTEGRATION DETAILS

### Import Paths
```python
# Main class
from batchrunner import BatchRunner

# Helper function
from batchrunner import load_commands_from_file

# Result classes
from batchrunner import CommandResult
```

### Configuration Best Practices
```python
# Production configuration
runner = BatchRunner(
    commands=production_commands,
    mode="sequential",           # Use sequential for critical steps
    max_retries=2,               # Retry twice for transient failures
    retry_delay_sec=2.0,         # 2-second delay between retries
    timeout_sec=300,             # 5-minute timeout per command
    log_file=Path(f"batch-{datetime.now():%Y%m%d-%H%M%S}.log"),
    verbose=False                # Quiet mode for production
)
```

### Error Handling Integration
**Exit Codes:**
- 0: All commands successful
- 1: One or more commands failed
- 130: User interrupt (Ctrl+C)

**Recommended Pattern:**
```python
try:
    runner = BatchRunner(commands)
    results, summary = runner.run()
    
    if summary["failed"] > 0:
        # Handle partial failure
        print(f"Warning: {summary['failed']} commands failed")
        # Decide: continue or abort?
    
except KeyboardInterrupt:
    print("Batch interrupted by user")
    sys.exit(130)
except Exception as e:
    print(f"Batch runner error: {e}")
    sys.exit(1)
```

---

## 🔧 MAINTENANCE & SUPPORT

### Update Strategy
- Minor updates (v1.x): As needed for bug fixes
- Major updates (v2.0+): When significant features added
- Security patches: Immediate (though unlikely given stdlib-only)

### Support Channels
- GitHub Issues: Bug reports and feature requests
- Synapse: Team Brain discussions and quick questions
- Direct to Builder (ATLAS): Complex integration questions

### Known Limitations
- Thread-based parallelism (not process-based) - limited by GIL for CPU-bound tasks
- No built-in scheduling - use external cron/Task Scheduler
- Platform-specific command differences require testing

---

## 📚 ADDITIONAL RESOURCES

- Main Documentation: [README.md](README.md) (610 lines)
- Examples: [EXAMPLES.md](EXAMPLES.md) (15+ working examples)
- Quick Start Guides: [QUICK_START_GUIDES.md](QUICK_START_GUIDES.md) (agent-specific)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt) (quick reference)
- GitHub: https://github.com/DonkRonk17/BatchRunner

---

**Last Updated:** February 13, 2026  
**Maintained By:** ATLAS (Team Brain)

*Built with precision. Deployed with pride.*  
*Team Brain Standard: 99%+ Quality, Every Time.* ⚛️
