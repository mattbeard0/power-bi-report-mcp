#!/usr/bin/env python3
"""
Test runner script for Power BI MCP project
"""
import sys
import subprocess
import argparse
from pathlib import Path


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Run Power BI MCP tests")
    parser.add_argument(
        "--cleanup-option",
        choices=["clean", "clean-failures", "keep"],
        default="clean",
        help="Cleanup option: 'clean' (default), 'clean-failures', or 'keep'"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--markers",
        action="store_true",
        help="Show available test markers"
    )
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="Collect tests without running them"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add cleanup option
    cmd.extend(["--cleanup-option", args.cleanup_option])
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=models", "--cov-report=html", "--cov-report=term"])
    
    # Add verbose if requested
    if args.verbose:
        cmd.append("-v")
    
    # Add collect-only if requested
    if args.collect_only:
        cmd.append("--collect-only")
    
    # Add markers if requested
    if args.markers:
        cmd.append("--markers")
    
    # Add test directory
    cmd.append("tests/")
    
    print(f"Running tests with cleanup option: {args.cleanup_option}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        # Run pytest
        result = subprocess.run(cmd, check=True)
        print("-" * 50)
        print("Tests completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print("-" * 50)
        print(f"Tests failed with exit code: {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())



