# BatchRunner - Quick Start Guides

5-minute guides for each Team Brain agent.

---

## 📖 ABOUT THESE GUIDES

Each guide is tailored to the agent's role and typical workflows. Choose your guide:

- [Forge (Orchestrator)](#-forge-quick-start)
- [Atlas (Executor)](#-atlas-quick-start)
- [Clio (Linux Agent)](#-clio-quick-start)
- [Nexus (Multi-Platform)](#-nexus-quick-start)
- [Bolt (Free Executor)](#-bolt-quick-start)

---

## 🔥 FORGE QUICK START

**Role:** Orchestrator / Reviewer  
**Time:** 5 minutes  
**Goal:** Orchestrate multi-tool workflows

### Step 1: Verify Installation

```bash
python C:\Users\logan\OneDrive\Documents\AutoProjects\BatchRunner\batchrunner.py --version
```

**Expected:** `BatchRunner 1.0`

### Step 2: Create Workflow Config

Create `forge-workflow.json`:

```json
{
  "commands": [
    {"name": "validate", "command": "python validate_tool.py"},
    {"name": "test", "command": "python test_tool.py"},
    {"name": "quality-check", "command": "python check_quality.py", "depends_on": ["validate", "test"]},
    {"name": "notify-team", "command": "python notify_complete.py", "depends_on": ["quality-check"]}
  ]
}
```

### Step 3: Execute Workflow

```bash
python batchrunner.py run forge-workflow.json --verbose --report markdown > workflow-report.md
```

### Step 4: Python API Integration

```python
from batchrunner import BatchRunner
from synapselink import quick_send

def orchestrate_build():
    runner = BatchRunner(verbose=True)
    runner.load_from_file(Path("forge-workflow.json"))
    
    result = runner.run()
    
    if result["success"]:
        quick_send("TEAM", "Workflow Complete", f"All {result['successful']} steps succeeded")
    else:
        quick_send("ATLAS,LOGAN", "Workflow Failed", f"{result['failed']} steps failed", priority="HIGH")
    
    return result
```

### Next Steps for Forge
1. Create standard workflow configs for common orchestration tasks
2. Integrate with SynapseLink for automated notifications
3. Use for multi-tool coordination workflows

---

## ⚡ ATLAS QUICK-START

**Role:** Executor / Builder  
**Time:** 5 minutes  
**Goal:** Automate Holy Grail tool build phases

### Step 1: Verify Installation

```bash
python C:\Users\logan\OneDrive\Documents\AutoProjects\BatchRunner\batchrunner.py --version
```

### Step 2: Create Build Pipeline

Create `holy-grail-pipeline.json`:

```json
{
  "commands": [
    {"name": "tests", "command": "python test_batchrunner.py"},
    {"name": "unicode-check", "command": "python check_unicode.py *.py"},
    {"name": "doc-check", "command": "test -f README.md && test -f EXAMPLES.md"},
    {"name": "integration-check", "command": "test -f INTEGRATION_PLAN.md", "depends_on": ["doc-check"]},
    {"name": "git-status", "command": "git status --short"}
  ]
}
```

### Step 3: Execute Build Pipeline

```bash
python batchrunner.py run holy-grail-pipeline.json --verbose
```

### Step 4: Python API for Tool Builds

```python
from batchrunner import BatchRunner
from pathlib import Path

def verify_tool_quality(tool_name):
    """Run all quality checks for a tool."""
    runner = BatchRunner(verbose=True)
    
    tool_dir = Path(f"AutoProjects/{tool_name}")
    
    runner.add_command("tests", f"python {tool_dir}/test_{tool_name.lower()}.py")
    runner.add_command("lint", f"grep -r '✅\\|❌\\|⚠️' {tool_dir}/*.py", failure_strategy="continue")
    runner.add_command("docs", f"wc -l {tool_dir}/README.md")  # Should be 400+ lines
    runner.add_command(
        "integration",
        f"test -f {tool_dir}/INTEGRATION_PLAN.md",
        depends_on=["docs"]
    )
    
    result = runner.run(abort_on_failure=True)
    
    if result["success"]:
        print(f"[OK] {tool_name} passed all quality gates (99%+)")
        return True
    else:
        print(f"[FAIL] {tool_name} failed quality gates")
        return False
```

### Next Steps for Atlas
1. Create standard pipeline configs for tool builds
2. Integrate into Holy Grail Protocol automation
3. Use for Phase 2-8 quality verification

---

## 🐧 CLIO QUICK START

**Role:** Linux / Ubuntu Agent  
**Time:** 5 minutes  
**Goal:** Automate Linux deployments and server management

### Step 1: Linux Installation

```bash
# Clone if needed
git clone https://github.com/DonkRonk17/BatchRunner.git
cd BatchRunner

# Make executable
chmod +x batchrunner.py

# Verify
./batchrunner.py --version
```

### Step 2: Create Linux Deployment Config

Create `linux-deploy.json`:

```json
{
  "commands": [
    {"name": "update", "command": "sudo apt update"},
    {"name": "install-nginx", "command": "sudo apt install -y nginx", "depends_on": ["update"]},
    {"name": "install-postgres", "command": "sudo apt install -y postgresql", "depends_on": ["update"]},
    {"name": "config-nginx", "command": "sudo cp nginx.conf /etc/nginx/", "depends_on": ["install-nginx"]},
    {"name": "restart-services", "command": "sudo systemctl restart nginx postgresql", "depends_on": ["config-nginx", "install-postgres"]}
  ]
}
```

### Step 3: Execute Deployment

```bash
./batchrunner.py run linux-deploy.json --verbose
```

### Step 4: Server Maintenance Workflow

```bash
# Create maintenance.json
{
  "commands": [
    {"name": "backup-db", "command": "pg_dump mydb > backup.sql"},
    {"name": "system-update", "command": "sudo apt update && sudo apt upgrade -y"},
    {"name": "clean-logs", "command": "sudo journalctl --vacuum-time=7d"},
    {"name": "restart-services", "command": "sudo systemctl restart nginx", "depends_on": ["system-update"]}
  ]
}
```

### Next Steps for Clio
1. Create deployment configs for ABIOS and BCH backend
2. Automate server maintenance tasks
3. Use for multi-service coordination

---

## 🌐 NEXUS QUICK START

**Role:** Multi-Platform Agent  
**Time:** 5 minutes  
**Goal:** Cross-platform builds and deployments

### Step 1: Platform Detection

```python
import platform
from batchrunner import BatchRunner

system = platform.system()
print(f"Platform: {system}")  # Windows, Darwin (macOS), or Linux

runner = BatchRunner()
```

### Step 2: Cross-Platform Config

Create `cross-platform-build.json`:

```json
{
  "commands": [
    {"name": "install-deps", "command": "pip install -r requirements.txt"},
    {"name": "test", "command": "python -m pytest", "depends_on": ["install-deps"]},
    {"name": "build", "command": "python setup.py build", "depends_on": ["test"]}
  ]
}
```

### Step 3: Platform-Specific Commands

```python
from batchrunner import BatchRunner
import platform

runner = BatchRunner()

# Platform-specific build commands
if platform.system() == "Windows":
    runner.add_command("build", "msbuild project.sln")
elif platform.system() == "Darwin":  # macOS
    runner.add_command("build", "xcodebuild -project app.xcodeproj")
else:  # Linux
    runner.add_command("build", "make")

runner.add_command("test", "python test.py", depends_on=["build"])

result = runner.run()
```

### Next Steps for Nexus
1. Test on all 3 platforms (Windows, macOS, Linux)
2. Create platform-specific deployment configs
3. Report platform-specific issues for fixes

---

## 🆓 BOLT QUICK START

**Role:** Free Executor (Cline + Grok)  
**Time:** 5 minutes  
**Goal:** Cost-free batch automation

### Step 1: Verify No API Costs

```bash
# BatchRunner uses zero AI APIs - perfect for Bolt!
python batchrunner.py --version
```

**Cost:** $0.00 per execution

### Step 2: Bulk Processing Config

Create `bulk-process.json`:

```json
{
  "commands": [
    {"name": "convert-images", "command": "mogrify -format jpg *.png"},
    {"name": "resize", "command": "mogrify -resize 800x600 *.jpg", "depends_on": ["convert-images"]},
    {"name": "optimize", "command": "optipng *.png"},
    {"name": "backup", "command": "tar -czf images-backup.tar.gz *.jpg *.png", "depends_on": ["resize", "optimize"]}
  ]
}
```

### Step 3: Execute Cost-Free

```bash
python batchrunner.py run bulk-process.json --verbose
```

**Result:** All operations complete with **ZERO API COSTS**

### Step 4: Batch File Operations

```python
from batchrunner import BatchRunner
from pathlib import Path

def bulk_file_operations(directory):
    """Process files in bulk without API costs."""
    runner = BatchRunner()
    
    # Find all files
    files = list(Path(directory).glob("*.txt"))
    
    # Add batch operations
    for i, file in enumerate(files):
        runner.add_command(
            f"process-{i}",
            f"python process_file.py {file}"
        )
    
    result = runner.run()
    print(f"Processed {result['successful']}/{len(files)} files at $0 cost")
```

### Next Steps for Bolt
1. Use for repetitive file operations
2. Automate bulk processing tasks
3. Save API costs on automation workflows

---

## 📚 ADDITIONAL RESOURCES

**For All Agents:**
- Full Documentation: [README.md](README.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Integration Plan: [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt)

**Support:**
- GitHub Issues: https://github.com/DonkRonk17/BatchRunner/issues
- Synapse: Post in THE_SYNAPSE/active/
- Direct: Contact ATLAS (Team Brain builder)

---

**Last Updated:** February 9, 2026  
**Maintained By:** ATLAS (Team Brain)
