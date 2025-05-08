# Jira Cleanup Project - Code Recommendations

Based on the architectural analysis, this document provides concrete code recommendations and examples to enhance the Jira Cleanup project's architecture and maintainability.

## 1. Application Layer Implementation

The current architecture has most business logic in domain services and processors. Creating a dedicated application layer with use cases will improve separation of concerns.

### Recommended Directory Structure

```
src/
└── application/
    ├── __init__.py
    ├── use_cases/
    │   ├── __init__.py 
    │   ├── assess_ticket_use_case.py
    │   ├── process_quiescent_tickets_use_case.py
    │   └── generate_comment_use_case.py
    ├── dto/
    │   ├── __init__.py
    │   ├── ticket_dto.py
    │   └── assessment_dto.py
    └── exceptions.py
```

### Sample Use Case Implementation

```python
# src/application/use_cases/assess_ticket_use_case.py
from dataclasses import dataclass
from typing import Dict, Any, Optional

from jira_cleanup.src.domain.entities.ticket import Ticket
from jira_cleanup.src.domain.entities.assessment import Assessment
from jira_cleanup.src.domain.repositories.ticket_repository import TicketRepository
from jira_cleanup.src.domain.services.quiescence_evaluator import QuiescenceEvaluator
from jira_cleanup.src.domain.services.interfaces.llm_service import LlmService


@dataclass
class AssessTicketRequest:
    """Input data for the assess ticket use case."""
    ticket_key: str
    use_llm: bool = True


@dataclass
class AssessTicketResponse:
    """Output data from the assess ticket use case."""
    success: bool
    ticket_key: str
    is_quiescent: bool
    justification: str
    llm_assessment: Optional[Assessment] = None
    rule_details: list = None
    error_message: Optional[str] = None


class AssessTicketUseCase:
    """
    Application use case for assessing if a ticket is quiescent.
    
    This use case orchestrates the domain services to perform a comprehensive
    assessment of a ticket's quiescence status.
    """
    
    def __init__(
        self,
        ticket_repository: TicketRepository,
        quiescence_evaluator: QuiescenceEvaluator,
        llm_service: Optional[LlmService] = None
    ):
        """
        Initialize the use case with required dependencies.
        
        Args:
            ticket_repository: Repository for retrieving ticket data
            quiescence_evaluator: Domain service for evaluating quiescence
            llm_service: Optional LLM service for AI-powered assessment
        """
        self.ticket_repository = ticket_repository
        self.quiescence_evaluator = quiescence_evaluator
        self.llm_service = llm_service
    
    def execute(self, request: AssessTicketRequest) -> AssessTicketResponse:
        """
        Execute the use case to assess a ticket.
        
        Args:
            request: Input parameters for the use case
            
        Returns:
            Response containing assessment results
        """
        try:
            # Get ticket from repository
            ticket = self.ticket_repository.get_by_key(request.ticket_key)
            
            if ticket is None:
                return AssessTicketResponse(
                    success=False,
                    ticket_key=request.ticket_key,
                    is_quiescent=False,
                    justification="",
                    error_message=f"Ticket {request.ticket_key} not found"
                )
            
            # Evaluate with rule-based system
            is_quiescent, justification, rule_details = self.quiescence_evaluator.evaluate(ticket)
            
            # Get LLM assessment if requested and available
            llm_assessment = None
            if request.use_llm and self.llm_service:
                llm_assessment = self.llm_service.assess_ticket(ticket)
                
                # If LLM assessment differs from rule-based, use the more conservative
                if llm_assessment.is_quiescent != is_quiescent:
                    # If either says it's not quiescent, go with that
                    if not llm_assessment.is_quiescent:
                        is_quiescent = False
                        justification = f"LLM assessment: {llm_assessment.justification}"
                    elif not is_quiescent:
                        # Keep is_quiescent=False but note the disagreement
                        justification += f" (Note: LLM assessment disagreed)"
            
            return AssessTicketResponse(
                success=True,
                ticket_key=ticket.key,
                is_quiescent=is_quiescent,
                justification=justification,
                llm_assessment=llm_assessment,
                rule_details=rule_details
            )
        except Exception as e:
            return AssessTicketResponse(
                success=False,
                ticket_key=request.ticket_key,
                is_quiescent=False,
                justification="",
                error_message=str(e)
            )
```

