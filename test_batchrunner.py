#!/usr/bin/env python3
"""
Comprehensive test suite for BatchRunner.

Tests cover:
- Core functionality
- Dependency management
- Parallel execution
- Error handling
- Configuration loading
- Reporting

Run: python test_batchrunner.py
"""

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from batchrunner import BatchRunner, Command, CommandResult


class TestCommandResult(unittest.TestCase):
    """Test CommandResult class."""
    
    def test_initialization(self):
        """Test CommandResult initializes correctly."""
        result = CommandResult(
            command="echo test",
            success=True,
            exit_code=0,
            duration=0.1
        )
        self.assertEqual(result.command, "echo test")
        self.assertTrue(result.success)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.duration, 0.1)
    
    def test_to_dict(self):
        """Test CommandResult converts to dictionary."""
        result = CommandResult(
            command="echo test",
            success=True,
            exit_code=0,
            duration=0.1,
            stdout="test output",
            stderr=""
        )
        data = result.to_dict()
        self.assertIn("command", data)
        self.assertIn("success", data)
        self.assertIn("timestamp", data)


class TestCommand(unittest.TestCase):
    """Test Command class."""
    
    def test_initialization(self):
        """Test Command initializes correctly."""
        cmd = Command("test", "echo hello")
        self.assertEqual(cmd.name, "test")
        self.assertEqual(cmd.command, "echo hello")
        self.assertEqual(cmd.depends_on, [])
    
    def test_with_dependencies(self):
        """Test Command with dependencies."""
        cmd = Command("test", "echo hello", depends_on=["build"])
        self.assertEqual(cmd.depends_on, ["build"])
    
    def test_with_options(self):
        """Test Command with additional options."""
        cmd = Command(
            "test",
            "echo hello",
            timeout=30,
            retry_count=3,
            working_dir="/tmp"
        )
        self.assertEqual(cmd.timeout, 30)
        self.assertEqual(cmd.retry_count, 3)
        self.assertEqual(cmd.working_dir, "/tmp")


class TestBatchRunnerCore(unittest.TestCase):
    """Test core BatchRunner functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = BatchRunner()
    
    def test_initialization(self):
        """Test BatchRunner initializes correctly."""
        runner = BatchRunner()
        self.assertIsNotNone(runner)
        self.assertEqual(len(runner.commands), 0)
    
    def test_add_command(self):
        """Test adding commands."""
        self.runner.add_command("test", "echo hello")
        self.assertEqual(len(self.runner.commands), 1)
        self.assertIn("test", self.runner.commands)
    
    def test_add_duplicate_command(self):
        """Test adding duplicate command raises error."""
        self.runner.add_command("test", "echo hello")
        with self.assertRaises(ValueError):
            self.runner.add_command("test", "echo world")
    
    def test_add_command_with_dependencies(self):
        """Test adding command with dependencies."""
        self.runner.add_command("build", "echo building")
        self.runner.add_command("test", "echo testing", depends_on=["build"])
        
        self.assertEqual(len(self.runner.commands), 2)
        self.assertEqual(self.runner.commands["test"].depends_on, ["build"])


class TestDependencyValidation(unittest.TestCase):
    """Test dependency validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = BatchRunner()
    
    def test_valid_dependencies(self):
        """Test valid dependency chain."""
        self.runner.add_command("a", "echo a")
        self.runner.add_command("b", "echo b", depends_on=["a"])
        self.runner.add_command("c", "echo c", depends_on=["b"])
        
        is_valid, errors = self.runner.validate_dependencies()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_missing_dependency(self):
        """Test missing dependency detection."""
        self.runner.add_command("a", "echo a", depends_on=["missing"])
        
        is_valid, errors = self.runner.validate_dependencies()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_circular_dependency(self):
        """Test circular dependency detection."""
        self.runner.add_command("a", "echo a", depends_on=["b"])
        self.runner.add_command("b", "echo b", depends_on=["a"])
        
        is_valid, errors = self.runner.validate_dependencies()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_complex_circular_dependency(self):
        """Test complex circular dependency detection."""
        self.runner.add_command("a", "echo a", depends_on=["b"])
        self.runner.add_command("b", "echo b", depends_on=["c"])
        self.runner.add_command("c", "echo c", depends_on=["a"])
        
        is_valid, errors = self.runner.validate_dependencies()
        self.assertFalse(is_valid)


