#!/usr/bin/env python3
"""
BatchRunner - Command Batch Orchestration Made Simple

A professional CLI tool for running multiple commands with proper logging,
error handling, progress tracking, and performance metrics. Supports both
sequential and parallel execution modes.

Perfect for build scripts, testing suites, deployment pipelines, and any
scenario where you need to orchestrate multiple commands reliably.

Author: ATLAS (Team Brain)
For: Logan Smith / Metaphy LLC
Version: 1.0
Date: February 13, 2026
License: MIT
"""

import argparse
import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed


class CommandResult:
    """Represents the result of a command execution."""
    
    def __init__(
        self,
        command: str,
        success: bool,
        exit_code: int,
        stdout: str,
        stderr: str,
        duration_ms: float,
        timestamp: str
    ):
        self.command = command
        self.success = success
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.timestamp = timestamp
    
    def to_dict(self) -> dict:
        """Convert result to dictionary for JSON serialization."""
        return {
            "command": self.command,
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp
        }


class BatchRunner:
    """
    Main batch runner for orchestrating command execution.
    
    Features:
    - Sequential or parallel execution
    - Automatic retry on failure
    - Progress tracking and logging
    - Performance metrics
    - Cross-platform support
    """
    
    def __init__(
        self,
        commands: List[str],
        mode: str = "sequential",
        max_retries: int = 0,
        retry_delay_sec: float = 1.0,
        timeout_sec: Optional[float] = None,
        log_file: Optional[Path] = None,
        verbose: bool = True
    ):
        """
        Initialize BatchRunner.
        
        Args:
            commands: List of commands to execute
            mode: Execution mode ("sequential" or "parallel")
            max_retries: Number of retry attempts on failure
            retry_delay_sec: Delay between retries
            timeout_sec: Timeout per command (None = no timeout)
            log_file: Path to log file (None = no file logging)
            verbose: Print progress to console
        """
        self.commands = commands
        self.mode = mode
        self.max_retries = max_retries
        self.retry_delay_sec = retry_delay_sec
        self.timeout_sec = timeout_sec
        self.log_file = log_file
        self.verbose = verbose
        
        self.results: List[CommandResult] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def _log(self, message: str, level: str = "INFO"):
        """Log a message to console and/or file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        
        if self.verbose:
            print(log_line)
        
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
    
    def _execute_command(self, command: str, attempt: int = 1) -> CommandResult:
        """
        Execute a single command with retry logic.
        
        Args:
            command: Command to execute
            attempt: Current attempt number
            
        Returns:
            CommandResult object
        """
        self._log(f"Executing: {command} (attempt {attempt}/{self.max_retries + 1})")
        
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            success = result.returncode == 0
            
            cmd_result = CommandResult(
                command=command,
                success=success,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_ms=duration_ms,
                timestamp=timestamp
            )
            
            if success:
                self._log(f"[OK] Command completed ({duration_ms:.1f}ms)", "SUCCESS")
            else:
                self._log(
                    f"[X] Command failed (exit code {result.returncode})",
                    "ERROR"
                )
                if result.stderr:
                    self._log(f"Error output: {result.stderr.strip()}", "ERROR")
            
            # Retry logic
            if not success and attempt <= self.max_retries:
                self._log(f"Retrying in {self.retry_delay_sec}s...")
                time.sleep(self.retry_delay_sec)
                return self._execute_command(command, attempt + 1)
            
            return cmd_result
            
        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            self._log(f"[X] Command timed out after {self.timeout_sec}s", "ERROR")
            
            cmd_result = CommandResult(
                command=command,
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {self.timeout_sec} seconds",
                duration_ms=duration_ms,
                timestamp=timestamp
            )
            
            # Retry on timeout
            if attempt <= self.max_retries:
                self._log(f"Retrying in {self.retry_delay_sec}s...")
                time.sleep(self.retry_delay_sec)
                return self._execute_command(command, attempt + 1)
            
            return cmd_result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._log(f"[X] Unexpected error: {str(e)}", "ERROR")
            
            return CommandResult(
                command=command,
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_ms=duration_ms,
                timestamp=timestamp
            )
    
    def run(self) -> Tuple[List[CommandResult], Dict]:
        """
        Execute all commands according to the configured mode.
        
        Returns:
            Tuple of (results list, summary dict)
        """
        self.start_time = time.time()
        
        self._log("=" * 70)
        self._log(f"BatchRunner v1.0 - Starting {len(self.commands)} commands")
        self._log(f"Mode: {self.mode}")
        self._log(f"Retries: {self.max_retries}")
        if self.timeout_sec:
            self._log(f"Timeout: {self.timeout_sec}s per command")
        self._log("=" * 70)
        
        if self.mode == "sequential":
            self._run_sequential()
        elif self.mode == "parallel":
            self._run_parallel()
        else:
            raise ValueError(f"Invalid mode: {self.mode}")
        
        self.end_time = time.time()
        
        summary = self._generate_summary()
        self._print_summary(summary)
        
        return self.results, summary
    
    def _run_sequential(self):
        """Execute commands sequentially."""
        for idx, command in enumerate(self.commands, 1):
            self._log(f"\n[{idx}/{len(self.commands)}] Starting command...")
            result = self._execute_command(command)
            self.results.append(result)
    
    def _run_parallel(self):
        """Execute commands in parallel."""
        max_workers = min(len(self.commands), 10)  # Cap at 10 parallel workers
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_cmd = {
                executor.submit(self._execute_command, cmd): cmd
                for cmd in self.commands
            }
            
            completed = 0
            for future in as_completed(future_to_cmd):
                result = future.result()
                self.results.append(result)
                completed += 1
                self._log(f"Progress: {completed}/{len(self.commands)} completed")
    
    def _generate_summary(self) -> Dict:
        """Generate execution summary statistics."""
        total_duration_ms = (self.end_time - self.start_time) * 1000
        
        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful
        
        avg_duration = sum(r.duration_ms for r in self.results) / len(self.results)
        min_duration = min(r.duration_ms for r in self.results)
        max_duration = max(r.duration_ms for r in self.results)
        
        return {
            "total_commands": len(self.commands),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / len(self.commands)) * 100,
            "total_duration_ms": total_duration_ms,
            "avg_command_duration_ms": avg_duration,
            "min_command_duration_ms": min_duration,
            "max_command_duration_ms": max_duration,
            "mode": self.mode,
            "max_retries": self.max_retries
        }
    
    def _print_summary(self, summary: Dict):
        """Print execution summary to console."""
        self._log("\n" + "=" * 70)
        self._log("EXECUTION SUMMARY")
        self._log("=" * 70)
        self._log(f"Total Commands: {summary['total_commands']}")
        self._log(f"Successful: {summary['successful']}")
        self._log(f"Failed: {summary['failed']}")
        self._log(f"Success Rate: {summary['success_rate']:.1f}%")
        self._log(f"Total Duration: {summary['total_duration_ms']:.1f}ms")
        self._log(f"Avg Command Duration: {summary['avg_command_duration_ms']:.1f}ms")
        self._log(f"Min Command Duration: {summary['min_command_duration_ms']:.1f}ms")
        self._log(f"Max Command Duration: {summary['max_command_duration_ms']:.1f}ms")
        self._log("=" * 70)
        
        if summary['failed'] > 0:
            self._log("\nFailed commands:")
            for result in self.results:
                if not result.success:
                    self._log(f"  - {result.command}")
                    if result.stderr:
                        self._log(f"    Error: {result.stderr[:100]}")
    
    def save_results(self, output_file: Path):
        """Save results to JSON file."""
        data = {
            "summary": self._generate_summary(),
            "results": [r.to_dict() for r in self.results]
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        self._log(f"\nResults saved to: {output_file}")


def load_commands_from_file(file_path: Path) -> List[str]:
    """
    Load commands from a text file (one command per line).
    
    Args:
        file_path: Path to commands file
        
    Returns:
        List of commands
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Commands file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        commands = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]
    
    if not commands:
        raise ValueError(f"No commands found in {file_path}")
    
    return commands


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="BatchRunner - Command Batch Orchestration Made Simple",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run commands from file sequentially
  python batchrunner.py -f commands.txt
  
  # Run commands in parallel
  python batchrunner.py -f commands.txt --parallel
  
  # With retries and timeout
  python batchrunner.py -f commands.txt --retries 2 --timeout 30
  
  # Run inline commands
  python batchrunner.py -c "echo Hello" "echo World" "dir"
  
  # Save results to JSON
  python batchrunner.py -f commands.txt -o results.json

