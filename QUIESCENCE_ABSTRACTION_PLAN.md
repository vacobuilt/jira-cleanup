# Quiescence Abstraction Plan 🎯

## 🏗️ Architectural Guidance

**Core Principle**: Transform quiescence from a hardcoded framework assumption into a purely configurable analysis type, making it equal to all other analyzer types with no special treatment.

**Design Goal**: Any analyzer type (quiescent, quality, security, compliance) should be a first-class citizen in the framework with identical capabilities and no hardcoded assumptions.

## 🔍 Current Problems Identified

### 1. **AssessmentResult Entity - Quiescence-Centric**
- **Issue**: `is_quiescent` field forces all analyzers to map to quiescence concepts
- **Impact**: Quality analyzer must fake `is_quiescent` as `needs_improvement`
- **Problem**: Non-quiescence analyzers have to contort their results into quiescence terminology

### 2. **QuiescentTicketProcessor - Hardcoded Logic**
- **Issue**: Processor assumes `assessment.is_quiescent` field exists and has meaning
- **Impact**: Cannot work with non-quiescence analyzers naturally
- **Problem**: Statistics tracking assumes quiescence-specific metrics (`quiescent`, `non_quiescent`)

### 3. **Hardcoded Filtering Logic**
- **Issue**: `create_quiescence_prefilter()` assumes age/activity criteria specific to quiescence
- **Impact**: Other analyzer types cannot define their own filtering criteria
- **Problem**: `use_default_quiescence_filter` parameter hardcodes quiescence assumptions

### 4. **Core Processor Assumptions**
- **Issue**: Core processor specifically creates `QuiescentTicketProcessor`
- **Impact**: Framework is not truly analyzer-agnostic
- **Problem**: UI and statistics assume quiescence-specific data structures

## 🎯 Proposed Solution Architecture

### **Phase 1: Generic Assessment Results**

**Objective**: Replace quiescence-specific `AssessmentResult` with analyzer-agnostic result system

**Changes Required**:
- Create `BaseAssessmentResult` abstract interface
- Define common fields all analyzers need: `needs_action`, `justification`, `responsible_party`, `suggested_action`, `planned_comment`
- Create analyzer-specific result types:
  - `QuiescentAssessmentResult` with `is_quiescent` field
  - `QualityAssessmentResult` with `quality_score`, `needs_improvement` fields
  - Future: `SecurityAssessmentResult`, `ComplianceAssessmentResult`, etc.

**Benefits**:
- Each analyzer returns results in its natural terminology
- No forced mapping to quiescence concepts
- Type safety for analyzer-specific fields

### **Phase 2: Generic Ticket Processor**

**Objective**: Transform `QuiescentTicketProcessor` into `GenericTicketProcessor` that works with any analyzer

**Changes Required**:
- Rename `QuiescentTicketProcessor` → `GenericTicketProcessor`
- Replace hardcoded `assessment.is_quiescent` checks with generic `assessment.needs_action`
- Make statistics tracking configurable per analyzer type
- Remove quiescence-specific logging and action descriptions
- Make action logic configurable based on analyzer result type

**Benefits**:
- Single processor works with all analyzer types
- No quiescence assumptions in processing logic
- Configurable behavior per analyzer type

### **Phase 3: Configurable Filtering System**

**Objective**: Replace hardcoded quiescence filtering with analyzer-specific filter factories

**Changes Required**:
- Create `AnalyzerFilterFactory` interface
- Implement `QuiescentFilterFactory` (age + activity criteria)
- Implement `QualityFilterFactory` (different criteria, e.g., missing fields)
- Update `ProjectTicketIterator` to accept analyzer-specific filters
- Remove `use_default_quiescence_filter` parameter

**Benefits**:
- Each analyzer type can define its own prefiltering logic
- No hardcoded assumptions about what makes a ticket worth analyzing
- Extensible for future analyzer types with different criteria

### **Phase 4: Analyzer-Agnostic Core Orchestration**

**Objective**: Update core processor and UI to work generically with any analyzer type

**Changes Required**:
- Update `TicketProcessor` to create `GenericTicketProcessor` instead of `QuiescentTicketProcessor`
- Make statistics collection configurable per analyzer type
- Update UI components to display analyzer-agnostic results
- Make progress tracking and logging analyzer-neutral
- Update CLI help text to be analyzer-agnostic

**Benefits**:
- Core framework has no knowledge of specific analyzer types
- UI adapts automatically to different analyzer result types
- Adding new analyzer types requires no core framework changes

## 🔧 Implementation Details

### **File Changes Required**:

1. **src/jiraclean/entities/assessment.py**
   - Create `BaseAssessmentResult` interface
   - Create analyzer-specific result classes
   - Maintain backward compatibility with current `AssessmentResult`

2. **src/jiraclean/processors/quiescent.py**
   - Rename to `src/jiraclean/processors/generic.py`
   - Remove hardcoded quiescence logic
   - Make behavior configurable per analyzer type

3. **src/jiraclean/iterators/filters.py**
   - Create `AnalyzerFilterFactory` system
   - Implement analyzer-specific filter factories
   - Remove hardcoded quiescence assumptions

4. **src/jiraclean/analysis/base.py**
   - Add `get_filter_factory()` method to `BaseTicketAnalyzer`
   - Add `get_result_type()` method for type safety

5. **src/jiraclean/core/processor.py**
   - Update to use `GenericTicketProcessor`
   - Make statistics and UI configurable per analyzer

6. **src/jiraclean/ui/components.py**
   - Update to display analyzer-agnostic results
   - Make formatting adapt to different result types

### **Backward Compatibility Strategy**:
- Keep current `AssessmentResult` as alias to `QuiescentAssessmentResult`
- Maintain `QuiescentTicketProcessor` as alias to `GenericTicketProcessor` with quiescent defaults
- Ensure existing CLI commands work unchanged
- Gradual migration path for existing code

### **Testing Strategy**:
- Verify quiescent analysis works identically after refactoring
- Test quality analyzer with new generic processor
- Ensure UI displays correctly for both analyzer types
- Validate filtering works correctly for different analyzer types

## 🎯 Success Criteria

**After Implementation**:
1. ✅ Quiescence has no special treatment in the framework
2. ✅ Adding new analyzer types requires no core framework changes
3. ✅ Each analyzer type can define its own filtering criteria
4. ✅ Results are displayed in analyzer-appropriate terminology
5. ✅ Statistics and UI adapt automatically to different analyzer types
6. ✅ Backward compatibility maintained for existing usage

## 🚀 Future Extensibility

**With This Architecture**:
- **SecurityAnalyzer**: Could filter for tickets with security labels, return `SecurityAssessmentResult` with risk levels
- **ComplianceAnalyzer**: Could filter for regulatory tickets, return compliance status and required actions
- **PerformanceAnalyzer**: Could filter for performance-related tickets, return optimization recommendations
- **BusinessValueAnalyzer**: Could assess business impact and prioritization

**Each Would Be Equal Citizens**: No analyzer type would have special framework treatment, making the system truly extensible and maintainable.

## ⚠️ Risk Assessment

**Low Risk Changes**:
- Creating new result types (additive)
- Adding filter factories (additive)
- Updating UI to be more generic (improves flexibility)

**Medium Risk Changes**:
- Renaming `QuiescentTicketProcessor` (requires alias for compatibility)
- Changing core processor logic (needs thorough testing)

**High Risk Changes**:
- Modifying `AssessmentResult` structure (affects all existing code)

**Mitigation Strategy**: Implement with backward compatibility aliases and gradual migration path.
