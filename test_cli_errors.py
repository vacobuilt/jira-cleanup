#!/usr/bin/env python3
"""
Simple test script to verify CLI error handling and edge cases.
This helps validate our Rich error formatting and Typer CLI robustness.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_cli_command(cmd_args, expect_error=False):
    """Run a CLI command and capture output."""
    try:
        # Set up environment
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{Path.cwd() / 'src'}:{env.get('PYTHONPATH', '')}"
        
        # Run command
        result = subprocess.run(
            ["python", "-m", "jiraclean.cli.main"] + cmd_args,
            capture_output=True,
            text=True,
            env=env,
            cwd=Path.cwd()
        )
        
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    except Exception as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False,
            "exception": e
        }

def test_help_commands():
    """Test help commands work correctly."""
    print("🧪 Testing help commands...")
    
    # Test main help
    result = run_cli_command(["--help"])
    assert result["success"], f"Main help failed: {result['stderr']}"
    assert "Jira Cleanup" in result["stdout"], "Help should contain app description"
    print("  ✅ Main help works")
    
    # Test command help
    result = run_cli_command(["main-command", "--help"])
    assert result["success"], f"Command help failed: {result['stderr']}"
    assert "Process Jira tickets" in result["stdout"], "Command help should contain description"
    print("  ✅ Command help works")

def test_invalid_options():
    """Test handling of invalid command line options."""
    print("🧪 Testing invalid options...")
    
    # Test invalid command
    result = run_cli_command(["invalid-command"], expect_error=True)
    assert not result["success"], "Invalid command should fail"
    print("  ✅ Invalid command properly rejected")
    
    # Test invalid option
    result = run_cli_command(["main-command", "--invalid-option"], expect_error=True)
    assert not result["success"], "Invalid option should fail"
    print("  ✅ Invalid option properly rejected")

def test_config_commands():
    """Test configuration commands."""
    print("🧪 Testing config commands...")
    
    # Test config list (should work even without real config)
    result = run_cli_command(["config", "list"])
    # This might succeed or fail depending on config, but shouldn't crash
    print(f"  ℹ️  Config list result: {result['returncode']}")
    
    # Test config help
    result = run_cli_command(["config", "--help"])
    assert result["success"], f"Config help failed: {result['stderr']}"
    print("  ✅ Config help works")

def test_setup_command():
    """Test setup command."""
    print("🧪 Testing setup command...")
    
    # Test setup help
    result = run_cli_command(["setup", "--help"])
    assert result["success"], f"Setup help failed: {result['stderr']}"
    print("  ✅ Setup help works")

def main():
    """Run all tests."""
    print("🚀 Starting CLI Error and Edge Case Testing")
    print("=" * 50)
    
    try:
        test_help_commands()
        test_invalid_options()
        test_config_commands()
        test_setup_command()
        
        print("=" * 50)
        print("✅ All CLI tests passed!")
        return 0
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
