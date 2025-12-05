// Calendar state
let currentDate = new Date();
let events = JSON.parse(localStorage.getItem('liveopsEvents')) || [];
let highlightedDate = null; // Store date to highlight from search
let filteredEvents = []; // Start with empty calendar, show only searched events

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
const webhookUrlInput = document.getElementById('webhookUrl');
const importWebhookBtn = document.getElementById('importWebhook');
const saveWebhookBtn = document.getElementById('saveWebhook');
const fairFilter = document.getElementById('fairFilter');
const dayEventsModal = document.getElementById('dayEventsModal');
const modalClose = document.querySelector('.modal-close');
const modalDayTitle = document.getElementById('modalDayTitle');
const modalSearchInput = document.getElementById('modalSearchInput');
const modalSearchBtn = document.getElementById('modalSearchBtn');
const modalClearSearch = document.getElementById('modalClearSearch');
const modalEventsList = document.getElementById('modalEventsList');

// Store current day's events for modal
let currentDayEvents = [];

// Initialize calendar
function init() {
    renderCalendar();
    setupEventListeners();
    loadSavedWebhook();
    
    // Populate Fair filter if events exist
    if (events.length > 0) {
        populateFairFilter();
        searchResultsElement.innerHTML = `
            <div class="no-results">
                ${events.length} event(s) loaded. Enter a search term or select a Fair to filter events
            </div>
        `;
    } else {
        searchResultsElement.innerHTML = `
            <div class="no-results">
                Import events from n8n webhook, then use search to find them.
            </div>
        `;
    }
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
    
    // Import event listeners (only if elements exist)
    if (importCSVBtn) importCSVBtn.addEventListener('click', importCSV);
    if (importPasteBtn) importPasteBtn.addEventListener('click', importFromPaste);
    if (importWebhookBtn) importWebhookBtn.addEventListener('click', importFromWebhook);
    if (saveWebhookBtn) saveWebhookBtn.addEventListener('click', saveWebhookUrl);
    
    // Search event listeners
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('input', handleSearch);
    clearSearchBtn.addEventListener('click', clearSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    
    // Fair filter listener
    if (fairFilter) {
        fairFilter.addEventListener('change', handleSearch);
    }
    
    // Clear all events listener
    clearAllBtn.addEventListener('click', clearAllEvents);
    
    // Modal event listeners
    if (modalClose) {
        modalClose.addEventListener('click', closeDayEventsModal);
    }
    
    if (dayEventsModal) {
        dayEventsModal.addEventListener('click', (e) => {
            if (e.target === dayEventsModal) {
                closeDayEventsModal();
            }
        });
    }
    
    if (modalSearchBtn) {
        modalSearchBtn.addEventListener('click', handleModalSearch);
    }
    
    if (modalClearSearch) {
        modalClearSearch.addEventListener('click', clearModalSearch);
    }
    
    if (modalSearchInput) {
        modalSearchInput.addEventListener('input', handleModalSearch);
        modalSearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleModalSearch();
            }
        });
    }
    
    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && dayEventsModal && dayEventsModal.style.display === 'block') {
            closeDayEventsModal();
        }
    });
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
        
        const dayElement = createDayElement(day, false, isToday, hasEvent, isHighlighted, dayEvents);
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
function createDayElement(day, isOtherMonth = false, isToday = false, hasEvent = false, isHighlighted = false, dayEvents = []) {
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
        
        // Add click handler to open modal with day's events
        dayElement.style.cursor = 'pointer';
        dayElement.addEventListener('click', () => {
            openDayEventsModal(day, dayEvents);
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
    
    // Skip header row if it exists
    const startIndex = data[0] && data[0][0] && 
                      (data[0][0].toString().toLowerCase().includes('date') || 
                       data[0][0].toString().toLowerCase().includes('when')) ? 1 : 0;
    
    for (let i = startIndex; i < data.length; i++) {
        const row = data[i];
        if (!row || row.length < 2) continue;
        
        const dateStr = row[0] ? row[0].toString().trim() : '';
        const title = row[1] ? row[1].toString().trim() : '';
        
        if (!dateStr || !title) continue;
        
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
                    });
                    importedCount++;
                }
            }
        } catch (err) {
            console.log('Skipping invalid date:', dateStr);
        }
    }
    
    if (importedCount > 0) {
        saveEvents();
        renderCalendar();
        
        // Update search prompt
        searchResultsElement.innerHTML = `
            <div class="no-results">
                ${events.length} event(s) loaded. Enter a search term to find events (e.g., "PO", "Sale", "Event")
            </div>
        `;
        
        alert(`Successfully imported ${importedCount} event(s)! Use the search box to find specific events.`);
        if (csvFileInput) csvFileInput.value = '';
    } else {
        alert('No valid events found in file. Make sure it has Date and Title columns.');
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
        searchResultsElement.innerHTML = `
            <div class="no-results">
                Import events from n8n webhook, then use search to find them.
            </div>
        `;
        renderCalendar();
        alert('All events have been cleared');
    }
}

