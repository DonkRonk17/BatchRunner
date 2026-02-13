# BatchRunner - Usage Examples

Quick navigation:
- [Example 1: Basic Sequential Execution](#example-1-basic-sequential-execution)
- [Example 2: Parallel Batch Processing](#example-2-parallel-batch-processing)
- [Example 3: With Automatic Retries](#example-3-with-automatic-retries)
- [Example 4: Timeout Protection](#example-4-timeout-protection)
- [Example 5: File Logging](#example-5-file-logging)
- [Example 6: JSON Output for Analysis](#example-6-json-output-for-analysis)
- [Example 7: Inline Commands](#example-7-inline-commands)
- [Example 8: CI/CD Integration](#example-8-cicd-integration)
- [Example 9: Multi-Step Deployment](#example-9-multi-step-deployment)
- [Example 10: Database Operations](#example-10-database-operations)
- [Example 11: Error Handling Strategies](#example-11-error-handling-strategies)
- [Example 12: Performance Testing](#example-12-performance-testing)
- [Example 13: Docker Container Management](#example-13-docker-container-management)
- [Example 14: Git Workflow Automation](#example-14-git-workflow-automation)
- [Example 15: Real Production Workflow](#example-15-real-production-workflow)

---

## Example 1: Basic Sequential Execution

**Scenario:** First time using the tool

**Create commands.txt:**
```bash
echo "Hello from BatchRunner"
echo "Command 2"
echo "Command 3"
```

**Run:**
```bash
python batchrunner.py -f commands.txt
```

**Expected Output:**
```
======================================================================
BatchRunner v1.0 - Starting 3 commands
Mode: sequential
Retries: 0
======================================================================
... [all commands execute] ...
Total Commands: 3
Successful: 3
Failed: 0
Success Rate: 100.0%
```

**What You Learned:**
- How to create a commands file
- Basic sequential execution
- Reading the summary output

---

## Example 2: Parallel Batch Processing

**Scenario:** Convert 5 files simultaneously

**Create convert-files.txt:**
```bash
python convert.py file1.dat file1.json
python convert.py file2.dat file2.json
python convert.py file3.dat file3.json
python convert.py file4.dat file4.json
python convert.py file5.dat file5.json
```

**Run:**
```bash
python batchrunner.py -f convert-files.txt --parallel
```

**Expected Output:**
```
Mode: parallel
...
Total Duration: 523.4ms  (vs ~2500ms sequential!)
```

**What You Learned:**
- Parallel execution is 5x faster for independent tasks
- Use --parallel flag for speed
- All 5 conversions run simultaneously

---

## Example 3: With Automatic Retries

**Scenario:** Unreliable API calls

**Create api-calls.txt:**
```bash
curl https://api.example.com/endpoint1
curl https://api.example.com/endpoint2
curl https://api.example.com/endpoint3
```

**Run:**
```bash
python batchrunner.py -f api-calls.txt --retries 3 --retry-delay 2
```

**Expected Behavior:**
- If a curl fails, it retries up to 3 times
- 2-second delay between retries
- Total: 4 attempts per command (initial + 3 retries)

**What You Learned:**
- --retries handles flaky commands
- --retry-delay prevents hammering services
- Automatic exponential backoff

---

## Example 4: Timeout Protection

**Scenario:** Commands that might hang forever

**Create risky-commands.txt:**
```bash
curl https://slow-api.example.com --max-time 10
python long-running-script.py
ping -c 100 example.com
```

**Run:**
```bash
python batchrunner.py -f risky-commands.txt --timeout 30
```

**Expected Behavior:**
- Each command has 30-second max runtime
- If command exceeds 30s, it's killed
- Marked as failed with timeout error

**What You Learned:**
- Timeouts prevent infinite hangs
- Good for unreliable external services
- Can combine with --retries

---

## Example 5: File Logging

**Scenario:** Need audit trail of what happened

**Run:**
```bash
python batchrunner.py -f deploy.txt -l deploy-20260213.log
```

**Result: deploy-20260213.log**
```
[2026-02-13 12:00:00] [INFO] ======================================================================
[2026-02-13 12:00:00] [INFO] BatchRunner v1.0 - Starting 5 commands
[2026-02-13 12:00:00] [INFO] Mode: sequential
...
[2026-02-13 12:00:15] [SUCCESS] [OK] Command completed (1234.5ms)
...
```

**What You Learned:**
- -l flag enables file logging
- Timestamped events for debugging
- Can review logs later

---

## Example 6: JSON Output for Analysis

**Scenario:** Need structured data for reporting

**Run:**
```bash
python batchrunner.py -f tests.txt -o test-results.json
```

**Result: test-results.json**
```json
{
  "summary": {
    "total_commands": 10,
    "successful": 9,
    "failed": 1,
    "success_rate": 90.0,
    "total_duration_ms": 5234.2,
    "avg_command_duration_ms": 523.4,
    "mode": "sequential"
  },
  "results": [
    {
      "command": "pytest test_module.py",
      "success": true,
      "exit_code": 0,
      "stdout": "...test output...",
      "stderr": "",
      "duration_ms": 1234.5,
      "timestamp": "2026-02-13T12:00:00"
    }
  ]
}
```

**What You Learned:**
- -o flag exports JSON
- Perfect for CI/CD integration
- Structured data for analysis

---

## Example 7: Inline Commands

**Scenario:** Quick one-off task without creating a file

**Run:**
```bash
python batchrunner.py -c \
  "echo 'Starting...'" \
  "python script1.py" \
  "python script2.py" \
  "echo 'Done!'"
```

**What You Learned:**
- -c flag for inline commands
- No need to create files for simple tasks
- Great for ad-hoc automation

---

## Example 8: CI/CD Integration

**Scenario:** GitHub Actions workflow

**Create .github/workflows/test.yml:**
```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Tests
        run: |
          python batchrunner.py -f ci-tests.txt --parallel -o results.json
      
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: results.json
```

**ci-tests.txt:**
```bash
python -m pytest tests/unit
python -m pytest tests/integration
python -m black . --check
python -m mypy .
```

**What You Learned:**
- BatchRunner integrates seamlessly with CI/CD
- Exit code triggers workflow success/failure
- JSON output for artifacts

---

## Example 9: Multi-Step Deployment

**Scenario:** Deploy application to production

**Create deploy-prod.txt:**
```bash
echo "[OK] Step 1/5: Pre-deployment checks..."
curl https://api.example.com/health
echo "[OK] Step 2/5: Stopping services..."
ssh prod "sudo systemctl stop myapp"
echo "[OK] Step 3/5: Deploying code..."
scp -r dist/ prod:/var/www/myapp/
echo "[OK] Step 4/5: Starting services..."
ssh prod "sudo systemctl start myapp"
sleep 10
echo "[OK] Step 5/5: Post-deployment verification..."
curl https://myapp.com/health
echo "[OK] Deployment complete!"
```

**Run:**
```bash
python batchrunner.py -f deploy-prod.txt -l deploy-$(date +%Y%m%d-%H%M%S).log --retries 2
```

**What You Learned:**
- Complex multi-step workflows
- Automatic retry on transient failures
- Timestamped logs for audit

---

## Example 10: Database Operations

**Scenario:** Run database migrations safely

**Create migrate.txt:**
```bash
echo "Backing up database..."
pg_dump mydb > backup_$(date +%Y%m%d).sql
echo "Running migration 001..."
psql mydb < migrations/001_create_tables.sql
echo "Running migration 002..."
psql mydb < migrations/002_add_indexes.sql
echo "Running migration 003..."
psql mydb < migrations/003_alter_columns.sql
echo "Verifying migrations..."
psql mydb -c "SELECT version FROM schema_version;"
echo "Migration complete!"
```

**Run:**
```bash
python batchrunner.py -f migrate.txt -l migrate.log --retries 1 --timeout 120
```

**What You Learned:**
- Database operations with safety
- Backup before migrations
- Retry on transient DB failures
- Timeout protection

---

## Example 11: Error Handling Strategies

**Scenario:** Some commands are expected to fail

**Create mixed-commands.txt:**
```bash
echo "Command 1: Success"
exit 1
echo "Command 3: This still runs!"
```

**Run:**
```bash
python batchrunner.py -f mixed-commands.txt
```

**Expected Output:**
```
Successful: 2
Failed: 1
Success Rate: 66.7%
```

**What You Learned:**
- BatchRunner continues on failure (doesn't abort)
- Summary shows success rate
- Exit code 1 if ANY command failed

---

## Example 12: Performance Testing

**Scenario:** Measure performance of different approaches

**Create perf-sequential.txt:**
```bash
python process.py chunk1
python process.py chunk2
python process.py chunk3
python process.py chunk4
```

**Test Sequential:**
```bash
python batchrunner.py -f perf-sequential.txt -o seq-results.json
```

**Test Parallel:**
```bash
python batchrunner.py -f perf-sequential.txt --parallel -o par-results.json
```

**Compare:**
```bash
python -c "
import json
seq = json.load(open('seq-results.json'))['summary']['total_duration_ms']
par = json.load(open('par-results.json'))['summary']['total_duration_ms']
print(f'Sequential: {seq:.1f}ms')
print(f'Parallel: {par:.1f}ms')
print(f'Speedup: {seq/par:.2f}x')
"
```

**What You Learned:**
- Measure actual performance gains
- JSON output enables analysis
- Parallel isn't always faster

---

## Example 13: Docker Container Management

**Scenario:** Start multiple services in order

**Create start-services.txt:**
```bash
echo "Starting database..."
docker start postgres-db
sleep 5
echo "Starting cache..."
docker start redis-cache
sleep 3
echo "Starting API..."
docker start api-service
sleep 5
echo "Starting worker..."
docker start worker-service
echo "Verifying all services..."
docker ps | grep "Up"
```

**Run:**
```bash
python batchrunner.py -f start-services.txt --retries 2 -l startup.log
```

**What You Learned:**
- Service orchestration
- Health checks with retries
- Dependency management (DB before API)

---

## Example 14: Git Workflow Automation

**Scenario:** Consistent git workflow

**Run:**
```bash
python batchrunner.py -c \
  "git status" \
  "git add ." \
  "git commit -m 'Auto commit: $(date)'" \
  "git push origin main" \
  "git log -1 --oneline"
```

**What You Learned:**
- Automate repetitive git tasks
- Inline commands for quick workflows
- Consistent process every time

---

## Example 15: Real Production Workflow

**Scenario:** Complete build-test-deploy pipeline

**Create pipeline.txt:**
```bash
echo "====== PHASE 1: BUILD ======"
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Linting code..."
python -m black .
python -m isort .
echo "Type checking..."
python -m mypy .
echo "Building package..."
python setup.py sdist bdist_wheel

echo "====== PHASE 2: TEST ======"
echo "Running unit tests..."
python -m pytest tests/unit --cov
echo "Running integration tests..."
python -m pytest tests/integration
echo "Running security scan..."
python -m bandit -r src/

echo "====== PHASE 3: DEPLOY ======"
echo "Uploading to PyPI..."
twine upload dist/*
echo "Tagging release..."
git tag v1.0.0
git push origin v1.0.0
echo "Done!"
```

**Run:**
```bash
python batchrunner.py -f pipeline.txt \
  -l pipeline-$(date +%Y%m%d-%H%M%S).log \
  -o pipeline-results.json \
  --retries 2 \
  --timeout 300
```

**Result:**
- Complete pipeline automation
- Audit trail in log file
- Structured results in JSON
- Automatic retry on transient failures
- Timeout protection per phase

**What You Learned:**
- End-to-end production workflow
- Multiple phases in one batch
- Professional deployment automation
- Complete observability

---

**More examples available at:** https://github.com/DonkRonk17/BatchRunner/tree/main/examples

**Questions?** Open an issue or check `CHEAT_SHEET.txt` for quick reference!
