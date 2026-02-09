# BatchRunner - Usage Examples

Complete guide with 10+ working examples covering all features.

**Quick Navigation:**
- [Example 1: Basic Usage](#example-1-basic-usage)
- [Example 2: Dependency Chain](#example-2-dependency-chain)
- [Example 3: Parallel Execution](#example-3-parallel-execution)
- [Example 4: Error Handling](#example-4-error-handling)
- [Example 5: Retry Logic](#example-5-retry-logic)
- [Example 6: Environment Variables](#example-6-environment-variables)
- [Example 7: Working Directories](#example-7-working-directories)
- [Example 8: Timeout Control](#example-8-timeout-control)
- [Example 9: CI/CD Pipeline](#example-9-cicd-pipeline)
- [Example 10: Python API](#example-10-python-api)
- [Example 11: Report Generation](#example-11-report-generation)
- [Example 12: Dry Run Mode](#example-12-dry-run-mode)

---

## Example 1: Basic Usage

**Scenario:** First time using BatchRunner - execute two simple commands.

**Configuration (`basic.json`):**

```json
{
  "commands": [
    {"name": "hello", "command": "echo Hello from BatchRunner"},
    {"name": "timestamp", "command": "date"}
  ]
}
```

**Execute:**

```bash
python batchrunner.py run basic.json --verbose
```

**Expected Output:**

```
[OK] Dependency validation passed
[OK] Execution plan: 1 groups
  Group 1: hello, timestamp

[GROUP 1] Executing 2 commands...
[RUN] hello: echo Hello from BatchRunner
[RUN] timestamp: date

======================================================================
BATCHRUNNER EXECUTION REPORT
======================================================================
Total Commands: 2
Successful: 2
Failed: 0

[OK] echo Hello from BatchRunner
  Exit Code: 0
  Duration: 0.02s

[OK] date
  Exit Code: 0
  Duration: 0.01s
======================================================================
```

**What You Learned:**
- How to create a basic configuration file
- Commands run in parallel (no dependencies)
- All output is captured and reported

---

## Example 2: Dependency Chain

**Scenario:** Build → Test → Deploy pipeline where each step depends on the previous.

**Configuration (`pipeline.json`):**

```json
{
  "commands": [
    {"name": "build", "command": "echo Building application..."},
    {"name": "test", "command": "echo Running tests...", "depends_on": ["build"]},
    {"name": "deploy", "command": "echo Deploying to production...", "depends_on": ["test"]}
  ]
}
```

**Execute:**

```bash
python batchrunner.py run pipeline.json --verbose
```

**Expected Output:**

```
[OK] Execution plan: 3 groups
  Group 1: build
  Group 2: test
  Group 3: deploy

[GROUP 1] Executing 1 commands...
[RUN] build: echo Building application...

[GROUP 2] Executing 1 commands...
[RUN] test: echo Running tests...

[GROUP 3] Executing 1 commands...
[RUN] deploy: echo Deploying to production...
```

**What You Learned:**
- How to create linear dependencies (A → B → C)
- Commands execute sequentially
- Each group waits for previous to complete

---

## Example 3: Parallel Execution

**Scenario:** Run lint, unit tests, and integration tests simultaneously.

**Configuration (`parallel.json`):**

```json
{
  "commands": [
    {"name": "lint", "command": "echo Linting code..."},
    {"name": "unit-tests", "command": "echo Running unit tests..."},
    {"name": "integration-tests", "command": "echo Running integration tests..."}
  ]
}
```

**Execute:**

```bash
python batchrunner.py run parallel.json --verbose
```

**Expected Output:**

```
[OK] Execution plan: 1 groups
  Group 1: lint, unit-tests, integration-tests

[GROUP 1] Executing 3 commands...
[RUN] lint: echo Linting code...
[RUN] unit-tests: echo Running unit tests...
[RUN] integration-tests: echo Running integration tests...

======================================================================
Total Commands: 3
Successful: 3
Failed: 0
Duration: 0.05s
======================================================================
```

**What You Learned:**
- Commands without dependencies run in parallel
- Total time = slowest command (not sum of all)
- Significant time savings on independent tasks

---

## Example 4: Error Handling

**Scenario:** Handle command failures with abort-on-failure.

**Configuration (`error-abort.json`):**

```json
{
  "commands": [
    {"name": "success", "command": "echo This will succeed"},
    {"name": "failure", "command": "exit 1"},
    {"name": "never-runs", "command": "echo This never executes", "depends_on": ["failure"]}
  ]
}
```

**Execute:**

```bash
python batchrunner.py run error-abort.json --verbose
```

**Expected Output:**

```
[GROUP 1] Executing 2 commands...
[RUN] success: echo This will succeed
[RUN] failure: exit 1
[ABORT] Stopping execution due to failure

======================================================================
Total Commands: 3
Executed: 2
Successful: 1
Failed: 1
======================================================================

[OK] echo This will succeed
  Exit Code: 0

[FAIL] exit 1
  Exit Code: 1
```

**What You Learned:**
- Abort-on-failure stops at first error
- Dependent commands don't execute
- Clear failure reporting

---

## Example 5: Retry Logic

**Scenario:** Retry failing commands with backoff.

**Configuration (`retry.json`):**

```json
{
  "commands": [
    {
      "name": "flaky-api",
      "command": "curl https://api.example.com/health",
      "retry_count": 3,
      "retry_delay": 2,
      "timeout": 10
    }
  ]
}
```

**Execute:**

```bash
python batchrunner.py run retry.json --verbose
```

**Expected Output (if fails initially):**

```
[RUN] flaky-api: curl https://api.example.com/health
[RETRY] flaky-api failed (attempt 1/4), retrying in 2s...
[RUN] flaky-api: curl https://api.example.com/health
[RETRY] flaky-api failed (attempt 2/4), retrying in 2s...
[RUN] flaky-api: curl https://api.example.com/health
[OK] Command succeeded on attempt 3
```

**What You Learned:**
- Retry transient failures automatically
- Configurable retry count and delay
- Useful for network requests and flaky tests

---

## Example 6: Environment Variables

**Scenario:** Pass environment variables to commands.

**Configuration (`env.json`):**

```json
{
  "commands": [
    {
      "name": "deploy-staging",
      "command": "echo Deploying to $DEPLOY_ENV with API key $API_KEY",
      "env": {
        "DEPLOY_ENV": "staging",
        "API_KEY": "staging-key-123"
      }
    },
    {
      "name": "deploy-prod",
      "command": "echo Deploying to $DEPLOY_ENV with API key $API_KEY",
      "env": {
        "DEPLOY_ENV": "production",
        "API_KEY": "prod-key-456"
      }
    }
  ]
}
```

**Execute:**

```bash
python batchrunner.py run env.json
```

**Expected Output:**

```
[OK] echo Deploying to staging with API key staging-key-123
[OK] echo Deploying to production with API key prod-key-456
```

**What You Learned:**
- Per-command environment variables
- Useful for different deployment environments
- Variables isolated per command

---

## Example 7: Working Directories

**Scenario:** Execute commands in different directories.

**Configuration (`workdir.json`):**

```json
{
  "commands": [
    {
      "name": "frontend-build",
      "command": "npm run build",
      "working_dir": "./frontend"
    },
    {
      "name": "backend-build",
      "command": "python setup.py build",
      "working_dir": "./backend"
    }
  ]
}
```

**Execute:**

```bash
python batchrunner.py run workdir.json --verbose
```

**Expected Output:**

```
[RUN] frontend-build: npm run build
  Working Directory: ./frontend

[RUN] backend-build: python setup.py build
  Working Directory: ./backend
```

**What You Learned:**
- Run commands in specific directories
- Useful for monorepos with multiple projects
- Each command has independent working directory

---

## Example 8: Timeout Control

**Scenario:** Kill commands that run too long.

**Configuration (`timeout.json`):**

```json
{
  "commands": [
    {
      "name": "quick-task",
      "command": "echo Quick task",
      "timeout": 5
    },
    {
      "name": "slow-task",
      "command": "sleep 30",
      "timeout": 10
    }
  ]
}
```

**Execute:**

```bash
python batchrunner.py run timeout.json --verbose
```

**Expected Output:**

```
[OK] quick-task: echo Quick task
  Duration: 0.01s

[FAIL] slow-task: sleep 30
  Exit Code: -1
  Error: Timeout after 10s
```

**What You Learned:**
- Prevent runaway commands
- Configurable timeout per command
- Clean termination on timeout

---

## Example 9: CI/CD Pipeline

**Scenario:** Complete real-world CI/CD pipeline.

**Configuration (`cicd.json`):**

```json
{
  "commands": [
    {
      "name": "install",
      "command": "npm install",
      "timeout": 300
    },
    {
      "name": "lint",
      "command": "npm run lint"
    },
    {
      "name": "test",
      "command": "npm test",
      "depends_on": ["install"],
      "retry_count": 2
    },
    {
      "name": "build",
      "command": "npm run build",
      "depends_on": ["test"],
      "timeout": 600
    },
    {
      "name": "docker-build",
      "command": "docker build -t myapp:latest .",
      "depends_on": ["build"],
      "timeout": 900
    },
    {
      "name": "docker-push",
      "command": "docker push myapp:latest",
      "depends_on": ["docker-build"],
      "retry_count": 3,
      "retry_delay": 5
    }
  ]
}
```

**Execute:**

```bash
python batchrunner.py run cicd.json --verbose --report markdown > pipeline-report.md
```

**Execution Plan:**

```
Group 1: install, lint (parallel)
Group 2: test
Group 3: build
Group 4: docker-build
Group 5: docker-push
```

**What You Learned:**
- Real-world complex pipeline
- Mix of parallel and sequential execution
- Multiple failure handling strategies
- Comprehensive timeout and retry configuration

---

## Example 10: Python API

**Scenario:** Use BatchRunner programmatically.

**Code (`build_script.py`):**

```python
from batchrunner import BatchRunner

def main():
    # Create runner
    runner = BatchRunner(verbose=True)
    
    # Add commands
    runner.add_command("clean", "rm -rf dist")
    runner.add_command("compile", "tsc", depends_on=["clean"])
    runner.add_command("webpack", "webpack --mode production", depends_on=["compile"])
    runner.add_command("test", "jest", depends_on=["compile"])
    runner.add_command(
        "deploy",
        "aws s3 sync dist/ s3://mybucket/",
        depends_on=["webpack", "test"],
        timeout=300,
        retry_count=3
    )
    
    # Validate before running
    is_valid, errors = runner.validate_dependencies()
    if not is_valid:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    # Execute
    result = runner.run(abort_on_failure=True)
    
    # Check results
    if result["success"]:
        print(f"\n[OK] Pipeline complete! {result['successful']} commands succeeded")
        print(f"Total duration: {result['duration']:.2f}s")
        return 0
    else:
        print(f"\n[FAIL] Pipeline failed: {result['failed']} commands failed")
        return 1

if __name__ == "__main__":
    exit(main())
```

**Execute:**

```bash
python build_script.py
```

**What You Learned:**
- Full Python API control
- Programmatic command addition
- Custom validation and error handling
- Integration with existing Python scripts

---

## Example 11: Report Generation

**Scenario:** Generate detailed reports in multiple formats.

**Code:**

```python
from batchrunner import BatchRunner

runner = BatchRunner()
runner.add_command("test1", "echo Test 1")
runner.add_command("test2", "echo Test 2")
runner.add_command("test3", "echo Test 3")

result = runner.run()

# Text report
print(runner.generate_report(format="text"))

# JSON report
with open("report.json", "w") as f:
    f.write(runner.generate_report(format="json"))

# Markdown report
with open("report.md", "w") as f:
    f.write(runner.generate_report(format="markdown"))
```

**Markdown Report Output:**

```markdown
# BatchRunner Execution Report

**Executed:** 2026-02-09T04:00:00

**Total Commands:** 3
**Successful:** 3
**Failed:** 0

## Commands

### [OK] echo Test 1
- **Exit Code:** 0
- **Duration:** 0.02s

### [OK] echo Test 2
- **Exit Code:** 0
- **Duration:** 0.01s

### [OK] echo Test 3
- **Exit Code:** 0
- **Duration:** 0.02s
```

**What You Learned:**
- Multiple report formats available
- Easy integration with documentation
- Exportable for analysis

---

## Example 12: Dry Run Mode

**Scenario:** Preview execution without running commands.

**Configuration (`complex.json`):**

```json
{
  "commands": [
    {"name": "step1", "command": "dangerous-command.sh"},
    {"name": "step2", "command": "another-dangerous-command.sh", "depends_on": ["step1"]},
    {"name": "step3", "command": "final-dangerous-command.sh", "depends_on": ["step2"]}
  ]
}
```

**Execute:**

```bash
python batchrunner.py run complex.json --dry-run --verbose
```

**Expected Output:**

```
[OK] Dependency validation passed
[OK] Execution plan: 3 groups
  Group 1: step1
  Group 2: step2
  Group 3: step3

[DRY RUN] Would execute: step1
[DRY RUN] Would execute: step2
[DRY RUN] Would execute: step3

======================================================================
Total Commands: 3
All commands validated successfully
No commands actually executed (dry run mode)
======================================================================
```

**What You Learned:**
- Test configuration without execution
- Verify dependency order
- Safe to test on production configs

---

## More Examples

For more integration examples with Team Brain tools, see:

- [INTEGRATION_EXAMPLES.md](INTEGRATION_EXAMPLES.md) - Integration patterns with AgentHealth, SynapseLink, etc.
- [QUICK_START_GUIDES.md](QUICK_START_GUIDES.md) - Agent-specific usage guides
- [CHEAT_SHEET.txt](CHEAT_SHEET.txt) - Quick reference

---

**Examples maintained by:** ATLAS (Team Brain)  
**Last updated:** February 9, 2026
