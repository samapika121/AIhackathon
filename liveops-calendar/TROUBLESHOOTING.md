# Troubleshooting: Can't Search Events

## Quick Debug Steps

### Step 1: Open Browser Console
1. Open `index.html` in your browser
2. Press **F12** (or Right-click → Inspect)
3. Click **Console** tab

### Step 2: Import Your Data
1. Copy data from Google Sheets (Ctrl+A, Ctrl+C)
2. Paste into the text area in your calendar app
3. Click **"Import from Paste"**

### Step 3: Check Console Output
You should see detailed logs like:
```
=== IMPORT DEBUG ===
Processing X rows of data
Current events before import: 0
Starting from row 0 (header detected: yes/no)
Row 0: Date="12/25/2024", Title="Christmas Sale"
Row 0: ✓ Added - 2024-12-25: Christmas Sale
Row 1: Date="01/15/2025", Title="Winter Launch"
Row 1: ✓ Added - 2025-01-15: Winter Launch
=== IMPORT SUMMARY ===
Imported: 2
Skipped: 0
Total events now: 2
All events: [...]
```

### Step 4: Try Searching
1. Type "sale" in the search box
2. Check console for:
```
Search query: sale
Total events: 2
Matching results: 1
```

## Common Issues & Fixes

### Issue 1: "No valid data found"
**Cause**: Data not properly formatted or missing columns

**Fix**:
- Make sure you copy BOTH Date and Title columns
- Try selecting just 2 columns from your sheet
- Check that dates are in first column, titles in second

### Issue 2: "No new events imported" 
**Cause**: All rows were skipped

**Fix**:
1. Check console logs to see WHY rows were skipped:
   - "Not enough columns" → Copy more columns
   - "Empty date or title" → Sheet has blank cells
   - "Invalid date format" → Dates not recognized
   - "Duplicate" → Events already imported

2. Common date format issues:
   - ✅ Works: 12/25/2024, 2024-12-25, Dec 25 2024
   - ❌ May fail: Text like "Christmas", "Q4", "Next week"

### Issue 3: Events imported but search doesn't find them
**Cause**: Possible localStorage issue or search logic problem

**Debug Steps**:
1. Check console after search:
   ```
   Search query: sale
   Total events: 5  ← Should match number imported
   Matching results: 2  ← Events found
   ```

2. If "Total events: 0":
   - Events didn't save to localStorage
   - Try importing again
   - Check browser privacy settings

3. If "Matching results: 0" but events exist:
   - Check exact event names in console
   - Search is case-insensitive
   - Try searching single word from event name

### Issue 4: Search works but calendar doesn't show events
**Cause**: Display issue, not import issue

**Fix**:
1. Click a search result to navigate
2. Check if red highlight appears
3. Verify month/year is correct
4. Try navigating manually with Previous/Next buttons

## Manual Test

If import still doesn't work, test with manual entry:

1. Click "Add Event" section
2. Pick a date
3. Type "Test Sale Event"
4. Click "Add Event" button
5. Search for "test"
6. Should find it immediately

If manual works but import doesn't → Import parsing issue
If neither works → Search logic issue

## Reset Everything

If all else fails:
1. Open browser console (F12)
2. Type: `localStorage.clear()`
3. Press Enter
4. Refresh page
5. Try importing again

## Get Full Debug Info

To see everything:
1. Open console (F12)
2. Import your data
3. Type: `events`
4. Press Enter
5. You'll see all imported events

Screenshot the console output and share if you need more help!

## Expected Behavior

✅ **Correct flow:**
1. Paste data → See "Processing X rows"
2. See "✓ Added" for each event
3. See "Imported: X" summary
4. Alert shows success
5. Search finds events
6. Calendar displays them

❌ **Problem flow:**
1. Paste data → See "Processing X rows"
2. See "Skipped" for all rows
3. See "Imported: 0"
4. Alert says no events
5. Search finds nothing

## Contact Points

If debugging doesn't help, provide:
1. Screenshot of console during import
2. Screenshot of console during search
3. First 3 rows of your Google Sheet data
4. Browser name and version
