// Calendar state
let currentDate = new Date();
let events = JSON.parse(localStorage.getItem('liveopsEvents')) || [];
let highlightedDate = null; // Store date to highlight from search
let filteredEvents = events; // Show all events by default, filter when searching

// DOM elements
const calendarGrid = document.getElementById('calendarGrid');
const currentMonthElement = document.getElementById('currentMonth');
const prevMonthBtn = document.getElementById('prevMonth');
const nextMonthBtn = document.getElementById('nextMonth');
const csvFileInput = document.getElementById('csvFile');
const importCSVBtn = document.getElementById('importCSV');
const pasteArea = document.getElementById('pasteArea');
const importPasteBtn = document.getElementById('importPaste');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const clearSearchBtn = document.getElementById('clearSearch');
const searchResultsElement = document.getElementById('searchResults');
const clearAllBtn = document.getElementById('clearAllBtn');

// ⭐ NEW: Modal elements
const eventModal = document.getElementById('eventModal');
const modalDateTitle = document.getElementById('modalDateTitle');
const modalEventList = document.getElementById('modalEventList');
const closeModalBtn = document.getElementById('closeModal');

// ⭐ NEW: Open modal for a specific date
function openEventModal(dateString) {
    if (!dateString) return;

    // Always show all events for that date (not filtered subset)
    const dayEvents = events.filter(ev => ev.date === dateString);

    modalDateTitle.textContent = `Events on ${dateString}`;
    modalEventList.innerHTML = '';

    if (dayEvents.length === 0) {
        modalEventList.innerHTML = '<p>No events on this date.</p>';
    } else {
        dayEvents.forEach(ev => {
            const div = document.createElement('div');
            div.classList.add('event-item');

            const clickupLink = ev.clickup
                ? `<a href="${ev.clickup}" target="_blank" rel="noopener noreferrer">Open ClickUp Task</a>`
                : `<span style="color:#999;">No ClickUp link</span>`;

            const docLink = ev.doc
                ? `<a href="${ev.doc}" target="_blank" rel="noopener noreferrer">Open Document</a>`
                : `<span style="color:#999;">No document link</span>`;

            div.innerHTML = `
                <strong>${ev.title}</strong><br>
                ${clickupLink}<br>
                ${docLink}
            `;
            modalEventList.appendChild(div);
        });
    }

    eventModal.classList.remove('hidden');
}

// ⭐ NEW: Close modal handlers
if (closeModalBtn) {
    closeModalBtn.addEventListener('click', () => {
        eventModal.classList.add('hidden');
    });
}

if (eventModal) {
    eventModal.addEventListener('click', (e) => {
        if (e.target === eventModal) {
            eventModal.classList.add('hidden');
        }
    });
}

// Load events from liveops.json (generated from Google Sheets via n8n)
async function loadEventsFromLiveopsJson() {
    try {
        const response = await fetch('liveops.json');
        if (!response.ok) {
            console.warn('liveops.json not found or failed to load, using localStorage events only');
            return;
        }

        const rows = await response.json();

        const mappedEvents = rows
    .map((row, index) => {
        const data = row && row.json ? row.json : row;

        const normalizedDate = normalizeLiveopsDate(data["JUMP TO TODAY"]);
        if (!normalizedDate) {
            return null;
        }

        const parts = [];
        if (data["JUMP TO TODAY"]) parts.push(data["JUMP TO TODAY"]);
        if (data["Holiday List"]) parts.push(data["Holiday List"]);
        if (data["ON-CALL TEAM"]) parts.push(`On-call: ${data["ON-CALL TEAM"]}`);
        if (data["REVENUE"]) parts.push(`Revenue: ${data["REVENUE"]}`);
        if (data["PERFORMANCE"]) parts.push(`Perf: ${data["PERFORMANCE"]}`);

        // 🔹 NEW: get Doc link from col_96 or "Google Doc link"
        let rawDoc = data["Google Doc link"] || data["col_96"] || null;
        let doc = rawDoc ? rawDoc.toString().trim() : null;

        // Make sure it’s a proper URL (add https:// if missing)
        if (doc && !/^https?:\/\//i.test(doc)) {
        doc = 'https://' + doc.replace(/^\/+/, '');
        }
       let rawClickup = data["Click up link"] || data["col_97"] || null;
       let clickup = rawClickup ? rawClickup.toString().trim() : null;

       if (clickup && !/^https?:\/\//i.test(clickup)) {
       clickup = 'https://' + clickup.replace(/^\/+/, '');
        }
        // if (doc) {
        //     parts.push(`Doc: ${doc}`);
        // }

        const title = parts.join(' | ') || normalizedDate;

        return {
            id: index,
            date: normalizedDate,
            title: title,
            doc,
            clickup   // ⭐ now every event has doc (or null)
        };
    })
    .filter(Boolean);


        if (mappedEvents.length === 0) {
            console.warn('liveops.json loaded but no valid events were mapped');
            return;
        }

        events = mappedEvents;
        filteredEvents = events;
        saveEvents();
    } catch (error) {
        console.error('Error loading events from liveops.json:', error);
    }
}

