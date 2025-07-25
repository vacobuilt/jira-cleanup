# Multi-Instance Jira Configuration Completion Checklist

## 🎯 **Current Status**
✅ **COMPLETED:**
- YAML configuration system with multiple instances (trilliant, personal, highspring)
- Configuration loading with fallback to .env files
- Clean CLI output without debug clutter
- All credential data properly configured in config.yaml
- Configuration validation and error handling
- Helper functions: `get_instance_config()`, `list_instances()`

❌ **REMAINING WORK:**
The CLI is still using the old single-instance approach. Need to integrate the new multi-instance system.

---

## 📋 **Implementation Checklist**

### **Phase 1: CLI Integration** ✅ **COMPLETED**
- [x] **Add `--instance` parameter** to main CLI command in `src/jiraclean/cli/commands.py`
  - Add to `main()` function parameters
  - Set default to use `config.get('default_instance')`
  - Add choices validation from available instances

- [x] **Update main processing function** `_run_main_processing()`
  - Add `instance` parameter
  - Replace direct config access with `get_instance_config(config, instance)`
  - Update Jira client creation to use instance-specific credentials

- [x] **Fix config structure access** in main processing
  - Replace `config['jira']['url']` with `instance_config['url']`
  - Replace `config['jira']['username']` with `instance_config['username']`
  - Replace `config['jira']['token']` with `instance_config['token']`
  - Replace `config['jira']['auth_method']` with `instance_config['auth_method']`

### **Phase 2: Config Commands Enhancement**
- [ ] **Update `config list` command**
  - Use `list_instances(config)` to show all available instances
  - Display instance names, URLs, descriptions
  - Mark default instance clearly
  - Show beautiful Rich table format

- [ ] **Update `config show` command**
  - Add optional `--instance` parameter
  - Show specific instance details or default
  - Display instance-specific settings vs global settings

- [ ] **Update `config test` command**
  - Make instance parameter required
  - Use `get_instance_config()` to get instance credentials
  - Test connection to specific instance

### **Phase 3: Settings Integration**
- [ ] **Update settings access patterns**
  - Replace `config['defaults']` with `config['settings']['defaults']`
  - Replace `config['logging']` with `config['settings']['logging']`
  - Update LLM settings access to use `config['settings']['llm']`

- [ ] **Fix validation function**
  - Update `validate_config()` to work with new structure
  - Add instance parameter to validation
  - Validate selected instance exists

### **Phase 4: Error Handling & UX**
- [ ] **Add instance validation**
  - Check if specified instance exists
  - Provide helpful error messages with available instances
  - Handle missing instance gracefully

- [ ] **Update help text and examples**
  - Add `--instance` examples to CLI help
  - Update documentation with multi-instance usage
  - Add instance selection to quick examples

### **Phase 5: Testing & Validation**
- [ ] **Test each instance**
  - `jiraclean --instance trilliant --project NEMS --dry-run --max-tickets 1`
  - `jiraclean --instance personal --project TEST --dry-run --max-tickets 1`
  - `jiraclean --instance highspring --project VACO --dry-run --max-tickets 1`

- [ ] **Test config commands**
  - `jiraclean config list` - should show all 3 instances
  - `jiraclean config show` - should show default (trilliant)
  - `jiraclean config test trilliant` - should test connection

- [ ] **Test fallback behavior**
  - Rename config.yaml temporarily
  - Verify .env fallback still works
  - Restore config.yaml

---

## 🔧 **Specific Code Changes Needed**

### **1. CLI Main Command (src/jiraclean/cli/commands.py)**
```python
# Add to main() function parameters:
instance: Optional[str] = typer.Option(
    None,
    "--instance", "-i", 
    help="🏢 Jira instance to use (trilliant, personal, highspring)"
),

# In _run_main_processing():
# Replace config loading section with:
config = load_configuration(env_file=str(env_file) if env_file else None)
instance_config = get_instance_config(config, instance)

# Replace Jira client creation with:
jira_client = create_jira_client(
    url=instance_config['url'],
    auth_method=instance_config['auth_method'], 
    username=instance_config['username'],
    token=instance_config['token'],
    dry_run=dry_run
)
```

### **2. Config Commands Update**
```python
# config list command:
instances = list_instances(config)
for name, info in instances.items():
    default_marker = " (default)" if info['is_default'] else ""
    console.print(f"• {name}{default_marker}: {info['name']} - {info['url']}")

# config show command:
instance_config = get_instance_config(config, instance)
console.print(f"Instance: {instance or 'default'}")
console.print(f"URL: {instance_config['url']}")
console.print(f"Username: {instance_config['username']}")
```

### **3. Settings Access Pattern**
```python
# Replace throughout:
config['defaults'] → config['settings']['defaults']
config['logging'] → config['settings']['logging'] 
config.get('llm_model') → config['settings']['llm']['model']
config.get('ollama_url') → config['settings']['llm']['ollama_url']
```

---

## 🎯 **Expected Final Usage**

**Default instance (trilliant):**
```bash
jiraclean --project NEMS --dry-run
```

**Specific instance:**
```bash
jiraclean --instance personal --project MYPROJ --dry-run
jiraclean --instance highspring --project VACO --dry-run
```

**Config management:**
```bash
jiraclean config list                    # Show all instances
jiraclean config show                    # Show default instance  
jiraclean config show --instance personal # Show specific instance
jiraclean config test trilliant          # Test specific instance
```

---

## ⚡ **Estimated Effort**
- **Phase 1-2:** ~2-3 hours (core CLI integration)
- **Phase 3-4:** ~1-2 hours (settings & error handling)  
- **Phase 5:** ~1 hour (testing & validation)
- **Total:** ~4-6 hours of focused development

---

## 🚀 **Success Criteria**
- [ ] Can switch between all 3 Jira instances seamlessly
- [ ] Default behavior unchanged (uses trilliant)
- [ ] Config commands show multi-instance information
- [ ] All existing functionality preserved
- [ ] Clean error messages for invalid instances
- [ ] Backward compatibility with .env files maintained