### CLI Integration

Update main.py to use the use case:

```python
# Integration example (in main.py or similar)
def process_ticket(ticket_key, args):
    # Create repositories
    ticket_repo = JiraTicketRepository(jira_client)
    
    # Create evaluator
    evaluator = QuiescenceEvaluator()
    
    # Create LLM service if needed
    llm_service = None
    if not args.no_llm:
        prompt_service = YamlPromptService()
        llm_service = OllamaLlmService(
            prompt_service=prompt_service,
            ollama_url=args.ollama_url,
            model=args.llm_model
        )
    
    # Create use case
    use_case = AssessTicketUseCase(
        ticket_repository=ticket_repo,
        quiescence_evaluator=evaluator,
        llm_service=llm_service
    )
    
    # Execute use case
    request = AssessTicketRequest(
        ticket_key=ticket_key,
        use_llm=not args.no_llm
    )
    result = use_case.execute(request)
    
    return result
```

## 2. Dependency Injection Container

Implement a DI container to simplify dependency management and improve testability.

### Container Implementation

```python
# src/infrastructure/di/container.py
from typing import Dict, Any, Type, TypeVar, Optional, Callable

T = TypeVar('T')

class Container:
    """
    Simple dependency injection container for managing service instances.
    """
    
    def __init__(self):
        """Initialize an empty container."""
        self._factories = {}
        self._instances = {}
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory function for creating instances of a given interface.
        
        Args:
            interface: The interface or type to register
            factory: Factory function that creates instances
        """
        self._factories[interface] = factory
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register a singleton instance for a given interface.
        
        Args:
            interface: The interface or type to register
            instance: The singleton instance
        """
        self._instances[interface] = instance
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve an instance for the given interface.
        
        Args:
            interface: The interface or type to resolve
            
        Returns:
            An instance of the requested interface
            
        Raises:
            ValueError: If no registration exists for the interface
        """
        # Return singleton instance if registered
        if interface in self._instances:
            return self._instances[interface]
        
        # Create instance using factory if registered
        if interface in self._factories:
            instance = self._factories[interface]()
            self._instances[interface] = instance  # Cache for future use
            return instance
        
        raise ValueError(f"No registration found for {interface.__name__}")
```

### Container Setup

```python
# src/infrastructure/di/setup.py
from typing import Dict, Any

from jira_cleanup.src.domain.repositories.ticket_repository import TicketRepository
from jira_cleanup.src.domain.repositories.comment_repository import CommentRepository
from jira_cleanup.src.domain.services.interfaces.llm_service import LlmService
from jira_cleanup.src.domain.services.interfaces.prompt_service import PromptService
from jira_cleanup.src.domain.services.quiescence_evaluator import QuiescenceEvaluator

from jira_cleanup.src.infrastructure.repositories.jira_ticket_repository import JiraTicketRepository
from jira_cleanup.src.infrastructure.repositories.jira_comment_repository import JiraCommentRepository
from jira_cleanup.src.infrastructure.services.ollama_llm_service import OllamaLlmService
from jira_cleanup.src.infrastructure.services.yaml_prompt_service import YamlPromptService

from jira_cleanup.src.jirautil import create_jira_client

from jira_cleanup.src.application.use_cases.assess_ticket_use_case import AssessTicketUseCase

from .container import Container


def setup_container(config: Dict[str, Any]) -> Container:
    """
    Set up the dependency injection container with all services.
    
    Args:
        config: Application configuration
        
    Returns:
        Configured DI container
    """
    container = Container()
    
    # Create Jira client
    jira_client = create_jira_client(
        url=config['jira']['url'],
        auth_method=config['jira']['auth_method'],
        username=config['jira']['username'],
        token=config['jira']['token'],
        dry_run=config['defaults']['dry_run']
    )
    
    # Register infrastructure services
    container.register_instance(PromptService, YamlPromptService())
    
    # Register repositories
    container.register_factory(
        TicketRepository,
        lambda: JiraTicketRepository(jira_client)
    )
    container.register_factory(
        CommentRepository,
        lambda: JiraCommentRepository(jira_client)
    )
    
    # Register domain services
    container.register_factory(
        QuiescenceEvaluator,
        lambda: QuiescenceEvaluator()
    )
    
    # Register LLM service if configured
    if config['defaults'].get('use_llm', True):
        container.register_factory(
            LlmService,
            lambda: OllamaLlmService(
                prompt_service=container.resolve(PromptService),
                ollama_url=config['defaults']['ollama_url'],
                model=config['defaults']['llm_model']
            )
        )
    
    # Register use cases
    container.register_factory(
        AssessTicketUseCase,
        lambda: AssessTicketUseCase(
            ticket_repository=container.resolve(TicketRepository),
            quiescence_evaluator=container.resolve(QuiescenceEvaluator),
            llm_service=container.resolve(LlmService) if config['defaults'].get('use_llm', True) else None
        )
    )
    
    return container
```

