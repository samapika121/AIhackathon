# Ticket Link Setup Guide

## Current Issue
Your events don't have ticket links because your Google Sheet doesn't have a "Link" column yet, or it's using a different column name.

## Steps to Fix:

### Option 1: Add a "Link" Column to Your Google Sheet

1. **Open your Google Sheet** that feeds into n8n
2. **Add a new column** with one of these names (the app checks for all of these):
   - `Link`
   - `link`
   - `URL`
   - `url`
   - `Ticket Link`

3. **Fill in ticket URLs** for each event, for example:
   - `https://jira.company.com/browse/PROJ-123`
   - `https://confluence.company.com/page/event-details`
   - `https://docs.google.com/document/d/YOUR-DOC-ID`

4. **In the app**:
   - Click "🗑️ Clear All Events" button
   - Click "Fetch from n8n" to re-import
   - Check the console logs to see if links are being imported

### Option 2: Check Console Logs

After re-importing, check your browser console for:
```
Available properties: [list of columns from your sheet]
Checking for Link column: Link= ... link= ... URL= ...
```

This will tell you:
- What columns exist in your Google Sheet
- Whether link data is being found

### Expected Google Sheet Structure:

| Date | Fairs | Launches | PO 1 | PO 2 | ... | **Link** |
|------|-------|----------|------|------|-----|----------|
| 1 Jan, Wed | Fair1 | Event1 | - | Event2 | ... | https://ticket-url.com |

### What Happens When You Click 🔗:

- **If link exists**: Opens link in new tab ✅
- **If no link**: Shows alert to add link ❌

## Debug Process:

1. **Clear all events** (🗑️ Clear All Events button)
2. **Re-import** from n8n webhook
3. **Open browser console** (F12 or Cmd+Option+J on Mac)
4. **Look for logs** that show:
   - "Available properties: ..."
   - "Row X - Date: ..., Fair: ..., Link: ..."
5. **Share console output** if you need help identifying the column name
