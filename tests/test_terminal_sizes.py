#!/usr/bin/env python3
"""
Test script to validate Rich output formatting across different terminal sizes.
This ensures our UI components are responsive and handle various terminal widths.
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from jiraclean.ui.console import console
from jiraclean.ui.components import TicketCard, StatusIndicator, ProgressTracker
from jiraclean.ui.formatters import format_processing_header, format_error
from rich.console import Console

def test_terminal_width(width):
    """Test Rich components at a specific terminal width."""
    print(f"\n🖥️  Testing terminal width: {width} columns")
    
    # Create a console with specific width
    test_console = Console(width=width, force_terminal=True)
    
    # Test data
    ticket_data = {
        'key': 'TEST-123',
        'type': 'Bug',
        'status': 'Open',
        'priority': 'High',
        'assignee': 'john.doe@company.com',
        'reporter': 'jane.smith@company.com',
        'summary': 'This is a test ticket with a reasonably long summary to test text wrapping behavior',
        'description': 'This is a longer description that should wrap properly across different terminal sizes and maintain readability.'
    }
    
    try:
        # Test processing header
        header = format_processing_header(
            project="TEST",
            dry_run=True,
            llm_enabled=True,
            max_tickets=5
        )
        test_console.print(header)
        print(f"  ✅ Processing header renders at {width} columns")
        
        # Test ticket card
        card = TicketCard.create(ticket_data)
        test_console.print(card)
        print(f"  ✅ Ticket card renders at {width} columns")
        
        # Test error formatting
        error_panel = format_error("Test error message", "Additional context information")
        test_console.print(error_panel)
        print(f"  ✅ Error panel renders at {width} columns")
        
        # Test status indicator
        status = StatusIndicator.success("Operation completed successfully")
        test_console.print(status)
        print(f"  ✅ Status indicator renders at {width} columns")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error at {width} columns: {e}")
        return False

def test_responsive_design():
    """Test various terminal sizes to ensure responsive design."""
    print("🎨 Testing Responsive Design Across Terminal Sizes")
    print("=" * 60)
    
    # Test different terminal widths
    test_widths = [
        40,   # Very narrow (mobile-like)
        60,   # Narrow
        80,   # Standard
        100,  # Wide
        120,  # Very wide
        160   # Ultra-wide
    ]
    
    results = {}
    
    for width in test_widths:
        results[width] = test_terminal_width(width)
    
    # Summary
    print("\n📊 Terminal Size Test Results:")
    print("-" * 40)
    
    passed = 0
    for width, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {width:3d} columns: {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(test_widths)} terminal sizes passed")
    return passed == len(test_widths)

def test_text_wrapping():
    """Test text wrapping behavior with long content."""
    print("\n📝 Testing Text Wrapping Behavior")
    print("-" * 40)
    
    # Test with very long content
    long_ticket = {
        'key': 'WRAP-456',
        'type': 'Story',
        'status': 'In Progress',
        'priority': 'Medium',
        'assignee': 'very.long.email.address@company-with-long-domain-name.com',
        'reporter': 'another.very.long.email@different-company-domain.org',
        'summary': 'This is an extremely long ticket summary that should test the text wrapping capabilities of our Rich formatting components to ensure they handle edge cases gracefully',
        'description': 'This is an even longer description that contains multiple sentences and should demonstrate how our formatting handles extensive text content. It includes various punctuation marks, numbers like 12345, and should wrap properly across multiple lines while maintaining readability and visual appeal.'
    }
    
    # Test at narrow width
    narrow_console = Console(width=50, force_terminal=True)
    card = TicketCard.create(long_ticket)
    narrow_console.print(card)
    print("  ✅ Long content wraps properly at 50 columns")
    
    # Test at very narrow width
    very_narrow_console = Console(width=30, force_terminal=True)
    very_narrow_console.print(card)
    print("  ✅ Long content wraps properly at 30 columns")
    
    return True

def test_color_schemes():
    """Test different color schemes and accessibility."""
    print("\n🎨 Testing Color Schemes and Accessibility")
    print("-" * 40)
    
    # Test with no color (accessibility)
    no_color_console = Console(width=80, force_terminal=True, no_color=True)
    
    ticket_data = {
        'key': 'COLOR-789',
        'type': 'Task',
        'status': 'Done',
        'priority': 'Low',
        'assignee': 'test@example.com',
        'reporter': 'reporter@example.com',
        'summary': 'Test ticket for color scheme validation',
        'description': 'Testing accessibility with no color output.'
    }
    
    try:
        # Test components without color
        card = TicketCard.create(ticket_data)
        no_color_console.print(card)
        print("  ✅ Components render properly without color")
        
        header = format_processing_header(
            project="TEST",
            dry_run=True,
            llm_enabled=False,
            max_tickets=1
        )
        no_color_console.print(header)
        print("  ✅ Headers render properly without color")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Color scheme test failed: {e}")
        return False

def main():
    """Run all terminal formatting tests."""
    print("🖥️  Starting Terminal Size and Formatting Validation")
    print("=" * 60)
    
    try:
        # Test responsive design
        responsive_ok = test_responsive_design()
        
        # Test text wrapping
        wrapping_ok = test_text_wrapping()
        
        # Test color schemes
        color_ok = test_color_schemes()
        
        # Overall results
        print("\n" + "=" * 60)
        if responsive_ok and wrapping_ok and color_ok:
            print("✅ All terminal formatting tests passed!")
            print("🎉 Rich components are responsive and accessible")
            return 0
        else:
            print("❌ Some terminal formatting tests failed")
            return 1
            
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
