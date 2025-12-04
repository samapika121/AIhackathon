# LiveOps Calendar App

A simple and elegant calendar application for tracking live operations and events.

## Features

- 📅 Interactive monthly calendar view
- 🔍 **Real-time search** - Find events instantly by name!
- ➕ Add events manually with date and title
- 📊 **Direct Google Sheets import** - Upload .xlsx files directly!
- 📄 CSV import support for maximum compatibility
- 🗑️ Delete individual events or clear all at once
- 💾 Automatic data persistence using localStorage
- 📱 Fully responsive design
- 🔢 Smart date parsing (handles Excel date numbers and text formats)
- 🎯 Click search results to jump to event date on calendar

## How to Use

### Opening the App
Simply open `index.html` in your web browser.

### Adding Events Manually
1. Select a date using the date picker
2. Enter the event title
3. Click "Add Event"

### Searching Events
1. Type the event name (or part of it) in the search box
2. Results appear instantly with matching text highlighted
3. Click any result to navigate to that event on the calendar
4. Click "Clear" to reset the search

For detailed search tips and examples, see [SEARCH_GUIDE.md](SEARCH_GUIDE.md)

### Importing from Google Sheets

#### Method 1: Download as Excel (Recommended - No Export Needed!)
1. Open your Google Sheet
2. Click **File → Download → Microsoft Excel (.xlsx)**
3. In the app, click "Choose File" and select the downloaded file
4. Click "Import File"
5. Done! Your events are now in the calendar

#### Method 2: Export as CSV
1. Open your Google Sheet
2. Click **File → Download → Comma-separated values (.csv)**
3. In the app, click "Choose File" and select the downloaded CSV
4. Click "Import File"

### File Format Requirements

**Supported File Types:**
- `.xlsx` - Excel/Google Sheets (Recommended)
- `.xls` - Legacy Excel format
- `.csv` - Comma-separated values

**Column Structure:**
Your file should have at least two columns in this order:
```
Date          | Title
2024-12-25    | Christmas Event
2025-01-01    | New Year Celebration
```

**Supported date formats:**
- Excel date numbers (automatically converted)
- `YYYY-MM-DD` (e.g., 2024-12-25)
- `MM/DD/YYYY` (e.g., 12/25/2024)
- Most standard date formats that JavaScript can parse

**Tips:**
- First row is automatically detected as header if it contains "Date" or "When"
- Empty rows are automatically skipped
- Duplicate events are prevented
- Invalid dates are skipped with a console warning

### Sample File
Check out `sample_events.csv` for a working example you can test with.

## Features Details

### Search Functionality
- **Real-time search**: Results update as you type
- **Intelligent matching**: Case-insensitive, partial word matching
- **Highlighted results**: Matching text appears with yellow highlight
- **Click to navigate**: Jump to event's month on calendar
- **Sorted by date**: Results ordered chronologically
- **Results counter**: Shows total matches found

### Visual Indicators
- **Purple gradient**: Today's date
- **Red dot**: Days with scheduled events
- **Hover effects**: Interactive calendar days
- **Yellow highlight**: Matched search terms in results

### Data Management
- All events are saved to browser localStorage
- Events persist between sessions
- Duplicate events are automatically prevented during import

### Calendar Navigation
- Use "Previous" and "Next" buttons to navigate months
- View shows current month and year
- Click search results to jump to specific event dates

## Technical Details

Built with:
- Pure HTML, CSS, and JavaScript
- **SheetJS (xlsx.js)** - Excel/Google Sheets file parsing
- LocalStorage for data persistence
- FileReader API for file import
- Smart date parsing for multiple formats

## Troubleshooting

**Events not appearing after import?**
- Ensure your file has at least two columns: Date and Title
- Check that dates are in the first column, titles in the second
- Verify dates are in a recognizable format (not just text like "January")
- Open browser console (F12) to see detailed error messages
- Try with the included `sample_events.csv` to test if import works

**Excel file not importing?**
- Make sure file extension is .xlsx or .xls
- Check that the file isn't corrupted or password-protected
- Try re-downloading from Google Sheets as Excel format
- As a fallback, export as CSV instead

**Google Sheets download not working?**
- You need download/edit access to the sheet
- Use **File → Download** (not File → Publish to web)
- Download as Microsoft Excel (.xlsx) format

**Events disappeared?**
- Check if browser localStorage was cleared
- Private/incognito mode doesn't save data between sessions
- Each browser has separate storage (data won't sync between Chrome/Firefox/etc.)

**File upload button not working?**
- Ensure you have an internet connection (SheetJS library loads from CDN)
- Try refreshing the page
- Check browser console for any loading errors
