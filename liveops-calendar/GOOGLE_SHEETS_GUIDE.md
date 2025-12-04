# Quick Start: Importing Google Sheets to LiveOps Calendar

## Step-by-Step Guide

### 1. Prepare Your Google Sheet

Make sure your Google Sheet has this structure:

| Date       | Title                    |
|------------|--------------------------|
| 12/25/2024 | Christmas Event          |
| 01/01/2025 | New Year Celebration     |
| 01/15/2025 | Limited Time Offer Ends  |

**Requirements:**
- First column = Date (any common date format works)
- Second column = Event title/description
- Header row is optional (will be auto-detected)

### 2. Download from Google Sheets

**Option A: Download as Excel (Easiest!)**
1. Open your Google Sheet
2. Click **File** → **Download** → **Microsoft Excel (.xlsx)**
3. File will download to your computer

**Option B: Download as CSV**
1. Open your Google Sheet
2. Click **File** → **Download** → **Comma-separated values (.csv)**
3. File will download to your computer

### 3. Import to Calendar

1. Open `index.html` in your web browser
2. Scroll down to the "Import from Google Sheets or CSV" section
3. Click **Choose File** button
4. Select the file you just downloaded
5. Click **Import File** button
6. You'll see a success message with the count of imported events!

## Example Google Sheet Structure

```
Date              | Title                  | (Optional: More columns ignored)
------------------|------------------------|--------------------------------
2024-12-01        | Launch Holiday Event   |
2024-12-15        | Winter Festival Begins |
2024-12-20        | Special Boss Battle    |
2024-12-25        | Christmas Day Event    |
2025-01-01        | New Year Celebration   |
```

## Tips for Best Results

✅ **DO:**
- Use standard date formats (12/25/2024, 2024-12-25, Dec 25 2024, etc.)
- Put dates in the first column
- Put event titles in the second column
- Have at least 2 columns (Date and Title)

❌ **DON'T:**
- Use text like "January" without a day and year
- Put empty rows at the top (except header)
- Use complex formulas in date cells (convert to values first)

## Common Date Formats That Work

All of these work perfectly:
- `12/25/2024` or `12-25-2024`
- `2024-12-25` or `2024/12/25`
- `Dec 25, 2024` or `December 25, 2024`
- `25 Dec 2024` or `25-Dec-2024`
- Excel serial numbers (like 45643) - auto-converted!

## Multiple Sheets?

If your Google Sheets file has multiple tabs:
- Only the **first tab** (sheet) will be imported
- To import other tabs, download each one separately or move the data to the first tab

## Updating Events

To update your calendar with new events:
1. Download your updated Google Sheet again
2. Import the new file
3. The app automatically prevents duplicates
4. Only new events will be added

## Need Help?

- Check the browser console (press F12) for detailed error messages
- Make sure your file has the correct format
- Try the included `sample_events.csv` to verify import works
- See main README.md for full troubleshooting guide