### Using the Container

```python
# In main.py
from jira_cleanup.src.infrastructure.di.setup import setup_container
from jira_cleanup.src.application.use_cases.assess_ticket_use_case import AssessTicketUseCase, AssessTicketRequest

# Set up container
config = load_environment_config()
container = setup_container(config)

# Use the container to resolve use cases
assess_ticket_use_case = container.resolve(AssessTicketUseCase)

# Execute use case
request = AssessTicketRequest(ticket_key="PROJ-123", use_llm=True)
result = assess_ticket_use_case.execute(request)
```

## 3. Policy Framework

The system needs a more configurable policy framework. Below is a recommendation for implementing flexible, configurable policies.

### Policy Domain Model

```python
# src/domain/entities/policy.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
import re


@dataclass
class RuleDefinition:
    """Value object representing a rule definition within a policy."""
    
    rule_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    description: str = ""


@dataclass
class ActionDefinition:
    """Value object representing an action definition within a policy."""
    
    action_type: str
    condition: str
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class Policy:
    """
    Domain entity representing a governance policy.
    
    A policy consists of rules that evaluate aspects of a ticket
    and actions to take based on those evaluations.
    """
    
    id: str
    name: str
    description: str
    rules: List[RuleDefinition] = field(default_factory=list)
    actions: List[ActionDefinition] = field(default_factory=list)
    enabled: bool = True
    
    def add_rule(self, rule: RuleDefinition) -> None:
        """Add a rule to the policy."""
        self.rules.append(rule)
    
    def add_action(self, action: ActionDefinition) -> None:
        """Add an action to the policy."""
        self.actions.append(action)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Policy':
        """Create a Policy from a dictionary representation."""
        rules = []
        for rule_data in data.get('rules', []):
            rules.append(RuleDefinition(
                rule_type=rule_data['type'],
                params=rule_data.get('params', {}),
                weight=rule_data.get('weight', 1.0),
                description=rule_data.get('description', '')
            ))
        
        actions = []
        for action_data in data.get('actions', []):
            actions.append(ActionDefinition(
                action_type=action_data['type'],
                condition=action_data['condition'],
                params=action_data.get('params', {}),
                description=action_data.get('description', '')
            ))
        
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            rules=rules,
            actions=actions,
            enabled=data.get('enabled', True)
        )
```

### Policy Repository Interface

```python
# src/domain/repositories/policy_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional

from jira_cleanup.src.domain.entities.policy import Policy


class PolicyRepository(ABC):
    """
    Repository interface for policy storage and retrieval.
    """
    
    @abstractmethod
    def get_all(self) -> List[Policy]:
        """
        Get all available policies.
        
        Returns:
            List of policies
        """
        pass
    
    @abstractmethod
    def get_by_id(self, policy_id: str) -> Optional[Policy]:
        """
        Get a policy by its ID.
        
        Args:
            policy_id: The policy ID
            
        Returns:
            Policy if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_enabled(self) -> List[Policy]:
        """
        Get all enabled policies.
        
        Returns:
            List of enabled policies
        """
        pass
    
    @abstractmethod
    def add(self, policy: Policy) -> None:
        """
        Add a new policy.
        
        Args:
            policy: The policy to add
        """
        pass
    
    @abstractmethod
    def update(self, policy: Policy) -> None:
        """
        Update an existing policy.
        
        Args:
            policy: The policy to update
        """
        pass
    
    @abstractmethod
    def delete(self, policy_id: str) -> None:
        """
        Delete a policy.
        
        Args:
            policy_id: The ID of the policy to delete
        """
        pass
```