// Normalize "JUMP TO TODAY" values like " 1 Jan, Wed" into YYYY-MM-DD
function normalizeLiveopsDate(raw) {
    if (!raw || typeof raw !== 'string') return null;

    const trimmed = raw.trim();
    if (!trimmed) return null;

    // Drop the weekday part ("1 Jan, Wed" -> "1 Jan")
    const parts = trimmed.split(',');
    const dayMonth = parts[0].trim();

    // Use the current year as a default; adjust if your sheet encodes year elsewhere
    const year = new Date().getFullYear();
    const parsed = new Date(`${dayMonth} ${year}`);

    if (isNaN(parsed.getTime())) {
        return null;
    }

    const y = parsed.getFullYear();
    const m = String(parsed.getMonth() + 1).padStart(2, '0');
    const d = String(parsed.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

// Initialize calendar
async function init() {
    // Try to load from liveops.json first; falls back to existing localStorage data
    await loadEventsFromLiveopsJson();
    renderCalendar();
    setupEventListeners();
}

// Setup event listeners
function setupEventListeners() {
    prevMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    nextMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });
    
    // Import event listeners
    importCSVBtn.addEventListener('click', importCSV);
    importPasteBtn.addEventListener('click', importFromPaste);
    
    // Search event listeners
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('input', handleSearch);
    clearSearchBtn.addEventListener('click', clearSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    
    // Clear all events listener
    clearAllBtn.addEventListener('click', clearAllEvents);
}

// Render calendar
function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // Update header
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
    currentMonthElement.textContent = `${monthNames[month]} ${year}`;
    
    // Get first day of month and number of days
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const daysInPrevMonth = new Date(year, month, 0).getDate();
    
    // Clear existing days (keep headers)
    const dayHeaders = calendarGrid.querySelectorAll('.day-header');
    calendarGrid.innerHTML = '';
    dayHeaders.forEach(header => calendarGrid.appendChild(header));
    
    // Add previous month's days
    for (let i = firstDay - 1; i >= 0; i--) {
        const day = daysInPrevMonth - i;
        const dayElement = createDayElement(day, true);
        calendarGrid.appendChild(dayElement);
    }
    
    // Add current month's days
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
        const isToday = day === today.getDate() && 
                       month === today.getMonth() && 
                       year === today.getFullYear();
        
        const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const dayEvents = filteredEvents.filter(event => event.date === dateString);
        const hasEvent = dayEvents.length > 0;
        const isHighlighted = highlightedDate === dateString;
        
        const dayElement = createDayElement(
            day, 
            false, 
            isToday, 
            hasEvent, 
            isHighlighted, 
            dayEvents, 
            dateString // ⭐ NEW
        );
        calendarGrid.appendChild(dayElement);
    }
    
    // Add next month's days
    const totalCells = calendarGrid.children.length - 7; // Subtract headers
    const remainingCells = 42 - totalCells - 7; // 6 rows * 7 days - existing cells - headers
    for (let day = 1; day <= remainingCells; day++) {
        const dayElement = createDayElement(day, true);
        calendarGrid.appendChild(dayElement);
    }
}

