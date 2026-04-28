# Wave 2 — S001-F-003 Implementation Summary

**Requirement:** Render dynamic-context URLs as plain text in the closed environment
**Status:** implemented
**Tests:** 12 / 12 passed
**Date:** 2026-04-28

---

## What was changed

### `src/i18n/locales/de.json`
Added a new top-level `"context"` section with the offline disclaimer key:
```json
"context": {
  "offlineNotice": "Offline-Modus: Inhalt wird simuliert"
}
```

### `src/i18n/locales/en.json`
Same new section, English translation:
```json
"context": {
  "offlineNotice": "Offline mode: content is simulated"
}
```

### `src/components/workspace/ContextHierarchyDialog.tsx`
Three changes:

1. **`ContextNode` interface** — added `url?: string` field so regulation nodes can carry their URL through the tree.

2. **`buildContextTree`** — regulation node construction now passes `url: reg.url` alongside the existing `label`/`description` fields.

3. **`renderNode`** — immediately after a node is rendered, if `node.url` is set it renders two new lines:
   - `<span className="font-mono text-xs text-muted-foreground break-all">{node.url}</span>`
   - `<p className="text-xs text-muted-foreground/70 italic">{t('context.offlineNotice', ...)}</p>`

   No `<a>` element is produced anywhere in `renderNode`.

### `src/components/workspace/CaseContextDialog.tsx`
Two changes:

1. **Removed** the `ExternalLink` Lucide import (no longer used).

2. **Regulations tab** — replaced the `<a href target="_blank">` anchor for `reg.url` with a plain div:
   ```tsx
   <div className="flex flex-col items-end text-right max-w-[200px]">
     <span className="font-mono text-xs text-muted-foreground break-all">{reg.url}</span>
     <span className="text-xs text-muted-foreground/70 italic mt-0.5">
       {t('context.offlineNotice', 'Offline mode: content is simulated')}
     </span>
   </div>
   ```
   Right-click → "Open link" is now impossible — no `<a>` element exists.

### `backend/services/gemini_service.py` — `_load_context`
After `context_manager.merge_contexts(...)` returns the merged string, a new block scans `case_ctx['regulations']` for any entry with an `extractedText` field. If found, it appends a dedicated section to the merged context:

```
=== REGULATION CONTENT (pre-extracted) ===
  [§43_AufenthG] (source: https://...)
  <operator-supplied extracted text>
```

The URL appears only as a citation marker in parentheses. No HTTP request is made. Regulations without `extractedText` are silently skipped. The return signature `(merged_context, document_tree)` is unchanged, so both `generate_response` and `generate_response_stream` callers are unaffected.

---

## Test files created

| File | What it verifies |
|---|---|
| `docs/tests/S001-F-003/TC-S001-F-003-01.py` | TSX source inspection: `renderNode` has no `<a>` or `href`, uses `font-mono` span, `url` field is wired in interface and `buildContextTree` |
| `docs/tests/S001-F-003/TC-S001-F-003-02.py` | Both locale files have `context.offlineNotice` with exact strings; `CaseContextDialog` uses the key and has no `target="_blank"` or `ExternalLink` |
| `docs/tests/S001-F-003/TC-S001-F-003-03.py` | `_load_context` with fixture regulation carrying `extractedText` produces a merged context containing the extracted text; `_build_prompt` includes it in the final prompt |
| `docs/tests/S001-F-003/TC-S001-F-003-04.py` | Without `extractedText` no extra section is appended; no HTTP call is made (urllib.request.urlopen patched to raise) |
| `docs/tests/S001-F-003/TC-S001-F-003-05.py` | When `context.offlineNotice` is removed from both locales, i18next returns the key name `"context.offlineNotice"` rather than throwing (delegates to `_i18next_runner.mjs` from S001-F-008) |

---

## Scope notes

- No files were touched outside the requirement's `affected_surface`.
- `context_manager.py` was **not** modified — the regulation text injection happens entirely within `gemini_service.py::_load_context` as a post-processing step on the string returned by `merge_contexts`.
- The `GET /api/context/case/{case_id}` endpoint continues to return the raw `case.json` payload; `extractedText` is server-side only and never sent to the browser.
- No crawler, no HTTP fetch, no new dependency. The `extractedText` field is purely opt-in: the operator pre-populates it by hand in `case.json`.
