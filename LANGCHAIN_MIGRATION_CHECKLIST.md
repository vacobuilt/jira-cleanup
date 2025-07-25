# LangChain Migration Checklist

## 🎯 **Objective**
Migrate from direct Ollama HTTP requests to LangChain for LLM connections, following KISS principles. This enables future multi-LLM configuration support while maintaining all existing functionality.

## 📋 **Migration Checklist**

### **Phase 1: Dependencies and Setup**
- [x] **Add LangChain Dependencies**
  - [x] Add `langchain-core >= 0.3.27` to pyproject.toml (core abstractions)
  - [x] Add `langchain-ollama >= 0.3.6` to pyproject.toml (Ollama integration)
  - [x] Add `langchain-openai >= 0.3.28` to pyproject.toml (OpenAI support)
  - [x] Add `langchain-anthropic >= 0.3.17` to pyproject.toml (Claude support)
  - [x] Add `langchain-google-genai >= 2.1.8` to pyproject.toml (Gemini support)
  - [x] Update poetry.lock with `poetry update`
  - [x] Verify dependencies install correctly

- [ ] **Update Configuration Schema**
  - [ ] Extend config.yaml to support multiple LLM providers
  - [ ] Add LLM provider configuration section
  - [ ] Maintain backward compatibility with existing config
  - [ ] Document new configuration options

### **Phase 2: LangChain Integration Layer**
- [x] **Create LangChain LLM Factory**
  - [x] Create `src/jiraclean/llm/langchain_factory.py`
  - [x] Implement `create_llm()` function for different providers
  - [x] Support Ollama provider initially
  - [x] Add error handling and validation
  - [x] Include provider-specific configuration

- [x] **Create LangChain Service Wrapper**
  - [x] Create `src/jiraclean/llm/langchain_service.py`
  - [x] Implement unified interface for LLM calls
  - [x] Maintain same API as current implementation
  - [x] Add proper error handling and retries
  - [x] Include logging and debugging support

### **Phase 3: Create Clean Business Logic Layer**
- [x] **Create TicketAnalyzer (Business Logic)**
  - [x] Create `src/jiraclean/analysis/ticket_analyzer.py`
  - [x] Move prompt building logic from assessment.py
  - [x] Move response parsing and sanitization logic
  - [x] Implement retry logic with enhanced JSON instructions
  - [x] Use dependency injection for LangChain service

- [x] **Refactor Assessment Module**
  - [x] Remove HTTP client code from `src/jiraclean/llm/assessment.py`
  - [x] Keep AssessmentResult class (moved to shared entities)
  - [x] Create clean re-export module for AssessmentResult
  - [x] No backward compatibility needed (clean implementation)
  - [x] Remove `call_ollama_api()` and related HTTP code

- [x] **Resolve Circular Import**
  - [x] Create shared entities module (`src/jiraclean/entities/`)
  - [x] Move AssessmentResult to entities/assessment.py
  - [x] Update all imports to use shared entity
  - [x] Test application functionality

### **Phase 4: Configuration Updates**
- [ ] **Extend Configuration Management**
  - [ ] Update `src/jiraclean/utils/config.py`
  - [ ] Add LLM provider configuration loading
  - [ ] Support multiple named LLM configurations
  - [ ] Maintain default behavior for existing configs
  - [ ] Add validation for LLM provider settings

- [ ] **Update CLI Integration**
  - [ ] Modify CLI to support LLM provider selection
  - [ ] Add `--llm-provider` parameter (optional)
  - [ ] Maintain existing `--llm-model` parameter
  - [ ] Ensure backward compatibility with existing commands
  - [ ] Update help text and documentation

### **Phase 5: Testing and Validation**
- [ ] **Unit Testing**
  - [ ] Test LangChain factory with different providers
  - [ ] Test service wrapper functionality
  - [ ] Test configuration loading and validation
  - [ ] Test error handling scenarios
  - [ ] Verify backward compatibility

- [ ] **Integration Testing**
  - [ ] Test with existing Ollama setup
  - [ ] Verify CLI commands work unchanged
  - [ ] Test dry-run and production modes
  - [ ] Validate multi-instance Jira support still works
  - [ ] Confirm LLM assessment output is identical

- [ ] **End-to-End Testing**
  - [ ] Run full ticket processing pipeline
  - [ ] Test with real Jira tickets
  - [ ] Verify Rich UI output remains unchanged
  - [ ] Confirm performance is acceptable
  - [ ] Test error scenarios and recovery