// Create day element
function createDayElement(
    day, 
    isOtherMonth = false, 
    isToday = false, 
    hasEvent = false, 
    isHighlighted = false, 
    dayEvents = [], 
    dateString = null // ⭐ NEW
) {
    const dayElement = document.createElement('div');
    dayElement.className = 'day';
    
    // Create day number
    const dayNumber = document.createElement('div');
    dayNumber.className = 'day-number';
    dayNumber.textContent = day;
    dayElement.appendChild(dayNumber);
    
    if (isOtherMonth) {
        dayElement.classList.add('other-month');
    }
    if (isToday) {
        dayElement.classList.add('today');
    }
    if (hasEvent) {
        dayElement.classList.add('has-event');
    }
    if (isHighlighted) {
        dayElement.classList.add('highlighted-search');
    }
    
    // Add event titles to the day cell
    if (dayEvents.length > 0 && !isOtherMonth) {
        const eventsContainer = document.createElement('div');
        eventsContainer.className = 'day-events';
        
        dayEvents.slice(0, 2).forEach(event => {
            const eventTag = document.createElement('div');
            eventTag.className = 'event-tag';
            eventTag.textContent = event.title.length > 15 ? event.title.substring(0, 15) + '...' : event.title;
            eventTag.title = event.title; // Show full title on hover
            eventsContainer.appendChild(eventTag);
        });
        
        if (dayEvents.length > 2) {
            const moreTag = document.createElement('div');
            moreTag.className = 'event-tag more-events';
            moreTag.textContent = `+${dayEvents.length - 2} more`;
            eventsContainer.appendChild(moreTag);
        }
        
        dayElement.appendChild(eventsContainer);
    }

    // ⭐ NEW: clicking a day opens modal for that date (only for current-month cells)
    if (!isOtherMonth && dateString) {
        dayElement.style.cursor = 'pointer';
        dayElement.addEventListener('click', () => {
            openEventModal(dateString);
        });
    }
    
    return dayElement;
}

// Delete event
function deleteEvent(id) {
    events = events.filter(event => event.id !== id);
    saveEvents();
    renderCalendar();
}

// Import CSV or Excel file
function importCSV() {
    const file = csvFileInput.files[0];
    if (!file) {
        alert('Please select a file first');
        return;
    }
    
    const fileName = file.name.toLowerCase();
    const fileExtension = fileName.split('.').pop();
    
    // Check if it's an Excel file
    if (fileExtension === 'xlsx' || fileExtension === 'xls') {
        importExcelFile(file);
    } else if (fileExtension === 'csv') {
        importCSVFile(file);
    } else {
        alert('Unsupported file format. Please upload .csv, .xlsx, or .xls file');
    }
}

// Import Excel/Google Sheets file
function importExcelFile(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array' });
            
            // Get first sheet
            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];
            
            // Convert to JSON
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
            
            processImportedData(jsonData);
        } catch (err) {
            console.error('Error parsing Excel file:', err);
            alert('Error reading Excel file. Please make sure it\'s a valid .xlsx or .xls file');
        }
    };
    
    reader.readAsArrayBuffer(file);
}

// Import CSV file
function importCSVFile(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const text = e.target.result;
            const lines = text.split('\n');
            const jsonData = lines.map(line => {
                const parts = line.split(/[,\t]/).map(part => part.trim().replace(/^"|"$/g, ''));
                return parts;
            });
            
            processImportedData(jsonData);
        } catch (err) {
            console.error('Error parsing CSV file:', err);
            alert('Error reading CSV file. Please make sure it\'s properly formatted');
        }
    };
    
    reader.readAsText(file);
}