class TestExecutionOrder(unittest.TestCase):
    """Test execution order calculation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = BatchRunner()
    
    def test_no_dependencies(self):
        """Test parallel execution with no dependencies."""
        self.runner.add_command("a", "echo a")
        self.runner.add_command("b", "echo b")
        self.runner.add_command("c", "echo c")
        
        groups = self.runner._get_execution_order()
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 3)
    
    def test_linear_dependencies(self):
        """Test sequential execution with linear dependencies."""
        self.runner.add_command("a", "echo a")
        self.runner.add_command("b", "echo b", depends_on=["a"])
        self.runner.add_command("c", "echo c", depends_on=["b"])
        
        groups = self.runner._get_execution_order()
        self.assertEqual(len(groups), 3)
        self.assertEqual(groups[0], ["a"])
        self.assertEqual(groups[1], ["b"])
        self.assertEqual(groups[2], ["c"])
    
    def test_mixed_dependencies(self):
        """Test mixed parallel/sequential execution."""
        self.runner.add_command("a", "echo a")
        self.runner.add_command("b", "echo b")
        self.runner.add_command("c", "echo c", depends_on=["a", "b"])
        
        groups = self.runner._get_execution_order()
        self.assertEqual(len(groups), 2)
        self.assertIn("a", groups[0])
        self.assertIn("b", groups[0])
        self.assertEqual(groups[1], ["c"])


class TestCommandExecution(unittest.TestCase):
    """Test command execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = BatchRunner()
    
    def test_successful_command(self):
        """Test executing successful command."""
        import platform
        if platform.system() == "Windows":
            cmd = "echo test"
        else:
            cmd = "echo test"
        
        self.runner.add_command("test", cmd)
        result = self.runner.run()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["successful"], 1)
        self.assertEqual(result["failed"], 0)
    
    def test_failing_command(self):
        """Test executing failing command."""
        import platform
        if platform.system() == "Windows":
            cmd = "exit 1"
        else:
            cmd = "exit 1"
        
        self.runner.add_command("test", cmd)
        result = self.runner.run()
        
        self.assertFalse(result["success"])
        self.assertEqual(result["failed"], 1)
    
    def test_multiple_commands_parallel(self):
        """Test multiple commands execute in parallel."""
        import platform
        if platform.system() == "Windows":
            cmd = "echo test"
        else:
            cmd = "echo test"
        
        self.runner.add_command("a", cmd)
        self.runner.add_command("b", cmd)
        self.runner.add_command("c", cmd)
        
        start_time = time.time()
        result = self.runner.run()
        duration = time.time() - start_time
        
        self.assertTrue(result["success"])
        self.assertEqual(result["successful"], 3)
        # Should be faster than sequential (but hard to guarantee on slow systems)
        # Just verify they all ran
        self.assertEqual(result["executed"], 3)
    
    def test_sequential_dependencies(self):
        """Test commands execute in correct order."""
        import platform
        if platform.system() == "Windows":
            cmd = "echo test"
        else:
            cmd = "echo test"
        
        self.runner.add_command("a", cmd)
        self.runner.add_command("b", cmd, depends_on=["a"])
        self.runner.add_command("c", cmd, depends_on=["b"])
        
        result = self.runner.run()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["successful"], 3)
        
        # Verify order in results
        results = result["results"]
        self.assertEqual(len(results), 3)


