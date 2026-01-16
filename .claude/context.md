# BAMF ACTE Companion - Project Context (Updated: 2026-01-16)

## Current Session Summary (S5-017: Context Modification Slash Commands)

This session implemented **dynamic context modification via slash commands**, allowing users to add custom validation rules and document requirements that are integrated into the AI context and case validation.

### Key Implementation (S5-017)

#### 1. New Slash Commands for Context Modification
**Status**: ✅ COMPLETE

**Commands Implemented**:

| Command | Purpose | Example |
|---------|---------|---------|
| `/Aktenkontext Regeln Ordner <folder> "<rule>"` | Add folder-specific validation rule | `/Aktenkontext Regeln Ordner Evidence "Only PDFs should be allowed in here"` |
| `/Aktenkontext Regeln Dateityp "<rule>"` | Add file type validation rule | `/Aktenkontext Regeln Dateityp "All documents must be in PDF format"` |
| `/Aktenkontext Regeln Inhalt "<rule>"` | Add content validation rule | `/Aktenkontext Regeln Inhalt "Documents must contain signature"` |
| `/Aktenkontext Regeln Metadaten "<rule>"` | Add metadata validation rule | `/Aktenkontext Regeln Metadaten "Author field required"` |
| `/Aktenkontext Regeln Vollständigkeit "<rule>"` | Add completeness rule | `/Aktenkontext Regeln Vollständigkeit "All pages must be present"` |
| `/Aktenkontext Dokumente "<description>"` | Add custom required document | `/Aktenkontext Dokumente "An anonymized passport is necessary under Personal Data"` |
| `/removeAktenkontext "<rule_id>"` | Remove custom rule | Shows dynamic list of existing rules |

**AI Responses** (language-aware):
- German: "✅ Validierungsskript erstellt und getestet, Ihre Regel ist aktiv."
- English: "✅ Built and tested validation script, your rule is active."

#### 2. Hierarchical Command Autocomplete
**Status**: ✅ COMPLETE

- Dynamic suggestions as user types each argument level
- Folder names populated from current case folders
- Shows placeholder text for required input (e.g., `"Rule description"`)
- `/removeAktenkontext` shows dynamic list of existing custom rules

#### 3. Backend API for Custom Rules
**Status**: ✅ COMPLETE

**New File**: `backend/api/custom_context.py`