### YAML Policy Repository Implementation

```python
# src/infrastructure/repositories/yaml_policy_repository.py
import os
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any

from jira_cleanup.src.domain.entities.policy import Policy
from jira_cleanup.src.domain.repositories.policy_repository import PolicyRepository


class YamlPolicyRepository(PolicyRepository):
    """
    Implementation of PolicyRepository that stores policies in YAML files.
    """
    
    def __init__(self, policy_dir: str):
        """
        Initialize the repository with the policy directory.
        
        Args:
            policy_dir: Directory path where policy YAML files are stored
        """
        self.policy_dir = Path(policy_dir)
        if not self.policy_dir.exists():
            os.makedirs(self.policy_dir, exist_ok=True)
        
        self._policies = {}
        self._load_policies()
    
    def _load_policies(self) -> None:
        """Load all policies from YAML files in the policy directory."""
        for file_path in self.policy_dir.glob("*.yaml"):
            try:
                with open(file_path, 'r') as f:
                    policy_data = yaml.safe_load(f)
                
                policy = Policy.from_dict(policy_data)
                self._policies[policy.id] = policy
            except Exception as e:
                # Log error but continue loading other policies
                print(f"Error loading policy from {file_path}: {str(e)}")
    
    def get_all(self) -> List[Policy]:
        """Get all policies."""
        return list(self._policies.values())
    
    def get_by_id(self, policy_id: str) -> Optional[Policy]:
        """Get a policy by ID."""
        return self._policies.get(policy_id)
    
    def get_enabled(self) -> List[Policy]:
        """Get all enabled policies."""
        return [p for p in self._policies.values() if p.enabled]
    
    def add(self, policy: Policy) -> None:
        """Add a new policy."""
        # Save to internal dictionary
        self._policies[policy.id] = policy
        
        # Save to file
        file_path = self.policy_dir / f"{policy.id}.yaml"
        self._save_policy_to_file(policy, file_path)
    
    def update(self, policy: Policy) -> None:
        """Update an existing policy."""
        if policy.id not in self._policies:
            raise ValueError(f"Policy with ID {policy.id} not found")
        
        # Update in memory
        self._policies[policy.id] = policy
        
        # Save to file
        file_path = self.policy_dir / f"{policy.id}.yaml"
        self._save_policy_to_file(policy, file_path)
    
    def delete(self, policy_id: str) -> None:
        """Delete a policy."""
        if policy_id not in self._policies:
            raise ValueError(f"Policy with ID {policy_id} not found")
        
        # Remove from memory
        del self._policies[policy_id]
        
        # Remove file
        file_path = self.policy_dir / f"{policy_id}.yaml"
        if file_path.exists():
            os.remove(file_path)
    
    def _save_policy_to_file(self, policy: Policy, file_path: Path) -> None:
        """
        Save a policy to a YAML file.
        
        Args:
            policy: The policy to save
            file_path: The file path to save to
        """
        # Convert policy to dictionary
        policy_dict = {
            'id': policy.id,
            'name': policy.name,
            'description': policy.description,
            'enabled': policy.enabled,
            'rules': [],
            'actions': []
        }
        
        # Add rules
        for rule in policy.rules:
            policy_dict['rules'].append({
                'type': rule.rule_type,
                'params': rule.params,
                'weight': rule.weight,
                'description': rule.description
            })
        
        # Add actions
        for action in policy.actions:
            policy_dict['actions'].append({
                'type': action.action_type,
                'condition': action.condition,
                'params': action.params,
                'description': action.description
            })
        
        # Save to file
        with open(file_path, 'w') as f:
            yaml.dump(policy_dict, f, default_flow_style=False)
```

### Example Policy YAML