// Process imported data (common for both CSV and Excel)
function processImportedData(data) {
    let importedCount = 0;
    let skippedCount = 0;
    
    console.log('=== IMPORT DEBUG ===');
    console.log('Processing', data.length, 'rows of data');
    console.log('Current events before import:', events.length);
    
    // Skip header row if it exists
    const startIndex = data[0] && data[0][0] && 
                      (data[0][0].toString().toLowerCase().includes('date') || 
                       data[0][0].toString().toLowerCase().includes('when')) ? 1 : 0;
    
    console.log('Starting from row', startIndex, '(header detected:', startIndex === 1 ? 'yes' : 'no', ')');
    
    for (let i = startIndex; i < data.length; i++) {
        const row = data[i];
        if (!row || row.length < 2) {
            console.log(`Row ${i}: Skipped (not enough columns)`);
            continue;
        }
        
        const dateStr = row[0] ? row[0].toString().trim() : '';
        const title = row[1] ? row[1].toString().trim() : '';
        
        console.log(`Row ${i}: Date="${dateStr}", Title="${title}"`);
        
        if (!dateStr || !title) {
            console.log(`Row ${i}: Skipped (empty date or title)`);
            skippedCount++;
            continue;
        }
        
        // Try to parse the date
        try {
            let date;
            
            // Check if it's an Excel serial date number
            if (!isNaN(dateStr) && dateStr > 1000) {
                // Excel date conversion
                date = XLSX.SSF.parse_date_code(parseFloat(dateStr));
                date = new Date(date.y, date.m - 1, date.d);
            } else {
                // Regular date string
                date = new Date(dateStr);
            }
            
            if (!isNaN(date.getTime())) {
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const formattedDate = `${year}-${month}-${day}`;
                
                // Check if event already exists
                const exists = events.some(e => e.date === formattedDate && e.title === title);
                if (!exists) {
                    events.push({
                        id: Date.now() + i,
                        date: formattedDate,
                        title: title
                        // ⭐ You could also extend here: clickup: row[2], doc: row[3]
                    });
                    console.log(`Row ${i}: ✓ Added - ${formattedDate}: ${title}`);
                    importedCount++;
                } else {
                    console.log(`Row ${i}: Duplicate (skipped)`);
                    skippedCount++;
                }
            } else {
                console.log(`Row ${i}: Invalid date format`);
                skippedCount++;
            }
        } catch (err) {
            console.log(`Row ${i}: Error parsing date - ${err.message}`);
            skippedCount++;
        }
    }
    
    console.log('=== IMPORT SUMMARY ===');
    console.log('Imported:', importedCount);
    console.log('Skipped:', skippedCount);
    console.log('Total events now:', events.length);
    console.log('All events:', events);
    
    if (importedCount > 0) {
        saveEvents();
        filteredEvents = events; // Update filtered events to show new imports
        renderCalendar();
        alert(`Successfully imported ${importedCount} event(s)! ${skippedCount > 0 ? `(${skippedCount} skipped)` : ''}\n\nYou can now search for them.`);
        csvFileInput.value = '';
    } else {
        alert(`No new events imported. ${skippedCount > 0 ? `${skippedCount} rows were skipped.` : ''}\n\nCheck browser console (F12) for details.`);
    }
}

// Clear all events
function clearAllEvents() {
    if (events.length === 0) {
        alert('No events to clear');
        return;
    }
    
    if (confirm(`Are you sure you want to delete all ${events.length} event(s)?`)) {
        events = [];
        filteredEvents = [];
        saveEvents();
        searchInput.value = '';
        searchResultsElement.innerHTML = '';
        renderCalendar();
        alert('All events have been cleared');
    }
}

// Search events
function handleSearch() {
    const query = searchInput.value.trim().toLowerCase();
    
    // Check if there are any events to search
    if (events.length === 0) {
        searchResultsElement.innerHTML = `
            <div class="no-results">
                No events available. Please import events from Google Sheets first!
            </div>
        `;
        filteredEvents = [];
        renderCalendar();
        return;
    }
    
    // If no query, show all events
    if (!query) {
        searchResultsElement.innerHTML = `
            <div class="no-results">
                Showing all ${events.length} event(s). Enter a search term to filter.
            </div>
        `;
        filteredEvents = events;
        renderCalendar();
        console.log('No search query - showing all events');
        return;
    }
    
    // Filter events by title
    const results = events.filter(event => 
        event.title.toLowerCase().includes(query)
    );
    
    console.log('Search query:', query);
    console.log('Total events:', events.length);
    console.log('Matching results:', results.length);
    
    // Update filtered events for calendar display
    filteredEvents = results;
    renderCalendar();
    
    displaySearchResults(results, query);
}