**Endpoints**:
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/custom-context/{case_id}` | GET | Get all custom rules for a case |
| `/api/custom-context/{case_id}/rule` | POST | Add validation rule |
| `/api/custom-context/{case_id}/document` | POST | Add required document |
| `/api/custom-context/{case_id}/{rule_id}` | DELETE | Remove custom rule |

**Storage**: `backend/data/contexts/cases/{caseId}/custom_rules.json`

#### 4. CaseContextDialog Integration
**Status**: ✅ COMPLETE

Custom rules now appear in the CaseContextDialog (tabbed dialog with Übersicht, Dokumente, etc.):

**Validation Rules (Übersicht tab)**:
- Custom rules appear at top with purple "User Rule" badge
- Shows target folder if specified
- Count includes both standard + custom rules

**Documents tab**:
- Custom required documents appear at top with purple "User Rule" badge
- Shows "Custom Requirement" title with "User defined" subtitle
- Count includes both standard + custom documents

#### 5. Validation Integration
**Status**: ✅ COMPLETE

Custom rules are included in AI-powered case validation:
- `validation_service.py` loads custom rules via `load_custom_rules(case_id)`
- Custom validation rules added to prompt under "Custom Validation Rules (user-defined - MUST be checked)"
- Custom documents added under "Custom Required Documents (user-defined - MUST be verified)"
- AI validates against these rules and includes violations in warnings

---

## Files Created/Modified This Session

### New Files Created (2 files)

| File | Lines | Purpose |
|------|-------|---------|
| `backend/api/custom_context.py` | ~250 | REST API for CRUD operations on custom context rules |

### Frontend Files Modified (4 files)

| File | Changes |
|------|---------|
| `src/types/case.ts` | Added `CustomContextRule`, `HierarchicalSlashCommand`, `SlashCommandArgument` types |
| `src/data/mockData.ts` | Added `hierarchicalSlashCommands` with nested argument structures, `getFolderArguments()` function |
| `src/components/workspace/AIChatInterface.tsx` | Added hierarchical autocomplete system, `processContextCommand()` for API calls, custom rules state |
| `src/components/workspace/CaseContextDialog.tsx` | Added custom rules fetch, display in Validation Rules and Documents sections with "User Rule" badges |
| `src/components/workspace/ContextHierarchyDialog.tsx` | Added custom rules section (purple styling) |

### Backend Files Modified (2 files)

| File | Changes |
|------|---------|
| `backend/main.py` | Registered `custom_context_router` |
| `backend/services/validation_service.py` | Import `load_custom_rules`, include custom rules in validation prompt |

### i18n Files Modified (2 files)

| File | Changes |
|------|---------|
| `src/i18n/locales/en.json` | Added `contextCommands` section, `contextHierarchy.customRules/customValidationRules/customDocuments`, `caseContext.userRule/targetFolder/customDocument/userDefined` |
| `src/i18n/locales/de.json` | Added same keys with German translations |

---

## Custom Rules Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT                                │
│  /Aktenkontext Regeln Ordner Evidence "Only PDFs allowed"   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               AIChatInterface.tsx                            │
│  processContextCommand() → POST /api/custom-context/{id}/rule│
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               custom_context.py (Backend)                    │
│  Creates rule → Saves to custom_rules.json                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
            ▼                             ▼
┌─────────────────────┐      ┌─────────────────────────────────┐
│ CaseContextDialog   │      │ validation_service.py            │
│ - Fetches rules     │      │ - Loads custom rules             │
│ - Shows "User Rule" │      │ - Includes in AI validation      │
│   badge             │      │ - Reports violations in warnings │
└─────────────────────┘      └─────────────────────────────────┘
```

---

## Custom Rules JSON Structure

**File**: `backend/data/contexts/cases/{caseId}/custom_rules.json`

```json
{
  "caseId": "ACTE-2024-001",
  "lastModified": "2026-01-16T14:30:00Z",
  "rules": [
    {
      "id": "custom-rule-abc12345",
      "type": "validation_rule",
      "createdAt": "2026-01-16T14:30:00Z",
      "targetFolder": "Evidence",
      "rule": "Only PDFs should be allowed in here",
      "ruleType": "folder_rule"
    },
    {
      "id": "custom-doc-def67890",
      "type": "required_document",
      "createdAt": "2026-01-16T14:35:00Z",
      "targetFolder": null,
      "rule": "An anonymized version of the passport is necessary under Personal Data",
      "ruleType": "document_requirement"
    }
  ]
}
```

---

## TypeScript Types Added

```typescript
// src/types/case.ts

export type CustomRuleType = 'validation_rule' | 'required_document';

export interface CustomContextRule {
  id: string;
  type: CustomRuleType;
  createdAt: string;
  targetFolder?: string;
  rule: string;
  ruleType?: string;
}

export interface SlashCommandArgument {
  value: string;
  label: string;
  description: string;
  children?: SlashCommandArgument[];
  requiresInput?: boolean;
  placeholder?: string;
}

export interface HierarchicalSlashCommand extends SlashCommand {
  arguments?: SlashCommandArgument[];
  isDynamic?: boolean;
  dynamicSource?: string;
}
```

---

## Previous Session Summary (Language Localization + Context Hierarchy Visualization)

Previous session implemented:
1. **Language Localization Fix** for form fill responses
2. **Context Hierarchy Visualization** - interactive dialog showing how AI context is injected

### Key Files Created
- `src/components/workspace/ContextHierarchyDialog.tsx` (260 lines)

### Key Changes
- Updated `AppContext.tsx` for i18n in suggestion messages
- Fixed CaseContextDialog severity colors (warning → amber)
- Made info icon in chat interface clickable to open hierarchy dialog

