# Architecture Overview

This document provides a comprehensive overview of the Jira Cleanup project's architecture, design principles, and system organization.

## Executive Summary

The Jira Cleanup project demonstrates a well-structured application built with modern software architecture principles. It successfully transforms a client-specific solution into a more general-purpose, configurable framework for Jira ticket governance. The codebase shows evidence of thoughtful design decisions, particularly in its adoption of Clean Architecture patterns, domain-driven design, and clear separation of concerns.

## Architectural Principles

### Clean Architecture

The project follows Clean Architecture principles with clear layer separation:

1. **Domain Layer** (innermost): Contains business logic and entities
2. **Application Layer**: Orchestrates use cases and workflows
3. **Infrastructure Layer** (outermost): Handles external systems and frameworks

### Key Design Principles

| Principle | Implementation | Benefits |
|-----------|----------------|----------|
| **Dependency Inversion** | Inner layers define interfaces that outer layers implement | Testability, flexibility |
| **Single Responsibility** | Each class has one reason to change | Maintainability |
| **Open/Closed Principle** | Open for extension, closed for modification | Extensibility |
| **Interface Segregation** | Small, focused interfaces | Loose coupling |
| **Domain-Driven Design** | Rich domain model with business logic | Clear business rules |

## System Architecture

### High-Level Structure

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                         │
│                     (jiraclean.main)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Application Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Iterators  │  │ Processors  │  │    Use Cases        │  │
│  │             │  │             │  │   (Future)          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Domain Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Entities   │  │ Repositories│  │     Services        │  │
│  │             │  │ (Interfaces)│  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│               Infrastructure Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Jira Client │  │ Repository  │  │   LLM Service       │  │
│  │             │  │Implementations│  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### Domain Layer
- **Entities**: Core business objects (Ticket, Assessment, User)
- **Value Objects**: Immutable data structures (Comment, TicketKey)
- **Domain Services**: Business logic that doesn't belong to entities
- **Repository Interfaces**: Data access contracts
- **Service Interfaces**: External service contracts

#### Application Layer
- **Iterators**: Ticket selection strategies
- **Processors**: Ticket processing workflows
- **Use Cases**: Business process orchestration (future)
- **DTOs**: Data transfer objects for layer boundaries

#### Infrastructure Layer
- **Repository Implementations**: Jira API, database access
- **Service Implementations**: LLM providers, notification services
- **External Integrations**: Jira client, Ollama client
- **Configuration**: Environment and file-based configuration

## Core Components

### Domain Model

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Ticket      │    │   Assessment    │    │     Action      │
│                 │    │                 │    │                 │
│ - key           │    │ - is_quiescent  │    │ - type          │
│ - summary       │    │ - justification │    │ - parameters    │
│ - status        │    │ - confidence    │    │ - timestamp     │
│ - assignee      │    │ - details       │    │                 │
│ - created_date  │    │                 │    │                 │
│ - updated_date  │    │                 │    │                 │
│                 │    │                 │    │                 │
│ + is_quiescent()│    │                 │    │                 │
│ + is_stale()    │    │                 │    │                 │
│ + age_in_days() │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Quiescence      │    │ Comment         │                │
│  │ Evaluator       │    │ Generator       │                │
│  │                 │    │                 │                │
│  │ + evaluate()    │    │ + generate()    │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ LLM Service     │    │ Prompt Service  │                │
│  │ (Interface)     │    │ (Interface)     │                │
│  │                 │    │                 │                │
│  │ + assess()      │    │ + load_template()│               │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Ticket Processing Flow

```
1. CLI Input
   ↓
2. Iterator Selection
   ↓
3. Ticket Retrieval
   ↓
4. Pre-filtering
   ↓
5. Assessment (Rule-based + LLM)
   ↓
6. Action Determination
   ↓
7. Action Execution (or Dry Run)
   ↓
8. Result Reporting
```

