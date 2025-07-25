# Dead Code Cleanup Plan

## 🎯 **Analysis Summary**

After analyzing the codebase, I've identified several areas of dead/superseded code that should be removed to clean up the repository.

## 📋 **Dead Code Identified**

### **1. Superseded CLI Implementation**
- **File**: `src/jiraclean/main.py` (300+ lines)
- **Status**: ❌ **DEAD CODE** - Completely superseded
- **Reason**: Old argparse-based CLI completely replaced by new Typer-based CLI in `src/jiraclean/cli/`
- **Current Entry Point**: `src/jiraclean/cli/main.py` (used by pyproject.toml)

### **2. Unused Domain/Infrastructure Architecture**
- **Status**: ❌ **DEAD CODE** - Not used by current CLI
- **Files**:
  - `src/jiraclean/domain/` (entire directory)
  - `src/jiraclean/infrastructure/` (entire directory)
- **Reason**: The current working CLI uses the simpler `core/processor.py` and doesn't use the complex domain/infrastructure pattern

### **3. Duplicate Utilities**
- **File**: `src/jiraclean/utils/formatters.py`
- **Status**: ❌ **POTENTIALLY DEAD** - May duplicate `src/jiraclean/ui/formatters.py`
- **Reason**: UI formatters are being used by current CLI

### **4. Old Configuration Functions**
- **File**: `src/jiraclean/utils/config.py`
- **Functions**: `setup_argument_parser()`, `load_environment_config()` (old versions)
- **Status**: ❌ **PARTIALLY DEAD** - Some functions superseded by new YAML config system

## 🔧 **Current Working Architecture**

**✅ ACTIVE CODE (Keep):**
- `src/jiraclean/cli/` - New Typer-based CLI
- `src/jiraclean/core/processor.py` - Current processor implementation
- `src/jiraclean/ui/` - Rich UI components
- `src/jiraclean/jirautil/` - Jira client utilities
- `src/jiraclean/iterators/` - Ticket iteration logic
- `src/jiraclean/processors/` - Ticket processing logic
- `src/jiraclean/llm/` - LLM assessment logic
- `src/jiraclean/prompts/` - Prompt templates
- `src/jiraclean/utils/config.py` - New YAML configuration system

## 📊 **Impact Analysis**

### **Safe to Remove (No Dependencies):**
1. `src/jiraclean/main.py` - Old CLI entry point
2. `src/jiraclean/domain/` - Unused domain layer
3. `src/jiraclean/infrastructure/` - Unused infrastructure layer

### **Requires Verification:**
1. `src/jiraclean/utils/formatters.py` - Check if duplicates UI formatters

## 🚀 **Cleanup Benefits**

- **Reduce codebase size** by ~40% (removing unused domain/infrastructure)
- **Eliminate confusion** about which CLI to use
- **Simplify maintenance** by removing duplicate code paths
- **Improve clarity** of the actual working architecture

## ⚠️ **Cleanup Strategy**

1. **Phase 1**: Remove obviously dead code (old main.py)
2. **Phase 2**: Remove unused domain/infrastructure directories
3. **Phase 3**: Clean up duplicate utilities
4. **Phase 4**: Update documentation to reflect simplified architecture

## 🎯 **Estimated Impact**

- **Files to Remove**: ~15-20 files
- **Lines of Code Reduction**: ~1000+ lines
- **Risk Level**: Low (dead code not used by current CLI)
- **Testing Required**: Verify current CLI still works after cleanup