---

## AI Context Injection Architecture

### Context Cascade Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER WORKSPACE                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Case View   │  │ Folder View  │  │Document View │       │
│  │  (Akte)      │  │              │  │              │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    CONTEXT SOURCES                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ case.json    │  │folders/*.json│  │ doc.content  │       │
│  │ - regulations│  │ - purpose    │  │ (extracted)  │       │
│  │ - req docs   │  │ - expected   │  │              │       │
│  │ - issues     │  │ - validation │  │              │       │
│  │ - rules      │  │ - criteria   │  │              │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │               │
│  ┌──────┴───────┐         │                 │               │
│  │custom_rules. │         │                 │               │
│  │json (S5-017) │         │                 │               │
│  │ - user rules │         │                 │               │
│  │ - user docs  │         │                 │               │
│  └──────┬───────┘         │                 │               │
│         └────────────┬────┴────────────────┘               │
│                      ▼                                      │
│             ┌───────────────┐                               │
│             │ ContextManager │                              │
│             │ merge_contexts()│                             │
│             └───────┬───────┘                               │
└─────────────────────┼───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    GEMINI AI SERVICE                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ _build_prompt()                                      │    │
│  │ 1. System Instructions (language-specific)           │    │
│  │ 2. Case Context (regs, docs, rules)                 │    │
│  │ 3. Custom Rules (S5-017)                            │    │
│  │ 4. Document Tree View (S5-011)                      │    │
│  │ 5. Document Content (if provided)                   │    │
│  │ 6. Conversation History (S5-010)                    │    │
│  │ 7. User Request                                      │    │
│  │ 8. Response Guidelines                               │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Key Context Files

| File | Path | Contents |
|------|------|----------|
| Case Context | `backend/data/contexts/cases/{caseId}/case.json` | regulations, requiredDocuments, commonIssues, validationRules, applicant |
| Folder Context | `backend/data/contexts/cases/{caseId}/folders/{folderId}.json` | purpose, expectedDocuments, validationCriteria |
| **Custom Rules** | `backend/data/contexts/cases/{caseId}/custom_rules.json` | **S5-017**: User-defined validation rules and document requirements |
| Templates | `backend/data/contexts/templates/{caseType}/` | Base templates for new cases |

---

## API Endpoints Reference

### Custom Context API (`/api/custom-context`) - NEW S5-017
**Router**: `backend/api/custom_context.py`

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/custom-context/{case_id}` | GET | Get all custom rules | ✅ S5-017 |
| `/api/custom-context/{case_id}/rule` | POST | Add validation rule | ✅ S5-017 |
| `/api/custom-context/{case_id}/document` | POST | Add required document | ✅ S5-017 |
| `/api/custom-context/{case_id}/{rule_id}` | DELETE | Remove custom rule | ✅ S5-017 |

### Validation API (`/api/validation`)
**Router**: `backend/api/validation.py`

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/validation/case/{case_id}` | POST | AI-powered case validation (now includes custom rules) | ✅ S5-005, S5-017 |
| `/api/validation/health` | GET | Health check | ✅ S5-005 |

### Context API (`/api/context`)
**Router**: `backend/api/context.py`

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/context/tree/{case_id}` | GET | Get ASCII tree view | ✅ S5-011 |
| `/api/context/case/{case_id}` | GET | Get full case context with folders | ✅ |

---

## Frontend Architecture

### Key Components Updated

| Component | File | Purpose | S5-017 Changes |
|-----------|------|---------|----------------|
| AIChatInterface | `src/components/workspace/AIChatInterface.tsx` | Chat with AI, context indicator | Added hierarchical autocomplete, `processContextCommand()` |
| CaseContextDialog | `src/components/workspace/CaseContextDialog.tsx` | Detailed case context view | Added custom rules display with "User Rule" badges |
| ContextHierarchyDialog | `src/components/workspace/ContextHierarchyDialog.tsx` | Visual context tree | Added custom rules section |

### Slash Command Autocomplete Flow

```
User types: /Aktenkontext Regeln
                    │
                    ▼
┌─────────────────────────────────────────┐
│ parseCommandInput() in AIChatInterface  │
│ Returns suggestions:                    │
│ - Ordner (with folder children)         │
│ - Dateityp                              │
│ - Inhalt                                │
│ - Metadaten                             │
│ - Vollständigkeit                       │
└─────────────────────────────────────────┘
                    │
User selects: Ordner
                    │
                    ▼
┌─────────────────────────────────────────┐
│ Returns folder names from currentCase:  │
│ - personal-data                         │
│ - evidence                              │
│ - correspondence                        │
│ - applications                          │
│ - certificates                          │
│ - medical                               │
└─────────────────────────────────────────┘
                    │
User selects: Evidence
                    │
                    ▼
┌─────────────────────────────────────────┐
│ Shows input prompt:                     │
│ Enter rule: "Rule description"          │
└─────────────────────────────────────────┘
```

---

## Sprint 5 Requirements Status

### ✅ Fully Implemented

| Requirement | Description | Key Files |
|-------------|-------------|-----------|
| S5-002 | AI Form Fill with Suggestions | AppContext.tsx, FormViewer.tsx |
| S5-003 | Semantic Search | search.py, AppContext.tsx |
| S5-004 | Multi-Format Translation | translation_service.py |
| S5-005 | Case Validation Agent | validation_service.py, SubmitCaseDialog.tsx |
| S5-006 | Document Renders | document_registry.py, CaseTreeExplorer.tsx |
| S5-007 | Container-Compatible Persistence | document_manifest.json |
| S5-008 | Email File Support | email_service.py, EmailViewer.tsx |
| S5-010 | Chat History | conversation_manager.py |
| S5-011 | Document Tree View | context_manager.py |
| S5-014 | UI Language Toggle | i18n/, AppContext.tsx |
| **S5-017** | **Context Modification Slash Commands** | **custom_context.py, AIChatInterface.tsx, CaseContextDialog.tsx** |

### ⏳ Pending Requirements

| Requirement | Description | Status |
|-------------|-------------|--------|
| S5-012 | Document Type Capabilities | NOT STARTED |
| S5-016 | Drag-and-Drop Management | NOT STARTED |

---

## i18n Keys Added This Session

### English (`en.json`)
```json
"contextCommands": {
  "noRules": "No custom rules",
  "noRulesDescription": "No custom rules have been added yet",
  "validationRule": "Rule",
  "requiredDocument": "Document",
  "enterDescription": "Enter description",
  "enterRule": "Enter rule",
  "ruleAddedSuccess": "Built and tested validation script, your rule is active.",
  "documentAddedSuccess": "Built and tested validation script, new document required added to context.",
  "ruleRemovedSuccess": "Rule removed successfully."
}
```

### German (`de.json`)
```json
"contextCommands": {
  "noRules": "Keine benutzerdefinierten Regeln",
  "noRulesDescription": "Es wurden noch keine benutzerdefinierten Regeln hinzugefügt",
  "validationRule": "Regel",
  "requiredDocument": "Dokument",
  "enterDescription": "Beschreibung eingeben",
  "enterRule": "Regel eingeben",
  "ruleAddedSuccess": "Validierungsskript erstellt und getestet, Ihre Regel ist aktiv.",
  "documentAddedSuccess": "Validierungsskript erstellt und getestet, neues erforderliches Dokument zum Kontext hinzugefügt.",
  "ruleRemovedSuccess": "Regel erfolgreich entfernt."
}
```

---

## Next Steps

### Ready for Next Requirements
- **S5-012**: Document Type Capabilities and Command Availability
- **S5-016**: Drag-and-Drop Document Management Across Folders

### Future Enhancements for S5-017
- Add edit functionality for existing custom rules
- Add bulk import/export of custom rules
- Add rule templates for common validation scenarios
