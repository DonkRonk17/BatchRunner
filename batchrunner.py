#!/usr/bin/env python3
"""
BatchRunner - Parallel Command Executor with Dependency Management

A professional command orchestration tool that executes multiple commands
with intelligent dependency management, parallel execution where possible,
and comprehensive error handling.

Perfect for:
- Build pipelines (compile -> test -> deploy)
- CI/CD automation
- Multi-step deployments
- Test suite execution
- Development workflows

Author: ATLAS (Team Brain)
For: Logan Smith / Metaphy LLC
Version: 1.0
Date: February 9, 2026
License: MIT
"""

import argparse
import json
import subprocess
import sys
import threading
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class CommandResult:
    """Result of a single command execution."""
    
    def __init__(
        self,
        command: str,
        success: bool,
        exit_code: int,
        duration: float,
        stdout: str = "",
        stderr: str = "",
        error: Optional[str] = None
    ):
        self.command = command
        self.success = success
        self.exit_code = exit_code
        self.duration = duration
        self.stdout = stdout
        self.stderr = stderr
        self.error = error
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "command": self.command,
            "success": self.success,
            "exit_code": self.exit_code,
            "duration": self.duration,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "timestamp": self.timestamp
        }


class Command:
    """Represents a single command to execute."""
    
    def __init__(
        self,
        name: str,
        command: str,
        depends_on: Optional[List[str]] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry_count: int = 0,
        retry_delay: int = 1,
        failure_strategy: str = "abort"  # abort, continue, retry
    ):
        self.name = name
        self.command = command
        self.depends_on = depends_on or []
        self.working_dir = working_dir
        self.env = env or {}
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.failure_strategy = failure_strategy
        self.result: Optional[CommandResult] = None