```yaml
# policies/stale_tickets.yaml
id: stale_tickets
name: Stale Ticket Policy
description: Policy for detecting and managing stale tickets
enabled: true

rules:
  - type: stale_check
    params:
      threshold_days: 14
    weight: 1.0
    description: Check if the ticket hasn't been updated in two weeks
    
  - type: unassigned_check
    weight: 0.5
    description: Check if the ticket is not assigned to anyone
    
  - type: unanswered_question_check
    weight: 0.8
    description: Check if there are unanswered questions in comments

actions:
  - type: add_comment
    condition: "score >= 1.5"
    params:
      template: stale_ticket_comment
      mention_assignee: true
    description: Add a comment to the ticket
    
  - type: transition
    condition: "score >= 2.0 && days_since_last_action > 7"
    params:
      to_status: Needs Attention
    description: Move ticket to 'Needs Attention' status
```

### Policy Evaluation Service

```python
# src/domain/services/policy_evaluator.py
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable
import re

from jira_cleanup.src.domain.entities.ticket import Ticket
from jira_cleanup.src.domain.entities.policy import Policy, RuleDefinition, ActionDefinition


@dataclass
class RuleResult:
    """Result of a rule evaluation."""
    rule_type: str
    passed: bool
    score: float
    reason: str


@dataclass
class ActionResult:
    """Result of an action evaluation."""
    action_type: str
    should_execute: bool
    params: Dict[str, Any]
    description: str


@dataclass
class PolicyEvaluationResult:
    """Result of evaluating a policy against a ticket."""
    policy_id: str
    policy_name: str
    total_score: float
    rule_results: List[RuleResult]
    action_results: List[ActionResult]
    
    @property
    def actions_to_execute(self) -> List[ActionResult]:
        """Get the list of actions that should be executed."""
        return [a for a in self.action_results if a.should_execute]


class PolicyEvaluator:
    """
    Domain service for evaluating policies against tickets.
    
    This service applies policy rules to tickets and determines
    which actions should be taken based on the evaluation results.
    """
    
    def __init__(self):
        """Initialize the policy evaluator with rule handlers."""
        self.rule_handlers = {
            'stale_check': self._evaluate_stale_rule,
            'unassigned_check': self._evaluate_unassigned_rule,
            'unanswered_question_check': self._evaluate_unanswered_question_rule,
            # Add more rule handlers here
        }
    
    def evaluate_policy(self, ticket: Ticket, policy: Policy) -> PolicyEvaluationResult:
        """
        Evaluate a policy against a ticket.
        
        Args:
            ticket: The ticket to evaluate
            policy: The policy to apply
            
        Returns:
            Evaluation result with scores and recommended actions
        """
        # Evaluate all rules
        rule_results = []
        total_score = 0.0
        
        for rule in policy.rules:
            result = self._evaluate_rule(ticket, rule)
            rule_results.append(result)
            
            if result.passed:
                total_score += result.score
        
        # Evaluate actions
        action_results = []
        for action in policy.actions:
            should_execute = self._evaluate_condition(
                action.condition,
                {
                    'score': total_score,
                    'days_since_update': ticket.days_since_update,
                    'days_since_creation': ticket.days_since_creation,
                    'has_assignee': ticket.is_assigned(),
                    'is_closed': ticket.is_closed(),
                    'days_since_last_action': self._get_days_since_last_action(ticket)
                }
            )
            
            action_results.append(ActionResult(
                action_type=action.action_type,
                should_execute=should_execute,
                params=action.params,
                description=action.description
            ))
        
        return PolicyEvaluationResult(
            policy_id=policy.id,
            policy_name=policy.name,
            total_score=total_score,
            rule_results=rule_results,
            action_results=action_results
        )
    
    def _evaluate_rule(self, ticket: Ticket, rule: RuleDefinition) -> RuleResult:
        """
        Evaluate a single rule against a ticket.
        
        Args:
            ticket: The ticket to evaluate
            rule: The rule to apply
            
        Returns:
            Rule evaluation result
        """
        if rule.rule_type not in self.rule_handlers:
            return RuleResult(
                rule_type=rule.rule_type,
                passed=False,
                score=0.0,
                reason=f"Unknown rule type: {rule.rule_type}"
            )
        
        # Call the appropriate handler
        handler = self.rule_handlers[rule.rule_type]
        passed, reason = handler(ticket, rule.params)
        
        return RuleResult(
            rule_type=rule.rule_type,
            passed=passed,
            score=rule.weight if passed else 0.0,
            reason=reason
        )
    
    def _evaluate_stale_rule(self, ticket: Ticket, params: Dict[str, Any]) -> tuple[bool, str]:
        """Evaluate if a ticket is stale based on last update."""
        threshold_days = params.get('threshold_days', 14)
        is_stale = ticket.days_since_update >= threshold_days
        
        if is_stale:
            return True, f"Ticket has not been updated in {ticket.days_since_update} days"
        else:
            return False, f"Ticket was updated {ticket.days_since_update} days ago"
    
    def _evaluate_unassigned_rule(self, ticket: Ticket, params: Dict[str, Any]) -> tuple[bool, str]:
        """Evaluate if a ticket is unassigned."""
        if ticket.is_closed():
            return False, "Ticket is closed, so assignee status is not relevant"
        
        if not ticket.is_assigned():
            return True, "Ticket is open but has no assignee"
        
        return False, f"Ticket is assigned to {ticket.assignee}"
    
    def _evaluate_unanswered_question_rule(self, ticket: Ticket, params: Dict[str, Any]) -> tuple[bool, str]:
        """Evaluate if a ticket has unanswered questions."""
        if not ticket.comments:
            return False, "No comments to check for questions"
        
        # Sort comments by date
        sorted_comments = sorted(ticket.comments, key=lambda c: c.created_date)
        
        # Check if the last comment contains a question
        last_comment = sorted_comments[-1]
        
        # Default question indicators
        question_indicators = params.get('question_indicators', [
            "?", "question", "can you", "could you", "would you", "will you", 
            "please clarify", "please explain", "what is", "how to"
        ])
        
        # Check if the last comment has question indicators
        has_question = any(indicator in last_comment.body.lower() for indicator in question_indicators)
        
        if has_question:
            return True, f"Last comment from {last_comment.author} appears to contain unanswered questions"
        
        return False, "No unanswered questions detected in the latest comments"
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition expression against a context.
        
        Args:
            condition: Condition expression to evaluate
            context: Dictionary of variables for the condition
            
        Returns:
            True if the condition is met, False otherwise
        """
        # Replace variables in the condition
        expr = condition
        for key, value in context.items():
            # Handle booleans specially
            if isinstance(value, bool):
                expr = re.sub(r'\b' + key + r'\b', str(value).lower(), expr)
            else:
                expr = re.sub(r'\b' + key + r'\b', str(value), expr)
        
        # Evaluate the expression
        try:
            return eval(expr)
        except Exception as e:
            # Log the error and return False
            print(f"Error evaluating condition '{condition}': {str(e)}")
            return False
    
    def _get_days_since_last_action(self, ticket: Ticket) -> int:
        """
        Calculate days since the last action on a ticket.
        
        Args:
            ticket: The ticket to check
            
        Returns:
            Days since the last action (comment or change)
        """
        # Get the latest date from comments and changelog
        latest_date = ticket.updated_date
        
        for comment in ticket.comments:
            if comment.created_date > latest_date:
                latest_date = comment.created_date
        
        for change in ticket.changelog:
            if change.date > latest_date:
                latest_date = change.date
        
        # Calculate days since that date
        from datetime import datetime
        now = datetime.now().replace(tzinfo=latest_date.tzinfo)
        return (now - latest_date).days
```

## 4. Testing Framework

Implement a comprehensive testing strategy. Here are examples for different test levels.

### Domain Entity Tests

```python
# tests/domain/entities/test_ticket.py
import pytest
from datetime import datetime, timedelta

from jira_cleanup.src.domain.entities.ticket import Ticket, User, Comment


class TestTicket:
    """Tests for the Ticket domain entity."""
    
    def test_is_stale_with_recent_update(self):
        """Test that a recently updated ticket is not stale."""
        # Arrange
        ticket = Ticket(
            key="TEST-123",
            summary="Test ticket",
            status="Open",
            issue_type="Task",
            created_date=datetime.now() - timedelta(days=30),
            updated_date=datetime.now() - timedelta(days=5)
        )
        
        # Act
        result = ticket.is_stale(threshold_days=14)
        
        # Assert
        assert result is False
    
    def test_is_stale_with_old_update(self):
        """Test that a ticket without recent updates is stale."""
        # Arrange
        ticket = Ticket(
            key="TEST-123",
            summary="Test ticket",