// Display search results
function displaySearchResults(results, query) {
    searchResultsElement.innerHTML = '';
    
    if (results.length === 0) {
        searchResultsElement.innerHTML = `
            <div class="no-results">
                No events found matching "${query}"
            </div>
        `;
        return;
    }
    
    // Sort results by date
    const sortedResults = [...results].sort((a, b) => new Date(a.date) - new Date(b.date));
    
    sortedResults.forEach(event => {
        const resultItem = document.createElement('div');
        resultItem.className = 'search-result-item';
        
        const eventDate = new Date(event.date + 'T00:00:00');
        const formattedDate = eventDate.toLocaleDateString('en-US', { 
            weekday: 'short', 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
        
        // Highlight matching text
        const highlightedTitle = highlightMatch(event.title, query);
        
        resultItem.innerHTML = `
            <div class="search-result-date">${formattedDate}</div>
            <div class="search-result-title">${highlightedTitle}</div>
        `;
        
        // Click to navigate to that date on calendar
        resultItem.addEventListener('click', () => {
            navigateToEvent(event);
        });
        
        searchResultsElement.appendChild(resultItem);
    });
    
    // Add results count
    const countElement = document.createElement('div');
    countElement.style.cssText = 'text-align: center; color: #667eea; font-weight: bold; margin-top: 15px; padding-top: 15px; border-top: 2px solid #e9ecef;';
    countElement.textContent = `Found ${results.length} event${results.length !== 1 ? 's' : ''}`;
    searchResultsElement.appendChild(countElement);
}

// Highlight matching text
function highlightMatch(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<span class="search-highlight">$1</span>');
}

// Navigate calendar to event date
function navigateToEvent(event) {
    const eventDate = new Date(event.date + 'T00:00:00');
    highlightedDate = event.date; // Set highlighted date
    currentDate = new Date(eventDate.getFullYear(), eventDate.getMonth(), 1);
    renderCalendar();
    
    // Scroll to calendar
    document.querySelector('.calendar-grid').scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Clear highlight after 5 seconds
    setTimeout(() => {
        highlightedDate = null;
        renderCalendar();
    }, 5000);
}

// Clear search
function clearSearch() {
    searchInput.value = '';
    searchResultsElement.innerHTML = '';
    filteredEvents = events; // Show all events when search is cleared
    highlightedDate = null; // Clear any highlighted dates
    renderCalendar();
    searchInput.focus();
    console.log('Search cleared - showing all events');
}

// Import from pasted Google Sheets data
function importFromPaste() {
    const pastedData = pasteArea.value.trim();
    
    if (!pastedData) {
        alert('Please paste data from your Google Sheet first');
        return;
    }
    
    try {
        // Split by lines
        const lines = pastedData.split('\n');
        const jsonData = [];
        
        console.log('Pasted data lines:', lines.length);
        
        // Process each line (tab-separated from Google Sheets)
        lines.forEach((line, index) => {
            // Try tab-separated first (Google Sheets default)
            let cells = line.split('\t');
            
            // If only one cell, try comma-separated (CSV format)
            if (cells.length < 2) {
                cells = line.split(',').map(cell => cell.trim().replace(/^"|"$/g, ''));
            }
            
            if (cells.length >= 2) {
                console.log(`Row ${index}:`, cells);
                jsonData.push(cells);
            }
        });
        
        console.log('Parsed rows:', jsonData.length);
        
        if (jsonData.length === 0) {
            alert('No valid data found. Make sure you copied both Date and Title columns from Google Sheets.');
            return;
        }
        
        processImportedData(jsonData);
        
        // Clear the paste area after successful import
        pasteArea.value = '';
        
    } catch (err) {
        console.error('Error parsing pasted data:', err);
        alert('Error processing pasted data. Please make sure you copied the data correctly from Google Sheets.');
    }
}

// Save events to localStorage
function saveEvents() {
    localStorage.setItem('liveopsEvents', JSON.stringify(events));
}

// Initialize the app
init();