For more information: https://github.com/DonkRonk17/BatchRunner
        """
    )
    
    # Input source (file or inline)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-f", "--file",
        type=Path,
        help="Path to file containing commands (one per line)"
    )
    input_group.add_argument(
        "-c", "--commands",
        nargs="+",
        help="Commands to execute (inline)"
    )
    
    # Execution mode
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Execute commands in parallel (default: sequential)"
    )
    
    # Retry options
    parser.add_argument(
        "--retries",
        type=int,
        default=0,
        help="Number of retry attempts on failure (default: 0)"
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=1.0,
        help="Delay between retries in seconds (default: 1.0)"
    )
    
    # Timeout
    parser.add_argument(
        "--timeout",
        type=float,
        help="Timeout per command in seconds (default: no timeout)"
    )
    
    # Logging
    parser.add_argument(
        "-l", "--log",
        type=Path,
        help="Path to log file (default: no file logging)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress console output (quiet mode)"
    )
    
    # Output
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Save results to JSON file"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="BatchRunner v1.0"
    )
    
    args = parser.parse_args()
    
    # Load commands
    try:
        if args.file:
            commands = load_commands_from_file(args.file)
        else:
            commands = args.commands
        
        if not commands:
            print("[X] Error: No commands to execute")
            return 1
        
        # Create runner
        mode = "parallel" if args.parallel else "sequential"
        
        runner = BatchRunner(
            commands=commands,
            mode=mode,
            max_retries=args.retries,
            retry_delay_sec=args.retry_delay,
            timeout_sec=args.timeout,
            log_file=args.log,
            verbose=not args.quiet
        )
        
        # Execute
        results, summary = runner.run()
        
        # Save results if requested
        if args.output:
            runner.save_results(args.output)
        
        # Exit with appropriate code
        if summary['failed'] > 0:
            return 1
        else:
            return 0
        
    except FileNotFoundError as e:
        print(f"[X] Error: {e}")
        return 1
    except ValueError as e:
        print(f"[X] Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        return 130
    except Exception as e:
        print(f"[X] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
