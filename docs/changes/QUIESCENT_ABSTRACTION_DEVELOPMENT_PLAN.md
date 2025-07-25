# Quiescent Framework Abstraction Development Plan 🎯

## 🏗️ **Architectural Goal: Triple Pattern Implementation**

Transform the current quiescence-hardcoded framework into a clean triple pattern:
```
QuiescentAnalyzer → QuiescentResult → QuiescentFormatter
```

**Core Principle**: The processing framework must be entirely agnostic to analysis details. All analysis-specific logic lives in the analyzer, results, and formatter components.

## 🔍 **Current State Analysis**

### **Problems Identified:**
1. **QuiescentTicketProcessor** - Hardcoded quiescence logic (`assessment.is_quiescent`, quiescence-specific statistics)
2. **AssessmentResult** - Quiescence-specific fields force all analyzers to fake quiescence concepts
3. **UI Components** - Hardcoded "QUIESCENT" vs "ACTIVE" terminology in TicketCard
4. **Statistics Tracking** - Hardcoded quiescence metrics in summary tables
5. **Core Processor** - Specifically creates QuiescentTicketProcessor

### **Files Requiring Changes:**
- `src/jiraclean/processors/quiescent.py` - Contains hardcoded quiescence logic
- `src/jiraclean/entities/assessment.py` - Quiescence-specific result structure
- `src/jiraclean/ui/components.py` - Hardcoded quiescence UI terminology
- `src/jiraclean/core/processor.py` - Creates quiescence-specific processor
- `src/jiraclean/analysis/ticket_analyzer.py` - Returns generic AssessmentResult

## 🎯 **Target Architecture**

### **Triple Pattern Components:**

1. **QuiescentAnalyzer** - Business logic for quiescence detection
2. **QuiescentResult** - Natural quiescence-specific data structure
3. **QuiescentFormatter** - UI adapter that knows how to display quiescence results

### **Generic Framework Components:**

1. **GenericTicketProcessor** - Framework-agnostic processor
2. **BaseResult** - Common interface for all result types
3. **BaseFormatter** - Common interface for all formatters

## 📋 **Implementation Plan**

### **Phase 1: Create Base Interfaces**

