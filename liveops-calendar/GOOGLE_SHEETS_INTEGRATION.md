# Google Sheets Integration Guide

## 🎯 Complete Integration Workflow

Your calendar is now fully integrated with Google Sheets! Here's how to use it:

## Step 1: Download Your Google Sheet

1. Open your Google Sheet: 
   `https://docs.google.com/spreadsheets/d/19duXZN3PdqULWhc9Hx3Szxui0UmVlLMgFGR7tnBZaKQ/edit`

2. Click **File → Download**

3. Choose one of:
   - **Microsoft Excel (.xlsx)** ← Recommended
   - **Comma-separated values (.csv)**

4. File downloads to your computer

## Step 2: Import to Calendar

1. Open your calendar app in browser (`index.html`)

2. At the top, you'll see **"Import from Google Sheets"** section (green background)

3. Click **"Choose File"** button

4. Select the downloaded file from your computer

5. Click **"Import File"** button

6. You'll see: "Successfully imported X event(s)!"

## Step 3: Search and Display

Now all your Google Sheets events are in the calendar!

### Search Any Event
1. Type event name in **"Search from my calendar"** section
2. Results appear instantly below
3. Click any result

### What Happens Next
✅ Calendar jumps to that month  
✅ Event appears in the calendar grid  
✅ Day cell is highlighted with red border  
✅ Event name shows on the day  
✅ Highlight pulses for 5 seconds

## Example Workflow

### If your Google Sheet has:
```
Date          | Title
2024-12-25    | Christmas Sale
2025-01-15    | Winter Promotion
2025-02-14    | Valentine's Sale
```

### After importing:
1. Type "sale" in search → Shows 2 results
2. Click "Christmas Sale"
3. Calendar shows December 2024
4. December 25th cell shows "Christmas Sale" with red highlight
5. Event is visible in the calendar grid!

## Your Google Sheet Format

Make sure your spreadsheet has:
- **Column 1**: Dates (any format like 12/25/2024 or 2024-12-25)
- **Column 2**: Event titles/names
- **Header row** (optional): "Date" and "Title"

## Re-Importing Updates

To update with new events:
1. Add events to your Google Sheet
2. Download again as Excel/CSV
3. Import the file again
4. Only NEW events are added (duplicates are skipped!)

## Features After Import

### Calendar Display
- Events show directly in calendar grid cells
- Purple tags for each event
- Up to 2 events per day visible
- "+X more" for additional events

### Search Functionality
- Real-time search as you type
- Case-insensitive matching
- Click results to navigate
- Yellow highlight on matched text

### Month-Wise View
- Navigate months with Previous/Next buttons
- Events display only in their correct months
- Today's date has purple gradient
- Searched events pulse with red border

## Supported File Types

✅ **.xlsx** - Excel/Google Sheets (Best option)  
✅ **.xls** - Legacy Excel format  
✅ **.csv** - Comma-separated values  

## Troubleshooting

### "No valid events found"
- Check that Column 1 has dates
- Check that Column 2 has event names
- Ensure dates are valid formats

### Events not displaying in calendar
- Check if dates are in the future/past
- Navigate to the correct month
- Use search to find and jump to events

### Import button not working
- Make sure you selected a file first
- Check file extension (.xlsx, .xls, or .csv)
- Refresh page and try again

## Data Persistence

- All imported events saved to browser localStorage
- Events persist even after closing browser
- Each import adds new events (no deletions)
- Use "Delete" button in event list to remove events

## Quick Tips

💡 **Batch Import**: Import all your events at once for the entire year  
💡 **Regular Updates**: Re-import monthly to add new campaigns  
💡 **Search First**: Use search to quickly find and navigate to any sale/event  
💡 **Visual Planning**: See all events in month-wise calendar grid view  

## What Makes This Powerful

1. **No Manual Entry**: Import hundreds of events in seconds
2. **Google Sheets**: Keep master data in familiar spreadsheet
3. **Instant Search**: Find any event by name immediately
4. **Visual Calendar**: See events in proper calendar grid format
5. **Click to Navigate**: Jump to any month with one click
6. **Mobile Friendly**: Works on all devices

Your Google Sheets data is now fully searchable and displayable in a beautiful calendar interface! 🎉
