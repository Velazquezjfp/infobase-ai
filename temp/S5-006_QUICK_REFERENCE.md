# S5-006 Quick Reference - For Next Session

## TL;DR - What to Do

**Goal:** Test anonymization creates renders (not duplicate files) using Playwright MCP

**Test URL:** http://localhost:8080

**Test Case:** ACTE-2024-001 → Personal Data folder → Personalausweis.png

**Expected:** After clicking "Anonymize", document becomes expandable container showing "Original" and "Anonymized" renders with badge "2 renders"

---

## Playwright MCP Commands (Quick Copy-Paste)

```javascript
// Navigate and setup
await page.goto('http://localhost:8080');
await page.waitForSelector('[data-testid="fall-explorer"]');

// Open Personal Data folder
await page.locator('text=Persönliche Daten').click();

// Click Personalausweis document
await page.locator('text=Personalausweis.png').click();

// Click Anonymize button
await page.locator('button:has-text("Anonymize")').click();

// Wait for completion
await page.waitForSelector('text=Anonymization Complete', { timeout: 15000 });
await page.waitForTimeout(1000);

// Verify render container
const badge = page.locator('text=/2 renders/i');
await expect(badge).toBeVisible();

// Expand and verify
await page.locator('[class*="ChevronRight"]').first().click();
await expect(page.locator('text=Original')).toBeVisible();
await expect(page.locator('text=Anonymized')).toBeVisible();

// Verify NO duplicate file
await expect(page.locator('text=Personalausweis_anonymized.png')).not.toBeVisible();
```

---

## Quick Debugging Commands

```bash
# Check manifest has renders
cat backend/data/document_manifest.json | jq '.documents[] | select(.fileName == "Personalausweis.png") | .renders'

# Test API endpoint
curl http://localhost:8000/api/documents/tree/ACTE-2024-001 | jq '.folders[].documents[] | select(.name == "Personalausweis.png")'

# Check files on disk
ls -la public/documents/ACTE-2024-001/personal-data/Personalausweis*
```

---

## Key Implementation Points (All Complete)

✅ **Backend:** document_registry.py has `add_render_to_document()` (line 717)
✅ **Backend:** file_service.py calls registry functions (line 542)
✅ **Backend:** anonymization_tool.py registers renders (line 245)
✅ **Backend:** chat.py passes documentId (line 461, 493)
✅ **Backend:** documents.py API includes renders (line 314)
✅ **Frontend:** AppContext maps renders (line 440)
✅ **Frontend:** RenderContainer component (line 81-157)
✅ **Frontend:** WebSocket handler adds renders (line 584-627)
✅ **Frontend:** DocumentViewer sends documentId (line 119)

---

## What Should Happen (Visual Guide)

**BEFORE Anonymization:**
```
📄 Personalausweis.png
```

**AFTER Anonymization:**
```
▶ 📄 Personalausweis.png [2 renders]
```

**When Expanded:**
```
▼ 📄 Personalausweis.png [2 renders]
    📄 Original
    🔒 Anonymized [🗑️ on hover]
```

**Should NOT see:**
```
❌ Personalausweis.png
❌ Personalausweis_anonymized.png
```

---

## Critical Files Modified (8 files)

1. `src/types/case.ts` - Added DocumentRender interface
2. `src/types/websocket.ts` - Added documentId, renderMetadata fields
3. `src/contexts/AppContext.tsx` - Render state, WebSocket handler, data loading
4. `src/components/workspace/CaseTreeExplorer.tsx` - RenderContainer component
5. `src/components/workspace/DocumentViewer.tsx` - Send documentId
6. `backend/services/document_registry.py` - Render management functions
7. `backend/services/file_service.py` - Render wrapper functions
8. `backend/tools/anonymization_tool.py` - Render registration
9. `backend/api/chat.py` - WebSocket handler
10. `backend/api/documents.py` - API includes renders

---

## If Test Fails, Check:

1. **Backend logs** - Look for "Added anonymized render to document"
2. **Browser console** - Look for "Loaded document tree from backend"
3. **Network tab** - Check `/api/documents/tree/` response has `renders` array
4. **Manifest file** - Should have `renders` array in document entry
5. **WebSocket** - Response should include `renderMetadata` and `documentId`

---

## Full Documentation

See: `/temp/S5-006_TESTING_GUIDE.md` for complete details

---

**Ready to test? Start Playwright MCP and run the test commands above!**
