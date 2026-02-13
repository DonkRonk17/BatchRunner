# BatchRunner - Quick Start Guides

## 📖 ABOUT THESE GUIDES

Each Team Brain agent has a **3-minute quick-start guide** tailored to their role and workflows.

**Choose your guide:**
- [Forge (Orchestrator)](#forge-quick-start)
- [Atlas (Executor)](#atlas-quick-start)
- [Clio (Linux Agent)](#clio-quick-start)
- [Nexus (Multi-Platform)](#nexus-quick-start)
- [Bolt (Free Executor)](#bolt-quick-start)

---

## 🔥 FORGE QUICK START

**Role:** Orchestrator / Reviewer  
**Time:** 3 minutes  
**Goal:** Use BatchRunner for code quality orchestration

### Step 1: Verify Installation
```bash
cd C:\Users\logan\OneDrive\Documents\AutoProjects\BatchRunner
python batchrunner.py --version
# Expected: BatchRunner v1.0
```

### Step 2: Create Quality Pipeline
```bash
# Create quality-checks.txt
cat > quality-checks.txt << EOF
python -m black . --check
python -m isort . --check-only
python -m mypy .
python -m pytest tests/ -v
python -m bandit -r src/
EOF
```

### Step 3: Run Quality Gates
```python
# In your Forge session
from batchrunner import BatchRunner

commands = [
    "python -m black . --check",
    "python -m mypy .",
    "python -m pytest"
]

runner = BatchRunner(commands, mode="sequential", verbose=True)
results, summary = runner.run()

if summary["success_rate"] == 100:
    print("[OK] All quality gates passed!")
else:
    print(f"[X] {summary['failed']} quality gates failed")
```

### Common Forge Commands
```bash
# Review code quality
python batchrunner.py -f quality-checks.txt -l quality.log

# Orchestrate multi-tool build
python batchrunner.py -f build-pipeline.txt --retries 1
```

### Next Steps for Forge
1. Integrate into code review workflows
2. Use for multi-agent task orchestration
3. Add to automated quality checks

---

## ⚡ ATLAS QUICK START

**Role:** Executor / Builder  
**Time:** 3 minutes  
**Goal:** Automate tool testing with BatchRunner

### Step 1: Quick Test
```bash
python -c "from batchrunner import BatchRunner; print('OK')"
```

### Step 2: Automate Tool Tests
```python
# In your Atlas tool build workflow
from batchrunner import BatchRunner
from pathlib import Path

# Test commands for a tool
test_commands = [
    "python test_module.py",
    "python test_integration.py",
    "python test_examples.py"
]

runner = BatchRunner(
    test_commands,
    mode="parallel",
    max_retries=1,
    log_file=Path("test-results.log")
)

results, summary = runner.run()

print(f"Tests: {summary['successful']}/{summary['total_commands']} passed")
```

### Step 3: Build Pipeline Integration
```bash
# Create build-steps.txt
echo "python -m pytest tests/" > build-steps.txt
echo "python -m black . --check" >> build-steps.txt
echo "python setup.py sdist bdist_wheel" >> build-steps.txt

# Run it
python batchrunner.py -f build-steps.txt -l build.log
```

### Common Atlas Commands
```bash
# Run all tests in parallel
python batchrunner.py -f all-tests.txt --parallel -o results.json

# Build with retries
python batchrunner.py -f build.txt --retries 2 -l build.log
```

### Next Steps for Atlas
1. Add to Holy Grail Protocol automation
2. Use for every tool test phase
3. Integrate with AgentHealth tracking

---

## 🐧 CLIO QUICK START

**Role:** Linux / Ubuntu Agent  
**Time:** 3 minutes  
**Goal:** System administration batch operations

### Step 1: Linux Installation
```bash
cd /path/to/AutoProjects/BatchRunner
chmod +x batchrunner.py
python3 batchrunner.py --version
```

### Step 2: System Maintenance Batch
```bash
# Create maintenance.txt
cat > maintenance.txt << 'EOF'
echo "Updating package lists..."
sudo apt-get update -q
echo "Checking for upgrades..."
apt list --upgradable
echo "System status:"
df -h
free -h
EOF

# Run it
python3 batchrunner.py -f maintenance.txt -l maintenance-$(date +%Y%m%d).log
```

### Step 3: Batch File Operations
```bash
# Convert multiple files
ls *.log | xargs -I {} echo "gzip {}" > compress-logs.txt
python3 batchrunner.py -f compress-logs.txt --parallel
```

### Common Clio Commands
```bash
# System maintenance
python3 batchrunner.py -f maintenance.txt --retries 1

# Backup multiple directories
python3 batchrunner.py -f backup.txt -l backup-$(date +%Y%m%d).log
```

### Next Steps for Clio
1. Add to ABIOS startup routines
2. Use for batch system operations
3. Integrate with log analysis workflows

---

## 🌐 NEXUS QUICK START

**Role:** Multi-Platform Agent  
**Time:** 3 minutes  
**Goal:** Cross-platform testing automation

### Step 1: Platform Detection
```python
import platform
from batchrunner import BatchRunner

print(f"Running on: {platform.system()}")

# Platform-specific commands
if platform.system() == "Windows":
    commands = ["dir", "echo Windows detected"]
else:
    commands = ["ls -la", "echo Unix detected"]

runner = BatchRunner(commands, verbose=True)
runner.run()
```

### Step 2: Cross-Platform Build
```bash
# Create cross-platform-tests.txt
# These commands work on all platforms
echo "Running cross-platform tests..."
python -m pytest tests/
python --version
python -c "import sys; print(sys.platform)"
```

### Step 3: Multi-Platform Verification
```bash
# Run on Windows, Linux, macOS
python batchrunner.py -f cross-platform-tests.txt -o platform-results.json
```

### Common Nexus Commands
```bash
# Test across platforms
python batchrunner.py -f platform-tests.txt --parallel

# Verify dependencies
python batchrunner.py -c "python --version" "pip --version" "git --version"
```

### Next Steps for Nexus
1. Create platform-specific test suites
2. Verify tool cross-platform compatibility
3. Report platform-specific issues

---

## 🆓 BOLT QUICK START

**Role:** Free Executor (Cline + Grok)  
**Time:** 3 minutes  
**Goal:** Cost-free batch automation

### Step 1: Verify No Cost
```bash
# BatchRunner is 100% free - zero dependencies!
python batchrunner.py --version
# No API calls, no paid services, just local execution
```

### Step 2: Automate Repetitive Tasks
```bash
# Create batch-tasks.txt
echo "echo 'Task 1 complete'" > batch-tasks.txt
echo "echo 'Task 2 complete'" >> batch-tasks.txt
echo "echo 'Task 3 complete'" >> batch-tasks.txt

python batchrunner.py -f batch-tasks.txt
```

### Step 3: Bulk Operations
```bash
# Process 50 files without any API costs
for i in {1..50}; do
    echo "python process.py file$i.txt" >> process-all.txt
done

python batchrunner.py -f process-all.txt --parallel -o results.json
```

### Common Bolt Commands
```bash
# Batch file operations (free!)
python batchrunner.py -f file-ops.txt --parallel

# Automated testing (no API usage)
python batchrunner.py -f tests.txt -l test-results.log
```

### Next Steps for Bolt
1. Use for all repetitive command sequences
2. Automate batch file processing
3. Replace manual command execution

---

## 📚 ADDITIONAL RESOURCES

**For All Agents:**
- Full Documentation: [README.md](README.md) (610 lines)
- Examples: [EXAMPLES.md](EXAMPLES.md) (15+ working examples)
- Integration Plan: [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt)

**Support:**
- GitHub Issues: https://github.com/DonkRonk17/BatchRunner/issues
- Synapse: Post in THE_SYNAPSE/active/
- Direct: Message ATLAS (tool builder)

---

**Last Updated:** February 13, 2026  
**Maintained By:** ATLAS (Team Brain)

*Quality is not an act, it is a habit!* ⚛️