class BatchRunner:
    """
    Parallel command executor with dependency management.
    
    Example:
        >>> runner = BatchRunner()
        >>> runner.add_command("build", "npm run build")
        >>> runner.add_command("test", "npm test", depends_on=["build"])
        >>> results = runner.run()
    """
    
    def __init__(self, verbose: bool = False, dry_run: bool = False):
        """
        Initialize BatchRunner.
        
        Args:
            verbose: Print detailed output
            dry_run: Show what would be executed without running
        """
        self.commands: Dict[str, Command] = {}
        self.verbose = verbose
        self.dry_run = dry_run
        self.results: List[CommandResult] = []
        self.lock = threading.Lock()
    
    def add_command(
        self,
        name: str,
        command: str,
        depends_on: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """
        Add a command to the batch.
        
        Args:
            name: Unique command identifier
            command: Shell command to execute
            depends_on: List of command names this depends on
            **kwargs: Additional command options (working_dir, env, timeout, etc.)
            
        Raises:
            ValueError: If command name already exists
        """
        if name in self.commands:
            raise ValueError(f"Command '{name}' already exists")
        
        self.commands[name] = Command(name, command, depends_on, **kwargs)
    
    def load_from_file(self, filepath: Path) -> None:
        """
        Load batch configuration from JSON or YAML file.
        
        Args:
            filepath: Path to configuration file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'commands' not in data:
            raise ValueError("Configuration must have 'commands' key")
        
        for cmd_data in data['commands']:
            if 'name' not in cmd_data or 'command' not in cmd_data:
                raise ValueError("Each command must have 'name' and 'command'")
            
            self.add_command(**cmd_data)
    
    def validate_dependencies(self) -> Tuple[bool, List[str]]:
        """
        Validate that all dependencies exist and there are no cycles.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check all dependencies exist
        for cmd in self.commands.values():
            for dep in cmd.depends_on:
                if dep not in self.commands:
                    errors.append(
                        f"Command '{cmd.name}' depends on '{dep}' which doesn't exist"
                    )
        
        # Check for circular dependencies
        def has_cycle(name: str, visited: set, stack: set) -> bool:
            visited.add(name)
            stack.add(name)
            
            if name in self.commands:
                for dep in self.commands[name].depends_on:
                    if dep not in visited:
                        if has_cycle(dep, visited, stack):
                            return True
                    elif dep in stack:
                        errors.append(
                            f"Circular dependency detected involving '{name}' and '{dep}'"
                        )
                        return True
            
            stack.remove(name)
            return False
        
        visited = set()
        for cmd_name in self.commands:
            if cmd_name not in visited:
                has_cycle(cmd_name, visited, set())
        
        return (len(errors) == 0, errors)
    
    def _get_execution_order(self) -> List[List[str]]:
        """
        Determine execution order respecting dependencies.
        Returns list of command groups that can run in parallel.
        
        Returns:
            List of lists, where each inner list can execute in parallel
        """
        # Calculate dependency levels
        levels: Dict[str, int] = {}
        
        def get_level(name: str) -> int:
            if name in levels:
                return levels[name]
            
            cmd = self.commands[name]
            if not cmd.depends_on:
                levels[name] = 0
                return 0
            
            max_dep_level = max(get_level(dep) for dep in cmd.depends_on)
            levels[name] = max_dep_level + 1
            return levels[name]
        
        for cmd_name in self.commands:
            get_level(cmd_name)
        
        # Group by level
        max_level = max(levels.values()) if levels else 0
        execution_groups = [[] for _ in range(max_level + 1)]
        
        for cmd_name, level in levels.items():
            execution_groups[level].append(cmd_name)
        
        return execution_groups
    
    def _execute_command(self, cmd: Command) -> CommandResult:
        """
        Execute a single command with retries.
        
        Args:
            cmd: Command to execute
            
        Returns:
            CommandResult with execution details
        """
        if self.verbose:
            print(f"[RUN] {cmd.name}: {cmd.command}")
        
        if self.dry_run:
            return CommandResult(
                command=cmd.command,
                success=True,
                exit_code=0,
                duration=0.0,
                stdout="[DRY RUN - not executed]",
                stderr=""
            )
        
        attempts = 0
        max_attempts = cmd.retry_count + 1
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                start_time = time.time()
                
                # Build environment
                env = None
                if cmd.env:
                    import os
                    env = os.environ.copy()
                    env.update(cmd.env)
                
                # Execute command
                process = subprocess.run(
                    cmd.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=cmd.working_dir,
                    env=env,
                    timeout=cmd.timeout
                )
                
                duration = time.time() - start_time
                success = process.returncode == 0
                
                result = CommandResult(
                    command=cmd.command,
                    success=success,
                    exit_code=process.returncode,
                    duration=duration,
                    stdout=process.stdout,
                    stderr=process.stderr
                )
                
                if success or attempts >= max_attempts:
                    return result
                
                # Retry on failure
                if self.verbose:
                    print(
                        f"[RETRY] {cmd.name} failed "
                        f"(attempt {attempts}/{max_attempts}), "
                        f"retrying in {cmd.retry_delay}s..."
                    )
                time.sleep(cmd.retry_delay)
                
            except subprocess.TimeoutExpired:
                duration = time.time() - start_time
                return CommandResult(
                    command=cmd.command,
                    success=False,
                    exit_code=-1,
                    duration=duration,
                    error=f"Timeout after {cmd.timeout}s"
                )
            except Exception as e:
                duration = time.time() - start_time
                return CommandResult(
                    command=cmd.command,
                    success=False,
                    exit_code=-1,
                    duration=duration,
                    error=str(e)
                )
        
        # Should never reach here
        return CommandResult(
            command=cmd.command,
            success=False,
            exit_code=-1,
            duration=0.0,
            error="Unknown error"
        )
    
    def _execute_group(
        self,
        group: List[str],
        abort_on_failure: bool = True
    ) -> Tuple[bool, List[CommandResult]]:
        """
        Execute a group of commands in parallel.
        
        Args:
            group: List of command names to execute
            abort_on_failure: Stop all if any fails
            
        Returns:
            Tuple of (all_success, results_list)
        """
        results = []
        threads = []
        failed = threading.Event()
        
        def run_command(cmd_name: str) -> None:
            if abort_on_failure and failed.is_set():
                return
            
            cmd = self.commands[cmd_name]
            result = self._execute_command(cmd)
            
            with self.lock:
                results.append(result)
                cmd.result = result
                
                if not result.success:
                    failed.set()
                    if cmd.failure_strategy == "abort":
                        if self.verbose:
                            print(f"[ABORT] {cmd_name} failed, aborting batch")
        
        # Start all threads
        for cmd_name in group:
            thread = threading.Thread(target=run_command, args=(cmd_name,))
            thread.start()
            threads.append(thread)
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        all_success = all(r.success for r in results)
        return (all_success, results)
    
    def run(self, abort_on_failure: bool = True) -> Dict[str, Any]:
        """
        Execute all commands respecting dependencies.
        
        Args:
            abort_on_failure: Stop execution if any command fails
            
        Returns:
            Dictionary with execution summary
        """
        # Validate
        is_valid, errors = self.validate_dependencies()
        if not is_valid:
            return {
                "success": False,
                "error": "Validation failed",
                "errors": errors
            }
        
        if self.verbose:
            print("[OK] Dependency validation passed")
        
        # Get execution order
        execution_groups = self._get_execution_order()
        
        if self.verbose:
            print(f"[OK] Execution plan: {len(execution_groups)} groups")
            for i, group in enumerate(execution_groups):
                print(f"  Group {i+1}: {', '.join(group)}")
        
        # Execute groups sequentially, commands within group in parallel
        start_time = time.time()
        all_results = []
        
        for i, group in enumerate(execution_groups):
            if self.verbose:
                print(f"\n[GROUP {i+1}] Executing {len(group)} commands...")
            
            group_success, group_results = self._execute_group(
                group,
                abort_on_failure
            )
            all_results.extend(group_results)
            
            if not group_success and abort_on_failure:
                if self.verbose:
                    print("[ABORT] Stopping execution due to failure")
                break
        
        total_duration = time.time() - start_time
        
        # Build summary
        successful = sum(1 for r in all_results if r.success)
        failed = len(all_results) - successful
        
        summary = {
            "success": failed == 0,
            "total_commands": len(self.commands),
            "executed": len(all_results),
            "successful": successful,
            "failed": failed,
            "duration": total_duration,
            "results": [r.to_dict() for r in all_results]
        }
        
        self.results = all_results
        return summary
    
    def generate_report(self, format: str = "text") -> str:
        """
        Generate execution report.
        
        Args:
            format: Output format (text, json, markdown)
            
        Returns:
            Formatted report string
        """
        if not self.results:
            return "No results available. Run batch first."
        
        if format == "json":
            return json.dumps(
                {"results": [r.to_dict() for r in self.results]},
                indent=2
            )
        
        elif format == "markdown":
            lines = ["# BatchRunner Execution Report\n"]
            lines.append(f"**Executed:** {datetime.now().isoformat()}\n")
            lines.append(f"**Total Commands:** {len(self.results)}\n")
            
            successful = sum(1 for r in self.results if r.success)
            lines.append(f"**Successful:** {successful}\n")
            lines.append(f"**Failed:** {len(self.results) - successful}\n\n")
            
            lines.append("## Commands\n")
            for r in self.results:
                status = "[OK]" if r.success else "[FAIL]"
                lines.append(f"### {status} {r.command}\n")
                lines.append(f"- **Exit Code:** {r.exit_code}\n")
                lines.append(f"- **Duration:** {r.duration:.2f}s\n")
                if r.error:
                    lines.append(f"- **Error:** {r.error}\n")
                lines.append("\n")
            
            return "".join(lines)
        
        else:  # text
            lines = []
            lines.append("=" * 70)
            lines.append("BATCHRUNNER EXECUTION REPORT")
            lines.append("=" * 70)
            
            successful = sum(1 for r in self.results if r.success)
            failed = len(self.results) - successful
            
            lines.append(f"Total Commands: {len(self.results)}")
            lines.append(f"Successful: {successful}")
            lines.append(f"Failed: {failed}")
            lines.append("")
            
            for r in self.results:
                status = "[OK]" if r.success else "[FAIL]"
                lines.append(f"{status} {r.command}")
                lines.append(f"  Exit Code: {r.exit_code}")
                lines.append(f"  Duration: {r.duration:.2f}s")
                if r.error:
                    lines.append(f"  Error: {r.error}")
                if r.stdout and self.verbose:
                    lines.append(f"  Output: {r.stdout[:200]}")
                lines.append("")
            
            lines.append("=" * 70)
            return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='BatchRunner - Parallel command executor with dependency management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute from config file
  batchrunner run batch.json
  
  # Dry run (show what would execute)
  batchrunner run batch.json --dry-run
  
  # Continue on failure
  batchrunner run batch.json --continue-on-failure
  
  # Generate report
  batchrunner report --format markdown

For more information: https://github.com/DonkRonk17/BatchRunner
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # run command
    run_parser = subparsers.add_parser('run', help='Execute batch')
    run_parser.add_argument('config', type=str, help='Path to batch configuration file')
    run_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    run_parser.add_argument('--dry-run', action='store_true', help='Show what would execute')
    run_parser.add_argument('--continue-on-failure', action='store_true',
                           help='Continue execution even if commands fail')
    run_parser.add_argument('--report', type=str, choices=['text', 'json', 'markdown'],
                           help='Generate report after execution')
    
    # validate command
    validate_parser = subparsers.add_parser('validate', help='Validate batch configuration')
    validate_parser.add_argument('config', type=str, help='Path to batch configuration file')
    
    # version command
    parser.add_argument('--version', action='version', version='BatchRunner 1.0')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'run':
            runner = BatchRunner(verbose=args.verbose, dry_run=args.dry_run)
            runner.load_from_file(Path(args.config))
            
            result = runner.run(abort_on_failure=not args.continue_on_failure)
            
            if args.verbose or args.report:
                format = args.report if args.report else 'text'
                print(runner.generate_report(format))
            
            return 0 if result['success'] else 1
        
        elif args.command == 'validate':
            runner = BatchRunner()
            runner.load_from_file(Path(args.config))
            
            is_valid, errors = runner.validate_dependencies()
            if is_valid:
                print("[OK] Configuration is valid")
                return 0
            else:
                print("[FAIL] Configuration validation failed:")
                for error in errors:
                    print(f"  - {error}")
                return 1
    
    except FileNotFoundError as e:
        print(f"[X] Error: {e}")
        return 1
    except Exception as e:
        print(f"[X] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