#### **File: `src/jiraclean/entities/base_result.py`**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseResult(ABC):
    """Base interface for all analysis results."""
    
    @abstractmethod
    def needs_action(self) -> bool:
        """Determine if this result requires action to be taken."""
        pass
    
    @abstractmethod
    def get_planned_comment(self) -> str:
        """Get the comment that should be added to the ticket."""
        pass
    
    @abstractmethod
    def get_responsible_party(self) -> str:
        """Get the party responsible for addressing this result."""
        pass
    
    @abstractmethod
    def get_suggested_action(self) -> str:
        """Get the suggested action for this result."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        pass
```

#### **File: `src/jiraclean/ui/formatters/base_formatter.py`**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from rich.panel import Panel
from rich.table import Table

class BaseFormatter(ABC):
    """Base interface for all result formatters."""
    
    @abstractmethod
    def format_ticket_card(self, ticket_data: Dict[str, Any], result) -> Panel:
        """Format a ticket card with analysis result."""
        pass
    
    @abstractmethod
    def format_assessment_panel(self, result) -> Panel:
        """Format an assessment panel for the result."""
        pass
    
    @abstractmethod
    def format_summary_stats(self, stats: Dict[str, Any]) -> Table:
        """Format summary statistics table."""
        pass
    
    @abstractmethod
    def get_status_text(self, result) -> str:
        """Get status text for display (e.g., 'QUIESCENT', 'HIGH_QUALITY')."""
        pass
    
    @abstractmethod
    def get_status_style(self, result) -> str:
        """Get Rich style for status display."""
        pass
    
    @abstractmethod
    def get_border_style(self, result) -> str:
        """Get Rich border style for panels."""
        pass
```

### **Phase 2: Create Quiescent-Specific Components**

#### **File: `src/jiraclean/entities/quiescent_result.py`**
```python
from dataclasses import dataclass
from typing import Dict, Any
from .base_result import BaseResult

@dataclass
class QuiescentResult(BaseResult):
    """Result structure for quiescence analysis."""
    
    is_quiescent: bool
    staleness_score: float  # 0-10 scale indicating how stale the ticket is
    inactivity_days: int    # Number of days without activity
    justification: str      # Detailed explanation of quiescence assessment
    responsible_party: str  # Person responsible for the ticket
    suggested_action: str   # Recommended action to take
    suggested_deadline: str # When action should be taken
    planned_comment: str    # Comment to add to ticket
    
    def needs_action(self) -> bool:
        """Quiescent tickets need action."""
        return self.is_quiescent
    
    def get_planned_comment(self) -> str:
        """Get the comment for quiescent tickets."""
        return self.planned_comment
    
    def get_responsible_party(self) -> str:
        """Get responsible party."""
        return self.responsible_party
    
    def get_suggested_action(self) -> str:
        """Get suggested action."""
        return self.suggested_action
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_quiescent': self.is_quiescent,
            'staleness_score': self.staleness_score,
            'inactivity_days': self.inactivity_days,
            'justification': self.justification,
            'responsible_party': self.responsible_party,
            'suggested_action': self.suggested_action,
            'suggested_deadline': self.suggested_deadline,
            'planned_comment': self.planned_comment
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuiescentResult':
        """Create from dictionary."""
        return cls(
            is_quiescent=data.get('is_quiescent', False),
            staleness_score=data.get('staleness_score', 0.0),
            inactivity_days=data.get('inactivity_days', 0),
            justification=data.get('justification', 'No justification provided'),
            responsible_party=data.get('responsible_party', 'Unknown'),
            suggested_action=data.get('suggested_action', 'No action suggested'),
            suggested_deadline=data.get('suggested_deadline', 'No deadline suggested'),
            planned_comment=data.get('planned_comment', 'No comment generated')
        )
    
    @classmethod
    def default(cls) -> 'QuiescentResult':
        """Create default (failed) result."""
        return cls(
            is_quiescent=False,
            staleness_score=0.0,
            inactivity_days=0,
            justification="Failed to assess ticket",
            responsible_party="Unknown",
            suggested_action="None",
            suggested_deadline="None",
            planned_comment="Failed to generate comment"
        )
```

#### **File: `src/jiraclean/ui/formatters/quiescent_formatter.py`**
```python
from typing import Dict, Any
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

from .base_formatter import BaseFormatter
from ..console import console

class QuiescentFormatter(BaseFormatter):
    """Formatter for quiescence analysis results."""
    
    def format_ticket_card(self, ticket_data: Dict[str, Any], result) -> Panel:
        """Format ticket card with quiescence assessment."""
        # Extract ticket information
        key = ticket_data.get('key', 'UNKNOWN')
        ticket_type = ticket_data.get('type', 'Unknown')
        status = ticket_data.get('status', 'Unknown')
        summary = ticket_data.get('summary', 'No summary available')
        priority = ticket_data.get('priority', 'Unknown')
        assignee = ticket_data.get('assignee', 'Unassigned')
        reporter = ticket_data.get('reporter', 'Unknown')
        
        # Create ticket info table
        ticket_table = Table.grid(padding=1)
        ticket_table.add_column(style="bold", justify="right", width=12)
        ticket_table.add_column(justify="left")
        
        ticket_table.add_row("Key:", Text(key, style="ticket.key"))
        ticket_table.add_row("Type:", Text(ticket_type, style="ticket.type"))
        ticket_table.add_row("Status:", Text(status, style="ticket.status"))
        ticket_table.add_row("Priority:", Text(priority, style="ticket.priority"))
        ticket_table.add_row("Assignee:", assignee)
        ticket_table.add_row("Reporter:", reporter)
        ticket_table.add_row("Summary:", Text(summary, style="bold"))
        
        # Create assessment table
        assessment_table = Table.grid(padding=1)
        assessment_table.add_column(style="bold", justify="right", width=12)
        assessment_table.add_column(justify="left")
        
        status_text = self.get_status_text(result)
        status_style = self.get_status_style(result)
        
        assessment_table.add_row("", "")  # Spacer
        assessment_table.add_row("Assessment:", Text(status_text, style=status_style))
        assessment_table.add_row("Reason:", Text(result.justification, style="italic"))
        assessment_table.add_row("Responsible:", result.responsible_party)
        assessment_table.add_row("Action:", result.suggested_action)
        
        # Add quiescence-specific fields
        if result.is_quiescent:
            assessment_table.add_row("Staleness:", f"{result.staleness_score:.1f}/10")
            assessment_table.add_row("Inactive Days:", str(result.inactivity_days))
        
        content = Columns([ticket_table, assessment_table], equal=False, expand=True)
        border_style = self.get_border_style(result)
        
        return Panel(
            content,
            title=f"🎫 Ticket {key}",
            title_align="left",
            border_style=border_style,
            padding=(1, 2)
        )
    
    def format_assessment_panel(self, result) -> Panel:
        """Format detailed assessment panel."""
        content = Table.grid(padding=1)
        content.add_column(style="bold", justify="right", width=15)
        content.add_column(justify="left")
        
        status_text = self.get_status_text(result)
        status_style = self.get_status_style(result)
        
        content.add_row("Status:", Text(status_text, style=status_style))
        content.add_row("Reason:", Text(result.justification, style="italic"))
        content.add_row("Responsible:", result.responsible_party)
        content.add_row("Suggested Action:", result.suggested_action)
        content.add_row("Deadline:", result.suggested_deadline)
        
        if result.is_quiescent:
            content.add_row("Staleness Score:", f"{result.staleness_score:.1f}/10")
            content.add_row("Inactive Days:", str(result.inactivity_days))
        
        content.add_row("", "")
        content.add_row("Planned Comment:", "")
        content.add_row("", Text(result.planned_comment, style="dim"))
        
        border_style = self.get_border_style(result)
        
        return Panel(
            content,
            title="🤖 LLM Assessment",
            border_style=border_style,
            padding=(1, 2)
        )
    
    def format_summary_stats(self, stats: Dict[str, Any]) -> Table:
        """Format quiescence-specific summary statistics."""
        table = Table(title="Processing Summary", show_header=True, header_style="bold magenta")
        
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Count", justify="right", style="green", width=10)
        table.add_column("Details", style="white")
        
        table.add_row("Tickets Processed", str(stats.get('processed', 0)), "Total tickets examined")
        table.add_row("Actions Taken", str(stats.get('actioned', 0)), "Comments added or status changes")
        table.add_row("Quiescent Found", str(stats.get('quiescent', 0)), "Tickets identified as inactive")
        table.add_row("Active Tickets", str(stats.get('non_quiescent', 0)), "Tickets with recent activity")
        table.add_row("Errors", str(stats.get('errors', 0)), "Processing failures")
        table.add_row("Skipped", str(stats.get('skipped', 0)), "Tickets not processed")
        
        return table
    
    def get_status_text(self, result) -> str:
        """Get status text for quiescence."""
        if result.is_quiescent:
            return "🟡 QUIESCENT"
        else:
            return "🟢 ACTIVE"
    
    def get_status_style(self, result) -> str:
        """Get Rich style for status."""
        return "assessment.quiescent" if result.is_quiescent else "assessment.active"
    
    def get_border_style(self, result) -> str:
        """Get border style for panels."""
        return "yellow" if result.is_quiescent else "blue"
```

### **Phase 3: Create Generic Processor**

#### **File: `src/jiraclean/processors/generic.py`**
```python
"""
Generic ticket processor implementation.

