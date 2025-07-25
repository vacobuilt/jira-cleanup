# LangChain Migration Checklist

## 🎯 **Objective**
Migrate from direct Ollama HTTP requests to LangChain for LLM connections, following KISS principles. This enables future multi-LLM configuration support while maintaining all existing functionality.

## 📋 **Migration Checklist**

### **Phase 1: Dependencies and Setup**
- [ ] **Add LangChain Dependencies**
  - [ ] Add `langchain-core` to pyproject.toml (core abstractions)
  - [ ] Add `langchain-ollama` to pyproject.toml (Ollama integration)
  - [ ] Add `langchain-openai` to pyproject.toml (future OpenAI support)
  - [ ] Update poetry.lock with `poetry install`
  - [ ] Verify dependencies install correctly

- [ ] **Update Configuration Schema**
  - [ ] Extend config.yaml to support multiple LLM providers
  - [ ] Add LLM provider configuration section
  - [ ] Maintain backward compatibility with existing config
  - [ ] Document new configuration options

### **Phase 2: LangChain Integration Layer**
- [ ] **Create LangChain LLM Factory**
  - [ ] Create `src/jiraclean/llm/langchain_factory.py`
  - [ ] Implement `create_llm()` function for different providers
  - [ ] Support Ollama provider initially
  - [ ] Add error handling and validation
  - [ ] Include provider-specific configuration

- [ ] **Create LangChain Service Wrapper**
  - [ ] Create `src/jiraclean/llm/langchain_service.py`
  - [ ] Implement unified interface for LLM calls
  - [ ] Maintain same API as current implementation
  - [ ] Add proper error handling and retries
  - [ ] Include logging and debugging support

### **Phase 3: Replace Current Implementation**
- [ ] **Update QuiescentTicketProcessor**
  - [ ] Replace direct HTTP calls with LangChain service
  - [ ] Maintain existing prompt formatting
  - [ ] Preserve all current functionality
  - [ ] Keep same response parsing logic
  - [ ] Ensure backward compatibility

- [ ] **Update LLM Assessment Module**
  - [ ] Modify `src/jiraclean/llm/assessment.py` if needed
  - [ ] Ensure AssessmentResult class remains unchanged
  - [ ] Maintain existing error handling patterns
  - [ ] Preserve response validation logic

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
    openai:  # Future support
      type: "openai"
      api_key: "${OPENAI_API_KEY}"
      models:
        - name: "gpt-4"
          alias: "gpt4"
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