### **Phase 6: Documentation and Cleanup**
- [ ] **Update Documentation**
  - [ ] Update README.md with new LLM configuration
  - [ ] Document multiple LLM provider support
  - [ ] Update configuration examples
  - [ ] Add troubleshooting guide for LangChain issues
  - [ ] Update API documentation

- [ ] **Code Cleanup**
  - [ ] Remove old HTTP client code (if no longer needed)
  - [ ] Clean up unused imports
  - [ ] Update type hints and docstrings
  - [ ] Ensure consistent error handling
  - [ ] Add deprecation warnings if needed

## 🔧 **Technical Implementation Details**

### **New Configuration Structure**
```yaml
llm:
  default_provider: "ollama"
  providers:
    ollama:
      type: "ollama"
      base_url: "http://localhost:11434"
      models:
        - name: "llama3.2:latest"
          alias: "default"
        - name: "codellama:latest"
          alias: "code"
    openai:
      type: "openai"
      api_key: "${OPENAI_API_KEY}"
      models:
        - name: "gpt-4"
          alias: "gpt4"
        - name: "gpt-3.5-turbo"
          alias: "gpt35"
    anthropic:
      type: "anthropic"
      api_key: "${ANTHROPIC_API_KEY}"
      models:
        - name: "claude-3-5-sonnet-20241022"
          alias: "claude"
        - name: "claude-3-haiku-20240307"
          alias: "claude-haiku"
    google:
      type: "google-genai"
      api_key: "${GOOGLE_API_KEY}"
      models:
        - name: "gemini-1.5-pro"
          alias: "gemini-pro"
        - name: "gemini-1.5-flash"
          alias: "gemini-flash"
```

### **LangChain Factory Interface**
```python
def create_llm(provider: str, model: str, config: Dict[str, Any]) -> BaseLLM:
    """Create LangChain LLM instance for specified provider."""
    
def get_available_providers() -> List[str]:
    """Get list of available LLM providers."""
    
def validate_provider_config(provider: str, config: Dict[str, Any]) -> bool:
    """Validate provider-specific configuration."""
```

### **Service Wrapper Interface**
```python
class LangChainLLMService:
    def __init__(self, provider: str, model: str, config: Dict[str, Any]):
        """Initialize with LangChain LLM instance."""
    
    def generate_response(self, prompt: str) -> str:
        """Generate response maintaining current API."""
    
    def validate_connection(self) -> bool:
        """Test LLM connection."""
```

## 🎯 **Success Criteria**

### **Functional Requirements**
- [ ] All existing CLI commands work unchanged
- [ ] LLM assessment produces identical results
- [ ] Performance is equivalent or better
- [ ] Error handling is improved or equivalent
- [ ] Configuration is backward compatible

### **Technical Requirements**
- [ ] Code follows KISS principles
- [ ] No breaking changes to existing APIs
- [ ] Proper error handling and logging
- [ ] Type hints and documentation complete
- [ ] Test coverage maintained or improved

### **Future Enablement**
- [ ] Easy to add new LLM providers
- [ ] Configuration supports multiple named LLMs
- [ ] Foundation for LangGraph integration
- [ ] Extensible architecture for advanced features

## 🚀 **Implementation Order**

1. **Start with Dependencies** - Add LangChain packages
2. **Create Factory** - Build LLM creation abstraction
3. **Create Service** - Wrap LangChain with current API
4. **Replace Gradually** - Update one component at a time
5. **Test Thoroughly** - Verify each step works
6. **Document Changes** - Update all documentation

## ⚠️ **Risk Mitigation**

### **Backward Compatibility**
- Maintain existing configuration format support
- Keep current CLI parameter behavior
- Preserve all existing functionality
- Add feature flags for gradual rollout

### **Performance Considerations**
- Monitor LLM response times
- Implement connection pooling if needed
- Add timeout and retry logic
- Cache LLM instances where appropriate

### **Error Handling**
- Graceful fallback for LangChain failures
- Clear error messages for configuration issues
- Proper logging for debugging
- Maintain existing error recovery patterns

## 📊 **Validation Commands**

```bash
# Test existing functionality still works
jiraclean --project NEMS --max-tickets 1 --dry-run

# Test with specific LLM model
jiraclean --project NEMS --llm-model llama3.2:latest --dry-run

# Test configuration validation
jiraclean config show

# Test multi-instance support
jiraclean --instance personal --project FORGE --dry-run
```

## 🎯 **Definition of Done**

- [ ] All checklist items completed
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Code reviewed and approved
- [ ] Performance validated
- [ ] Backward compatibility confirmed
- [ ] Ready for multi-LLM configuration feature

This migration maintains KISS principles while providing the foundation for advanced LLM configuration and future LangGraph integration.