### Detailed Processing Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Project   │───▶│   Filter    │───▶│   Assess    │
│  Iterator   │    │   Tickets   │    │   Tickets   │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
┌─────────────┐    ┌─────────────┐    ┌──────▼──────┐
│   Report    │◀───│   Execute   │◀───│  Generate   │
│   Results   │    │   Actions   │    │   Actions   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Design Patterns

### Repository Pattern
- **Purpose**: Abstract data access
- **Implementation**: Interface in domain, concrete implementations in infrastructure
- **Benefits**: Testability, flexibility, separation of concerns

### Strategy Pattern
- **Purpose**: Interchangeable algorithms
- **Implementation**: Iterator and Processor hierarchies
- **Benefits**: Extensibility, runtime algorithm selection

### Template Method Pattern
- **Purpose**: Define algorithm skeleton
- **Implementation**: Base processor with customizable steps
- **Benefits**: Code reuse, consistent workflow

### Dependency Injection
- **Purpose**: Manage dependencies
- **Implementation**: Constructor injection, interface-based
- **Benefits**: Testability, loose coupling, configurability

## Configuration Architecture

### Configuration Sources

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Environment    │    │  Command Line   │    │  Config Files   │
│   Variables     │    │   Arguments     │    │   (.env, YAML)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Configuration         │
                    │     Manager             │
                    └─────────────────────────┘
```

### Template System

```
User Templates (~/.config/jiraclean/templates/)
         │
         ▼ (if not found)
System Templates (/etc/jiraclean/templates/)
         │
         ▼ (if not found)
Built-in Templates (package defaults)
```

## Extension Points

### Adding New Components

#### New Iterator
```python
class CustomIterator(TicketIterator):
    def __iter__(self) -> Iterator[Ticket]:
        # Custom ticket selection logic
        pass
```

#### New Processor
```python
class CustomProcessor(TicketProcessor):
    def process(self, ticket: Ticket) -> Dict[str, Any]:
        # Custom processing logic
        pass
```

#### New LLM Provider
```python
class CustomLlmService(LlmService):
    def assess_ticket(self, ticket: Ticket) -> Assessment:
        # Custom LLM integration
        pass
```

## Quality Attributes

### Maintainability
- **Modular design**: Clear separation of concerns
- **Consistent patterns**: Repository, Strategy, Template Method
- **Documentation**: Comprehensive inline and external documentation

### Testability
- **Dependency injection**: Easy to mock dependencies
- **Interface-based design**: Test doubles can be easily created
- **Pure functions**: Domain logic is side-effect free

### Extensibility
- **Plugin architecture**: New iterators, processors, and services
- **Configuration-driven**: Behavior modification without code changes
- **Template system**: Customizable prompts and responses

### Performance
- **Lazy evaluation**: Iterators load tickets on demand
- **Filtering**: Pre-filter tickets to reduce LLM calls
- **Caching**: Future support for result caching

### Security
- **Credential management**: Environment-based configuration
- **Dry-run mode**: Safe testing without side effects
- **Input validation**: Sanitization of user inputs

## Future Architecture Evolution

### Planned Improvements

1. **Complete Application Layer**: Implement use cases for better orchestration
2. **Event-Driven Architecture**: Domain events for cross-cutting concerns
3. **Microservices Boundaries**: Split into focused services if needed
4. **Policy Engine**: Configurable rule system for governance
5. **Comprehensive Testing**: Unit, integration, and end-to-end tests

### Scalability Considerations

- **Horizontal scaling**: Stateless design supports multiple instances
- **Database integration**: Support for persistent state and caching
- **Message queues**: Asynchronous processing for large datasets
- **API gateway**: RESTful API for integration with other systems

## Conclusion

The Jira Cleanup project demonstrates strong architectural fundamentals with its clean architecture approach, rich domain model, and well-defined interfaces. The design supports the evolution from a client-specific solution to a general-purpose framework while maintaining flexibility, maintainability, and extensibility.

The architecture is well-positioned for future enhancements and can serve as a solid foundation for enterprise-grade Jira governance solutions.
