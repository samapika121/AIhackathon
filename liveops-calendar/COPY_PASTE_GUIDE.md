# Copy & Paste from Google Sheets - Quick Guide

## 🎯 Upload Your Sheet "As It Is"

The easiest way to get your Google Sheets data into the calendar!

## Method 1: Direct Copy & Paste (Recommended) ⭐

### Step 1: In Google Sheets
1. Open your Google Sheet
2. Select all data you want to import (or press Ctrl+A / Cmd+A)
3. Copy it (Ctrl+C / Cmd+C)

### Step 2: In Calendar App
1. Go to the green "Import from Google Sheets" section at top
2. Click inside the **text area** (big box under "Method 1")
3. Paste your data (Ctrl+V / Cmd+V)
4. Click **"Import from Paste"** button

### Step 3: Done!
- Events are imported automatically
- Success message shows count
- Paste area clears automatically
- Ready to search!

## What Gets Imported

The app looks for:
- **First column**: Dates
- **Second column**: Event titles
- All other columns are ignored

## Example Google Sheet

```
Date          | Title                | Status    | Owner
12/25/2024    | Christmas Sale       | Active    | Marketing
01/15/2025    | Winter Launch        | Planned   | Product
02/14/2025    | Valentine Promo      | Active    | Sales
```

Only Date and Title columns are imported:
✅ Date: 12/25/2024 → Title: Christmas Sale
✅ Date: 01/15/2025 → Title: Winter Launch
✅ Date: 02/14/2025 → Title: Valentine Promo

## Why This Method is Best

✅ **No download needed** - Direct from Google Sheets  
✅ **Preserves formatting** - Tabs are handled automatically  
✅ **Fast** - Copy-paste in seconds  
✅ **Works with any columns** - Only uses first two  
✅ **Mobile friendly** - Works on phones/tablets  

## Tips for Success

### 💡 Select Smart
- Include header row (optional - auto-detected)
- Make sure Date is first column
- Make sure Title is second column
- Can include extra columns (they're ignored)

### 💡 Check Your Data
Before pasting, verify:
- Dates are in a valid format (12/25/2024, 2024-12-25, etc.)
- Event titles are meaningful
- No empty rows in middle

### 💡 Update Workflow
To add new events:
1. Add rows to Google Sheet
2. Copy ALL data again (Ctrl+A, Ctrl+C)
3. Paste and import
4. Duplicates are automatically skipped!

## Troubleshooting

### "No valid data found"
- Make sure you copied both Date AND Title columns
- Check that data actually pasted into the text area
- Try copying just 2 columns from your sheet

### Events not importing
- Check date format (should be recognizable date)
- Ensure no merged cells in Google Sheets
- Try Method 2 (file upload) as alternative

### Some events missing
- Look for dates in unusual format
- Check browser console (F12) for skipped rows
- Dates must be parseable by JavaScript

## After Import

Once imported, you can:
1. **Search** events by name in search box
2. **View** them in calendar grid month-wise
3. **Click** search results to jump to month
4. **See** events highlighted with red pulse animation

## Method 2: File Upload

If copy-paste doesn't work:
1. Download sheet as Excel (.xlsx)
2. Use "Method 2" file upload
3. Same result, different path

## Pro Tips

🚀 **Keyboard Shortcut**: Ctrl+A → Ctrl+C → Ctrl+V → Enter  
🚀 **Headers OK**: First row auto-detected if it says "Date"  
🚀 **Extra Columns**: Paste entire sheet, extras ignored  
🚀 **Quick Updates**: Re-paste anytime to add new events  

## Example Workflow

```
Google Sheets → Copy (Ctrl+C) → Calendar App → Paste (Ctrl+V) → Import → Search!
     ↑                                                                    ↓
     └──────────────────── Add more events ←──────────────────────────────┘
```

Simple, fast, and no files needed! 🎉