// Search events
function handleSearch() {
    const query = searchInput.value.trim().toLowerCase();
    const selectedFair = fairFilter ? fairFilter.value : '';
    
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
    
    // If no query and no fair selected, clear the calendar
    if (!query && !selectedFair) {
        searchResultsElement.innerHTML = `
            <div class="no-results">
                Enter a search term or select a Fair to filter events
            </div>
        `;
        filteredEvents = [];
        renderCalendar();
        console.log('No search query or fair filter - calendar cleared');
        return;
    }
    
    // Filter events by title and/or Fair
    let results = events;
    
    // Filter by Fair first if selected
    if (selectedFair) {
        results = results.filter(event => 
            event.fair && event.fair === selectedFair
        );
    }
    
    // Then filter by search query if provided
    if (query) {
        results = results.filter(event => 
            event.title.toLowerCase().includes(query)
        );
    }
    
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
        const highlightedTitle = highlightMatch(event.title, query || '');
        
        // Include Fair info if available
        const fairInfo = event.fair ? `<div class="search-result-fair">Fair: ${event.fair}</div>` : '';
        
        resultItem.innerHTML = `
            <div class="search-result-date">${formattedDate}</div>
            <div class="search-result-title">${highlightedTitle}</div>
            ${fairInfo}
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
    if (fairFilter) fairFilter.value = '';
    searchResultsElement.innerHTML = `
        <div class="no-results">
            Enter a search term or select a Fair to filter events
        </div>
    `;
    filteredEvents = []; // Clear calendar when search is cleared
    highlightedDate = null; // Clear any highlighted dates
    renderCalendar();
    searchInput.focus();
    console.log('Search cleared - calendar hidden');
}

// Populate Fair filter dropdown
function populateFairFilter() {
    if (!fairFilter) return;
    
    console.log('=== POPULATING FAIR FILTER ===');
    console.log('Total events:', events.length);
    
    // Get unique Fair values from events
    const fairValues = new Set();
    events.forEach((event, index) => {
        if (index < 5) {
            console.log(`Event ${index}:`, event.title, 'Fair:', event.fair);
        }
        if (event.fair && event.fair.trim() !== '') {
            fairValues.add(event.fair);
        }
    });
    
    console.log('Unique fairs found:', Array.from(fairValues));
    
    // Clear existing options except "All Fairs"
    fairFilter.innerHTML = '<option value="">All Fairs</option>';
    
    // Add unique Fair values as options
    const sortedFairs = Array.from(fairValues).sort();
    sortedFairs.forEach(fair => {
        const option = document.createElement('option');
        option.value = fair;
        option.textContent = fair;
        fairFilter.appendChild(option);
    });
    
    console.log('Fair filter populated with', fairValues.size, 'unique fairs');
}

// Import from pasted Google Sheets data
function importFromPaste() {
    if (!pasteArea) return;
    
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
        const fair = row[2] ? row[2].toString().trim() : '';
        const link = row[3] ? row[3].toString().trim() : '';
        
        console.log(`Row ${i}: Date="${dateStr}", Title="${title}", Fair="${fair}", Link="${link}"`);
        
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
                        title: title,
                        fair: fair,
                        link: link
                    });
                    console.log(`Row ${i}: ✓ Added - ${formattedDate}: ${title} (Fair: ${fair}, Link: ${link})`);
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
        populateFairFilter(); // Populate Fair dropdown with unique values
        renderCalendar();
        
        // Update search prompt
        searchResultsElement.innerHTML = `
            <div class="no-results">
                ${events.length} event(s) loaded. Enter a search term or select a Fair to filter events
            </div>
        `;
        
        alert(`Successfully imported ${importedCount} event(s)! ${skippedCount > 0 ? `(${skippedCount} skipped)` : ''}\n\nUse the search box or Fair filter to find specific events.`);
        if (csvFileInput) csvFileInput.value = '';
    } else {
        alert(`No new events imported. ${skippedCount > 0 ? `${skippedCount} rows were skipped.` : ''}\n\nCheck browser console (F12) for details.`);
    }
}

// Load saved webhook URL
function loadSavedWebhook() {
    if (!webhookUrlInput) return;
    
    const savedWebhook = localStorage.getItem('n8nWebhookUrl');
    if (savedWebhook) {
        webhookUrlInput.value = savedWebhook;
    }
}

// Save webhook URL to localStorage
function saveWebhookUrl() {
    if (!webhookUrlInput) return;
    
    const url = webhookUrlInput.value.trim();
    if (!url) {
        alert('Please enter a webhook URL first');
        return;
    }
    
    try {
        new URL(url); // Validate URL format
        localStorage.setItem('n8nWebhookUrl', url);
        alert('Webhook URL saved successfully!');
    } catch (err) {
        alert('Please enter a valid URL (e.g., https://your-n8n.com/webhook/...)');
    }
}

// Import from n8n webhook
async function importFromWebhook() {
    if (!webhookUrlInput) return;
    
    const url = webhookUrlInput.value.trim();
    
    if (!url) {
        alert('Please enter your n8n webhook URL first');
        return;
    }
    
    try {
        // Show loading state
        if (importWebhookBtn) {
            importWebhookBtn.textContent = 'Fetching...';
            importWebhookBtn.disabled = true;
        }
        
        console.log('Fetching data from n8n webhook:', url);
        
        // Fetch data from webhook
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Received data from n8n:', data);
        
        // Process the data - handle different response formats
        let dataArray = [];
        
        if (Array.isArray(data)) {
            dataArray = data;
        } else if (data.data && Array.isArray(data.data)) {
            dataArray = data.data;
        } else if (data.body && Array.isArray(data.body)) {
            dataArray = data.body;
        } else {
            throw new Error('Unexpected data format. Expected an array of events.');
        }
        
        // Convert to the format expected by processImportedData
        const jsonData = [];
        
        // Log first item to see actual structure
        if (dataArray.length > 0) {
            console.log('=== WEBHOOK DATA STRUCTURE DEBUG ===');
            console.log('First item structure:', dataArray[0]);
            console.log('Available properties:', Object.keys(dataArray[0]));
            const firstItem = dataArray[0];
            console.log('Link column values:', {
                'Link': firstItem['Link'],
                'link': firstItem['link'],
                'URL': firstItem['URL'],
                'url': firstItem['url'],
                'Ticket Link': firstItem['Ticket Link']
            });
            
            // Show all column values to help identify the correct link column
            console.log('Sample of first row values:');
            Object.keys(firstItem).slice(0, 15).forEach(key => {
                console.log(`  ${key}: ${firstItem[key]}`);
            });
        }
        
        // Event columns to check for LiveOps data
        const eventColumns = [
            'Launches', 'Fairs', 'Chip / Rockets Store Sale', 'PO 1', 'PO 2', 
            'SeasonPass', 'Album Sale', 'RBS', 'EBS', 'Piggy Bank', 'Wheel Spin',
            'Web Shop Sale', 'Event 1', 'Event 2', 'Powerplay Promo', 
            'Lever/Promo 1', 'Lever/Promo 2', 'Bash Wins/Tourney', 'Rooms Lever',
            'DIscounted Card Cost (DCC)', 'Bash Care Package', 'Slots Promo',
            'Season Pass Challenge', 'Web', 'VIP', 'Bold Beats - I', 'Bold Beats - II',
            'Bold beats - III', 'CRM Promo-1', 'CRM Promotions 2', 'Room Config Changes'
        ];
        
        dataArray.forEach((item, index) => {
            // Get date from the Date field (format: " 1 Jan, Wed")
            const dateStr = item.Date || item.date || '';
            
            if (!dateStr) return;
            
            // Parse date format " 1 Jan, Wed" to standard date
            try {
                const dateParts = dateStr.trim().split(',')[0].trim(); // " 1 Jan"
                const [day, monthStr] = dateParts.split(' ').filter(p => p);
                
                const monthMap = {
                    'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
                    'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
                };
                
                const currentYear = new Date().getFullYear();
                const month = monthMap[monthStr];
                const date = new Date(currentYear, month, parseInt(day));
                
                const year = date.getFullYear();
                const monthNum = String(date.getMonth() + 1).padStart(2, '0');
                const dayNum = String(date.getDate()).padStart(2, '0');
                const formattedDate = `${year}-${monthNum}-${dayNum}`;
                
                // Get Fair value and Link for this row
                const fairValue = item['Fairs'] || '';
                const linkValue = item['Link'] || item['link'] || item['URL'] || item['url'] || item['Ticket Link'] || '';
                
                if (index < 5) {
                    console.log(`Row ${index} - Date: ${dateStr}, Fair: "${fairValue}", Link: "${linkValue}"`);
                }
                
                // Check all event columns for values
                eventColumns.forEach(colName => {
                    const value = item[colName];
                    if (value && value.toString().trim() && value !== '' && value !== '-') {
                        // Store date, title, fair value, and link
                        jsonData.push([formattedDate, `${colName}: ${value}`, fairValue, linkValue]);
                        if (index < 3 && jsonData.length <= 10) {
                            console.log(`  - Added: ${colName}: ${value}, Fair: "${fairValue}", Link: "${linkValue}"`);
                        }
                    }
                });
                
            } catch (err) {
                if (index < 5) {
                    console.log(`Row ${index} date parse error:`, dateStr, err);
                }
            }
        });
        
        console.log('Processed data:', jsonData);
        
        if (jsonData.length === 0) {
            alert('No valid events found in webhook response. Make sure your n8n workflow returns an array with "date" and "title" fields.');
            return;
        }
        
        // Import the data
        processImportedData(jsonData);
        
    } catch (err) {
        console.error('Error fetching from webhook:', err);
        alert(`Error fetching data from n8n:\n${err.message}\n\nMake sure:\n1. The webhook URL is correct\n2. Your n8n workflow is active\n3. The workflow returns JSON data with "date" and "title" fields`);
    } finally {
        // Reset button state
        if (importWebhookBtn) {
            importWebhookBtn.textContent = 'Fetch from n8n';
            importWebhookBtn.disabled = false;
        }
    }
}

// Save events to localStorage
function saveEvents() {
    localStorage.setItem('liveopsEvents', JSON.stringify(events));
}

// Open day events modal
function openDayEventsModal(day, dayEvents) {
    if (!dayEventsModal) return;
    
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    modalDayTitle.textContent = `Events for ${monthNames[month]} ${day}, ${year}`;
    currentDayEvents = [...dayEvents]; // Store events for filtering
    
    // Clear search input
    if (modalSearchInput) modalSearchInput.value = '';
    
    // Display all events for the day
    displayModalEvents(currentDayEvents);
    
    // Show modal
    dayEventsModal.style.display = 'block';
}

// Close day events modal
function closeDayEventsModal() {
    if (dayEventsModal) {
        dayEventsModal.style.display = 'none';
    }
    currentDayEvents = [];
    if (modalSearchInput) modalSearchInput.value = '';
}

// Handle modal search
function handleModalSearch() {
    const query = modalSearchInput ? modalSearchInput.value.trim().toLowerCase() : '';
    
    if (!query) {
        // Show all events if no query
        displayModalEvents(currentDayEvents);
        return;
    }
    
    // Filter events by query
    const filtered = currentDayEvents.filter(event =>
        event.title.toLowerCase().includes(query)
    );
    
    displayModalEvents(filtered, query);
}

// Clear modal search and show all events
function clearModalSearch() {
    if (modalSearchInput) {
        modalSearchInput.value = '';
    }
    
    // Remove all selections
    const allItems = modalEventsList.querySelectorAll('.modal-event-item');
    allItems.forEach(item => item.classList.remove('modal-event-selected'));
    
    // Show all events
    displayModalEvents(currentDayEvents);
}

// Display events in modal
function displayModalEvents(eventsToShow, query = '') {
    if (!modalEventsList) return;
    
    modalEventsList.innerHTML = '';
    
    if (eventsToShow.length === 0) {
        modalEventsList.innerHTML = '<div class="modal-no-events">No events found</div>';
        return;
    }
    
    eventsToShow.forEach(event => {
        const eventItem = document.createElement('div');
        eventItem.className = 'modal-event-item';
        
        // Event content wrapper
        const eventContent = document.createElement('div');
        eventContent.className = 'modal-event-content';
        
        const eventTitle = document.createElement('div');
        eventTitle.className = 'modal-event-title';
        
        // Highlight search term if present
        if (query) {
            const regex = new RegExp(`(${query})`, 'gi');
            eventTitle.innerHTML = event.title.replace(regex, '<span class="search-highlight">$1</span>');
        } else {
            eventTitle.textContent = event.title;
        }
        
        eventContent.appendChild(eventTitle);
        
        // Add date info
        const eventDate = document.createElement('div');
        eventDate.className = 'modal-event-date';
        eventDate.textContent = formatDateForDisplay(event.date);
        eventContent.appendChild(eventDate);
        
        // Add Fair info if available
        if (event.fair) {
            const fairInfo = document.createElement('div');
            fairInfo.className = 'modal-event-fair';
            fairInfo.textContent = `Fair: ${event.fair}`;
            eventContent.appendChild(fairInfo);
        }
        
        eventItem.appendChild(eventContent);
        
        // Add action buttons
        const actionsContainer = document.createElement('div');
        actionsContainer.className = 'modal-event-actions';
        
        // Ticket link button
        const ticketBtn = document.createElement('button');
        ticketBtn.className = 'modal-action-btn ticket-btn';
        ticketBtn.innerHTML = '🔗';
        ticketBtn.title = event.link ? 'Open ticket link (from Google Sheet)' : 'No link available';
        ticketBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openTicketLink(event);
        });
        
        // Disable button if no link
        if (!event.link || event.link.trim() === '') {
            ticketBtn.style.opacity = '0.4';
            ticketBtn.style.cursor = 'not-allowed';
        }
        
        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'modal-action-btn delete-btn';
        deleteBtn.innerHTML = '🗑️';
        deleteBtn.title = 'Delete event';
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteEventFromModal(event);
        });
        
        actionsContainer.appendChild(ticketBtn);
        actionsContainer.appendChild(deleteBtn);
        eventItem.appendChild(actionsContainer);
        
        // Make event item selectable
        eventItem.addEventListener('click', () => {
            selectModalEvent(eventItem, event);
        });
        
        modalEventsList.appendChild(eventItem);
    });
}

// Format date for display
function formatDateForDisplay(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Select event in modal
function selectModalEvent(eventItem, event) {
    // Populate search box with event title
    if (modalSearchInput) {
        modalSearchInput.value = event.title;
    }
    
    // Filter to show only this event
    handleModalSearch();
    
    // Add selection to the filtered item (need to re-query after filter)
    setTimeout(() => {
        const allItems = modalEventsList.querySelectorAll('.modal-event-item');
        allItems.forEach(item => item.classList.remove('modal-event-selected'));
        
        // Find and select the matching event in the filtered list
        allItems.forEach(item => {
            item.classList.add('modal-event-selected');
        });
    }, 50);
}

// Open ticket link
function openTicketLink(event) {
    // Check if event has an associated link from Google Sheet
    if (event.link && event.link.trim() !== '') {
        // Open the link from Google Sheet in a new tab
        window.open(event.link, '_blank');
        
        // Show temporary success message
        const message = document.createElement('div');
        message.className = 'ticket-success-message';
        message.textContent = '🔗 Ticket link opened in new tab!';
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.remove();
        }, 2000);
    } else {
        // No link available
        alert('No ticket link available for this event.\n\nPlease add a link in the "Link" column of your Google Sheet for this event.');
    }
}

// Delete event from modal
function deleteEventFromModal(event) {
    if (confirm(`Are you sure you want to delete:\n"${event.title}"?`)) {
        // Remove from events array
        events = events.filter(e => e.id !== event.id);
        
        // Remove from current day events
        currentDayEvents = currentDayEvents.filter(e => e.id !== event.id);
        
        // Save and refresh
        saveEvents();
        
        // Refresh modal display
        displayModalEvents(currentDayEvents);
        
        // If no events left, close modal
        if (currentDayEvents.length === 0) {
            closeDayEventsModal();
        }
        
        // Refresh calendar and search
        renderCalendar();
        if (searchInput && searchInput.value.trim()) {
            handleSearch();
        }
        
        // Update fair filter
        populateFairFilter();
    }
}

// Initialize the app
init();
