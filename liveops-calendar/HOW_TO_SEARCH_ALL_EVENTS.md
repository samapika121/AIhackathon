# How to Search All Events and Sales from Google Sheet

## Quick Steps to See ALL Your Events

### Method 1: Show All Events (Easiest!)
1. Open your calendar app
2. Leave the search box **EMPTY**
3. Click the **"Search"** button
4. ✅ ALL imported events will appear!

### Method 2: Search by Name
1. Type "sale" to find all sales
2. Type "event" to find all events  
3. Type any keyword that appears in your event names

### Method 3: Check Upcoming Events List
- Scroll to the bottom
- "Upcoming Events" section shows all imported events
- Sorted by date

## Complete Workflow: Import → Search → View

### Step 1: Import Your Google Sheet

**Option A: Copy & Paste (Recommended)**
1. Open your Google Sheet: `https://docs.google.com/spreadsheets/d/19duXZN3PdqULWhc9Hx3Szxui0UmVlLMgFGR7tnBZaKQ/edit`
2. Select all data (Ctrl+A or Cmd+A)
3. Copy (Ctrl+C or Cmd+C)
4. Paste in the text area under "Method 1: Copy & Paste Directly"
5. Click **"Import from Paste"**
6. Wait for success message: "Successfully imported X event(s)!"

**Option B: Upload File**
1. Download Google Sheet as Excel (.xlsx)
2. Use "Method 2: Upload File"
3. Select the downloaded file
4. Click **"Import File"**

### Step 2: Verify Import (Open Console)
1. Press **F12** (opens Developer Tools)
2. Click **Console** tab
3. Look for:
   ```
   === IMPORT SUMMARY ===
   Imported: 25
   Skipped: 0
   Total events now: 25
   ```
4. This confirms all events are loaded

### Step 3: Search for ALL Events
1. **Leave search box empty**
2. Click **"Search"** button
3. See all 25 events (or however many you imported)
4. Click any event to jump to that month in calendar

### Step 4: Search Specific Events
- Type "sale" → See all sales events
- Type "winter" → See winter-related events
- Type "2024" → See events with 2024 in name
- Type "promo" → See promotion events

## Example: Your Google Sheet

If your sheet looks like:
```
Date          | Title
12/25/2024    | Christmas Sale
12/31/2024    | New Year Sale
01/15/2025    | Winter Launch Event
02/14/2025    | Valentine Sale
03/20/2025    | Spring Promotion
```

### To See ALL 5 Events:
- Leave search box empty → Click "Search" → Shows all 5

### To See ALL Sales:
- Type "sale" → Click "Search" → Shows 3 results (Christmas, New Year, Valentine)

### To See ALL Events:
- Type "event" → Click "Search" → Shows 1 result (Winter Launch Event)

### To See ALL 2025 Items:
- Type "2025" → Click "Search" → Shows 3 results (Winter, Valentine, Spring)

## Troubleshooting: "No events available"

### If clicking Search shows "No events available":

**1. Check if Import Succeeded**
- Did you see success message?
- Look for "Successfully imported X event(s)!"
- If not, import failed

**2. Open Console to Debug**
- Press F12
- Look at console logs during import
- Check for errors or "Skipped" messages

**3. Check Total Events**
- Open console (F12)
- Type: `events`
- Press Enter
- Should show array with your events
- If empty `[]`, nothing was imported

**4. Common Import Issues**

| Issue | Solution |
|-------|----------|
| No success message | Re-import your data |
| "Invalid date format" | Check date column has real dates |
| "Not enough columns" | Copy both Date AND Title columns |
| "Duplicate (skipped)" | Events already imported (this is OK) |

## Testing with Sample Data

Try this to test if search works:

1. Copy this data:
```
12/25/2024	Christmas Sale
01/15/2025	Winter Event
02/14/2025	Valentine Sale
```

2. Paste in the text area
3. Click "Import from Paste"
4. Should import 3 events
5. Click "Search" (empty box) → See all 3
6. Type "sale" → See 2 results
7. Type "event" → See 1 result

If this works → Your import/search is fine, just need to import your actual Google Sheet
If this doesn't work → There's a technical issue

## What Search Actually Does

### Empty Search = Show ALL
- Query: (empty)
- Results: Every single imported event
- Perfect for browsing all sales/events

### Keyword Search = Filter
- Query: "sale"
- Results: Only events with "sale" in the title
- Case-insensitive (finds "Sale", "SALE", "sale")

### Clicking Result = Navigate
- Clicks on a search result
- Calendar jumps to that month
- Event highlighted with red border
- Shows event in calendar grid

## Pro Tips

💡 **Show Everything**: Click Search with empty box to see if import worked

💡 **Multiple Keywords**: Search "winter sale" finds events with both words

💡 **Check Count**: Console shows "Total events: X" to verify import

💡 **Calendar View**: Events appear in grid on their actual dates

💡 **Upcoming Events**: Bottom section always shows all events sorted by date

## Summary

To search ALL events and sales from your Google Sheet:

1. ✅ Import data (copy-paste or file upload)
2. ✅ Verify in console (F12) - see "Imported: X"
3. ✅ Click "Search" with empty box - see ALL events
4. ✅ Type keywords to filter specific events
5. ✅ Click results to view in calendar month-wise

Your calendar now has complete import → search → display functionality! 🎉