This module provides a processor that works with any analyzer and formatter,
making the processing framework completely agnostic to analysis types.
"""

import logging
from typing import Dict, Any, List, Optional

from jiraclean.processors.base import TicketProcessor
from jiraclean.jirautil import JiraClient
from jiraclean.iterators.project import ProjectTicketIterator
from jiraclean.analysis.base import BaseTicketAnalyzer
from jiraclean.ui.formatters.base_formatter import BaseFormatter

logger = logging.getLogger('jiraclean.processors.generic')


class GenericTicketProcessor(TicketProcessor):
    """
    Generic processor that works with any analyzer and formatter.
    
    This processor is completely agnostic to analysis types and delegates
    all analysis-specific logic to the analyzer and formatter components.
    """
    
    def __init__(self, 
                jira_client: JiraClient,
                analyzer: BaseTicketAnalyzer,
                formatter: BaseFormatter):
        """
        Initialize the generic ticket processor.
        
        Args:
            jira_client: JiraClient instance for Jira API access
            analyzer: Analyzer instance for ticket assessment
            formatter: Formatter instance for UI display
        """
        super().__init__()
        self.jira_client = jira_client
        self.analyzer = analyzer
        self.formatter = formatter
        
        # Generic statistics - no analysis-specific fields
        self._stats.update({
            'needs_action': 0,
            'no_action_needed': 0,
            'assessment_failures': 0,
            'comments_added': 0,
            'prefiltered': 0
        })
    
    def process(self, 
                ticket_key: str, 
                ticket_data: Optional[Dict[str, Any]] = None, 
                dry_run: bool = True) -> Dict[str, Any]:
        """
        Process a single ticket using the configured analyzer and formatter.
        
        Args:
            ticket_key: The Jira issue key
            ticket_data: Optional ticket data (fetched if not provided)
            dry_run: If True, only simulate actions without making changes
            
        Returns:
            Result dictionary with action information
        """
        result = {
            'ticket_key': ticket_key,
            'actions': [],
            'success': False,
            'message': ''
        }
        
        try:
            # Fetch ticket data if not provided
            if ticket_data is None:
                ticket_data = self.jira_client.get_issue(ticket_key, fields=None)
            
            # Analyze the ticket using the injected analyzer
            analysis_result = self.analyzer.analyze(ticket_data)
            
            # Use formatter to determine status and log appropriately
            status_text = self.formatter.get_status_text(analysis_result)
            logger.info(f"Ticket {ticket_key} analysis: {status_text} - {analysis_result.justification}")
            
            # Update statistics based on result
            if analysis_result.needs_action():
                self._stats['needs_action'] += 1
            else:
                self._stats['no_action_needed'] += 1
            
            # Take action if needed
            if analysis_result.needs_action():
                comment = analysis_result.get_planned_comment()
                
                if not dry_run:
                    try:
                        comment_result = self.jira_client.add_comment(ticket_key, comment)
                        self._stats['comments_added'] += 1
                        
                        result['actions'].append({
                            'type': 'comment',
                            'description': f'Added {self.analyzer.get_analyzer_type()} comment',
                            'success': True,
                            'details': {
                                'comment_id': comment_result.get('id'),
                                'comment_body': comment[:100] + '...'
                            }
                        })
                    except Exception as e:
                        logger.error(f"Error adding comment to {ticket_key}: {str(e)}")
                        result['actions'].append({
                            'type': 'comment',
                            'description': f'Failed to add {self.analyzer.get_analyzer_type()} comment',
                            'success': False,
                            'details': {'error': str(e)}
                        })
                else:
                    # Dry run mode
                    self.jira_client.add_comment(ticket_key, comment)
                    result['actions'].append({
                        'type': 'comment',
                        'description': f'Would add {self.analyzer.get_analyzer_type()} comment (dry run)',
                        'success': True,
                        'details': {'dry_run': True}
                    })
            
            result['success'] = True
            result['message'] = f"Ticket {ticket_key} processed successfully"
            result['analysis_result'] = analysis_result.to_dict()
            
        except Exception as e:
            logger.error(f"Error processing ticket {ticket_key}: {str(e)}")
            self._stats['assessment_failures'] += 1
            result['success'] = False
            result['message'] = f"Error processing ticket: {str(e)}"
        
        self._update_stats(result)
        return result
    
    def get_formatter(self) -> BaseFormatter:
        """Get the formatter for UI display."""
        return self.formatter
    
    def get_analyzer_type(self) -> str:
        """Get the analyzer type for logging and display."""
        return self.analyzer.get_analyzer_type()
```

### **Phase 4: Update Quiescent Analyzer**

#### **Modify: `src/jiraclean/analysis/ticket_analyzer.py`**
```python
# Update QuiescentAnalyzer to return QuiescentResult instead of AssessmentResult

from jiraclean.entities.quiescent_result import QuiescentResult

class QuiescentAnalyzer(BaseTicketAnalyzer):
    def analyze(self, ticket_data: Dict[str, Any], template: Optional[str] = None, **kwargs) -> QuiescentResult:
        """
        Analyze a ticket for quiescence.
        
        Returns:
            QuiescentResult with quiescence-specific assessment
        """
        if template is None:
            template = self.get_default_template()
        
        return self.assess_quiescence(ticket_data, template)
    
    def assess_quiescence(self, ticket_data: Dict[str, Any], template: str = "quiescent_assessment") -> QuiescentResult:
        """
        Assess a ticket for quiescence using the configured LLM.
        
        Returns:
            QuiescentResult with LLM assessment
        """
        # ... existing logic ...
        
        # Calculate quiescence-specific metrics
        staleness_score = self._calculate_staleness_score(ticket_data)
        inactivity_days = self._calculate_inactivity_days(ticket_data)
        
        # Parse LLM response and create QuiescentResult
        try:
            result_dict = json.loads(cleaned_response)
            
            return QuiescentResult(
                is_quiescent=result_dict.get('is_quiescent', False),
                staleness_score=staleness_score,
                inactivity_days=inactivity_days,
                justification=result_dict.get('justification', 'No justification provided'),
                responsible_party=result_dict.get('responsible_party', 'Unknown'),
                suggested_action=result_dict.get('suggested_action', 'No action suggested'),
                suggested_deadline=result_dict.get('suggested_deadline', 'No deadline suggested'),
                planned_comment=result_dict.get('planned_comment', 'No comment generated')
            )
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return QuiescentResult.default()
    
    def _calculate_staleness_score(self, ticket_data: Dict[str, Any]) -> float:
        """Calculate staleness score (0-10) based on ticket age and activity."""
        # Implementation for calculating staleness
        pass
    
    def _calculate_inactivity_days(self, ticket_data: Dict[str, Any]) -> int:
        """Calculate number of days since last activity."""
        # Implementation for calculating inactivity
        pass
```

### **Phase 5: Update Core Processor**

#### **Modify: `src/jiraclean/core/processor.py`**
```python
from jiraclean.processors.generic import GenericTicketProcessor
from jiraclean.ui.formatters.quiescent_formatter import QuiescentFormatter

def create_processor(analyzer_type: str, jira_client: JiraClient, llm_service) -> GenericTicketProcessor:
    """Create a processor with the appropriate analyzer and formatter."""
    
    if analyzer_type == 'quiescent':
        from jiraclean.analysis.ticket_analyzer import QuiescentAnalyzer
        analyzer = QuiescentAnalyzer(llm_service)
        formatter = QuiescentFormatter()
        return GenericTicketProcessor(jira_client, analyzer, formatter)
    
    # Future analyzer types would be added here
    # elif analyzer_type == 'quality':
    #     analyzer = QualityAnalyzer(llm_service)
    #     formatter = QualityFormatter()
    #     return GenericTicketProcessor(jira_client, analyzer, formatter)
    
    else:
        raise ValueError(f"Unknown analyzer type: {analyzer_type}")
```

### **Phase 6: Backward Compatibility**

#### **Maintain: `src/jiraclean/processors/quiescent.py`**
```python
# Keep as compatibility wrapper
from jiraclean.processors.generic import GenericTicketProcessor
from jiraclean.ui.formatters.quiescent_formatter import QuiescentFormatter

class QuiescentTicketProcessor(GenericTicketProcessor):
    """
    Backward compatibility wrapper for QuiescentTicketProcessor.
    
    This maintains the existing API while using the new generic architecture.
    """
    
    def __init__(self, 
                jira_client: JiraClient,
                ticket_analyzer: BaseTicketAnalyzer,
                min_age_days: int = 14,
                min_inactive_days: int = 7):
        """Maintain existing constructor signature."""
        formatter = QuiescentFormatter()
        super().__init__(jira_client, ticket_analyzer, formatter)
        
        # Store original parameters for compatibility
        self.min_age_days = min_age_days
        self.min_inactive_days = min_inactive_days
    
    # Maintain existing method signatures for backward compatibility
    def process_project(self, project_key: str, max_tickets: Optional[int] = None, 
                       statuses_to_exclude: Optional[List[str]] = None,
                       dry_run: bool = True, skip_prefilter: bool = False) -> Dict[str, Any]:
        """Maintain existing process_project signature."""
        # Delegate to parent with appropriate mapping
        return super().process_project(project_key, max_tickets, statuses_to_exclude, dry_run, skip_prefilter)
```

## 🧪 **Testing Strategy**

### **Phase 1: Unit Tests**
- Test QuiescentResult creation and methods
- Test QuiescentFormatter output formatting
- Test GenericTicketProcessor with mock analyzer/formatter

### **Phase 2: Integration Tests**
- Test complete quiescence analysis pipeline
- Verify UI output matches expected format
- Test backward compatibility with existing code

### **Phase 3: Regression Tests**
- Run existing test suite to ensure no breaking changes
- Compare output before/after refactoring
- Validate statistics and metrics are preserved

## 📊 **Success Criteria**

### **Framework Agnosticism:**
✅ GenericTicketProcessor has zero knowledge of analysis types
✅ No hardcoded quiescence logic in core framework
✅ UI adapts automatically to different result types

### **Natural Result Types:**
✅ QuiescentResult uses native quiescence terminology
✅ Specific fields like staleness_score and inactivity_days
✅ No forced mapping to generic concepts

### **Flexible UI:**
✅ QuiescentFormatter handles all quiescence display logic
✅ Appropriate colors, icons, and terminology
✅ Statistics tables show relevant metrics

### **Easy Extension:**
✅ Adding new analyzer requires: Analyzer + Result + Formatter
✅ No changes to core framework
✅ Type-safe implementation

### **Backward Compatibility:**
✅ Existing QuiescentTicketProcessor API preserved
✅ No breaking changes to public interfaces
✅ Gradual migration path available

## 🚀 **Implementation Order**

1. **Base Interfaces** - Create BaseResult and BaseFormatter
2. **Quiescent Components** - QuiescentResult and QuiescentFormatter
3. **Generic Processor** - Framework-agnostic GenericTicketProcessor
4. **Update Analyzer** - QuiescentAnalyzer returns QuiescentResult
5. **Update Core** - Use new triple pattern in processor creation
6. **Backward Compatibility** - Wrapper classes for existing API
7. **Testing** - Comprehensive test suite validation
8. **Documentation** - Update architecture documentation

## 🎯 **Benefits Achieved**

### **Clean Architecture:**
- Complete separation of concerns
- Framework agnostic to analysis types
- Natural result types for each analyzer

### **Extensibility:**
- Easy to add new analyzer types
- No core framework changes required
- Type-safe implementation

### **Maintainability:**
- Clear responsibilities for each component
- Testable components in isolation
- Backward compatibility preserved

This plan transforms the quiescence framework into a clean, extensible architecture that serves as the foundation for unlimited analyzer types while maintaining full backward compatibility.