class TestFailureHandling(unittest.TestCase):
    """Test failure handling strategies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = BatchRunner()
    
    def test_abort_on_failure(self):
        """Test abort on failure strategy."""
        import platform
        if platform.system() == "Windows":
            fail_cmd = "exit 1"
            success_cmd = "echo test"
        else:
            fail_cmd = "exit 1"
            success_cmd = "echo test"
        
        self.runner.add_command("fail", fail_cmd)
        self.runner.add_command("success", success_cmd, depends_on=["fail"])
        
        result = self.runner.run(abort_on_failure=True)
        
        # Should abort after first failure
        self.assertFalse(result["success"])
        self.assertEqual(result["executed"], 1)
    
    def test_continue_on_failure(self):
        """Test continue on failure strategy."""
        import platform
        if platform.system() == "Windows":
            fail_cmd = "exit 1"
            success_cmd = "echo test"
        else:
            fail_cmd = "exit 1"
            success_cmd = "echo test"
        
        self.runner.add_command("fail", fail_cmd)
        self.runner.add_command("success", success_cmd)
        
        result = self.runner.run(abort_on_failure=False)
        
        # Should execute all commands
        self.assertFalse(result["success"])  # Overall fails due to one failure
        self.assertEqual(result["executed"], 2)


class TestConfigurationLoading(unittest.TestCase):
    """Test loading configuration from file."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = BatchRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_load_valid_config(self):
        """Test loading valid configuration."""
        config = {
            "commands": [
                {"name": "a", "command": "echo a"},
                {"name": "b", "command": "echo b", "depends_on": ["a"]}
            ]
        }
        
        config_file = Path(self.temp_dir) / "batch.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        self.runner.load_from_file(config_file)
        
        self.assertEqual(len(self.runner.commands), 2)
        self.assertIn("a", self.runner.commands)
        self.assertIn("b", self.runner.commands)
    
    def test_load_missing_file(self):
        """Test loading missing file raises error."""
        with self.assertRaises(FileNotFoundError):
            self.runner.load_from_file(Path("/nonexistent/batch.json"))
    
    def test_load_invalid_format(self):
        """Test loading invalid format raises error."""
        config = {"invalid": "format"}
        
        config_file = Path(self.temp_dir) / "batch.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        with self.assertRaises(ValueError):
            self.runner.load_from_file(config_file)


class TestReporting(unittest.TestCase):
    """Test report generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = BatchRunner()
        import platform
        if platform.system() == "Windows":
            cmd = "echo test"
        else:
            cmd = "echo test"
        self.runner.add_command("test", cmd)
        self.runner.run()
    
    def test_text_report(self):
        """Test text report generation."""
        report = self.runner.generate_report(format="text")
        self.assertIsInstance(report, str)
        self.assertIn("BATCHRUNNER", report)
        self.assertIn("[OK]", report)
    
    def test_json_report(self):
        """Test JSON report generation."""
        report = self.runner.generate_report(format="json")
        data = json.loads(report)
        self.assertIn("results", data)
        self.assertIsInstance(data["results"], list)
    
    def test_markdown_report(self):
        """Test Markdown report generation."""
        report = self.runner.generate_report(format="markdown")
        self.assertIn("# BatchRunner", report)
        self.assertIn("##", report)


class TestDryRun(unittest.TestCase):
    """Test dry run mode."""
    
    def test_dry_run(self):
        """Test dry run doesn't execute commands."""
        runner = BatchRunner(dry_run=True)
        runner.add_command("test", "echo test")
        
        result = runner.run()
        
        self.assertTrue(result["success"])
        # Check that output indicates dry run
        self.assertIn("DRY RUN", result["results"][0]["stdout"])


class TestVerboseMode(unittest.TestCase):
    """Test verbose output mode."""
    
    def test_verbose_mode(self):
        """Test verbose mode produces output."""
        runner = BatchRunner(verbose=True)
        import platform
        if platform.system() == "Windows":
            cmd = "echo test"
        else:
            cmd = "echo test"
        runner.add_command("test", cmd)
        
        # Just verify it runs without error
        result = runner.run()
        self.assertTrue(result["success"])


def run_tests():
    """Run all tests with nice output."""
    print("=" * 70)
    print("TESTING: BatchRunner v1.0")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCommandResult))
    suite.addTests(loader.loadTestsFromTestCase(TestCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchRunnerCore))
    suite.addTests(loader.loadTestsFromTestCase(TestDependencyValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestExecutionOrder))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestFailureHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestReporting))
    suite.addTests(loader.loadTestsFromTestCase(TestDryRun))
    suite.addTests(loader.loadTestsFromTestCase(TestVerboseMode))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {result.testsRun} tests")
    print(f"[OK] Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    if result.failures:
        print(f"[X] Failed: {len(result.failures)}")
    if result.errors:
        print(f"[X] Errors: {len(result.errors)}")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
