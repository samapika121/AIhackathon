# Search-Only Display Mode

## How It Works Now

Your calendar now displays events **ONLY** when you search for them. This keeps the calendar clean and focused on what you're looking for.

## Complete Workflow

### 1. Import Events (Clean Calendar)
- Import from Google Sheets (paste or file)
- Events are stored but **NOT displayed** on calendar
- Calendar grid stays clean
- "Upcoming Events" list shows all imported events

### 2. Search for Specific Events
- Type "sale" in search box → Click Search
- **ONLY sales events** appear in:
  - Search results list
  - Calendar grid on their dates
- All other events hidden

### 3. Try Different Searches
- Type "event" → See only events
- Type "winter" → See only winter items
- Type "2024" → See only 2024 items
- Each search updates the calendar display

### 4. Clear Search
- Click "Clear" button
- Calendar grid becomes **empty again**
- Search results disappear
- Ready for next search

## Examples

### Example 1: Search "Sale"

**Before Search:**
```
Calendar: Empty (no events visible)
```

**After Searching "sale":**
```
Search Results:
- Christmas Sale (12/25/2024)
- New Year Sale (12/31/2024)
- Valentine Sale (02/14/2025)

Calendar Grid:
December 2024:
  25: [Christmas Sale]
  31: [New Year Sale]

February 2025:
  14: [Valentine Sale]
```

**After Clear:**
```
Calendar: Empty again
```

### Example 2: Search "Event"

**Search Query:** "event"

**Results:**
```
Search Results:
- Winter Launch Event (01/15/2025)
- Spring Event (03/20/2025)
- Summer Event (06/15/2025)

Calendar Grid:
January 2025:
  15: [Winter Launch Event]

March 2025:
  20: [Spring Event]

June 2025:
  15: [Summer Event]
```

Only these 3 events appear in calendar. All sales are hidden.

### Example 3: Multiple Keywords

**Search Query:** "winter sale"

**Results:**
```
Search Results:
- Winter Launch Sale (01/15/2025)

Calendar Grid:
January 2025:
  15: [Winter Launch Sale]
```

Only events matching BOTH "winter" AND "sale" appear.

## Key Features

### ✅ Clean Calendar
- No clutter from all events
- Only see what you search for
- Easy to focus on specific campaigns

### ✅ Dynamic Display
- Each search updates calendar instantly
- No need to manually filter
- Clear shows clean calendar again

### ✅ Full Event List
- "Upcoming Events" section always shows ALL imported events
- This is your master list
- Use calendar for searched items only

### ✅ Visual Navigation
- Click search results to jump to month
- Red highlight animation on clicked event
- Event shows in calendar grid on that date

## Practical Use Cases

### Use Case 1: Review All Sales
1. Type "sale" → Search
2. See all sales in results
3. Click each to jump to month in calendar
4. Review timing and spacing

### Use Case 2: Check Q1 Events
1. Type "january" or "february" or "march"
2. OR type "2025" to see all 2025 events
3. See them in calendar grid
4. Plan around those dates

### Use Case 3: Find Specific Campaign
1. Type unique keyword (e.g., "black friday")
2. See exact event
3. Click to see in calendar context
4. Check surrounding dates

### Use Case 4: Compare Similar Events
1. Search "winter" 
2. See all winter-related events
3. View in calendar grid
4. Analyze distribution across months

## Tips

💡 **Start Fresh**: Import events once, calendar stays clean

💡 **Search Smart**: Use keywords that appear in your event names

💡 **Quick Clear**: Clear button resets calendar to empty state

💡 **Multiple Views**: 
- Calendar grid = Searched events only
- Upcoming Events list = All events always

💡 **Navigate Freely**: Use Previous/Next to browse months while viewing searched events

## Compared to Previous Behavior

| Feature | Before | Now |
|---------|--------|-----|
| After Import | All events in calendar | Clean calendar |
| Searching | Shows results + all events still visible | Shows ONLY searched events |
| Calendar View | Always shows everything | Only shows current search |
| Clarity | Cluttered with all events | Clean, focused on search |

## Summary

**Old Way:**
- Import → See ALL events in calendar
- Search → See results but calendar still shows all
- Confusing mix of everything

**New Way:**
- Import → Calendar stays clean ✨
- Search "sale" → See ONLY sales 🎯
- Clear → Back to clean calendar 🧹
- Perfect for focused review! ✅

Your calendar is now a powerful search-driven tool that shows exactly what you're looking for, when you need it!
