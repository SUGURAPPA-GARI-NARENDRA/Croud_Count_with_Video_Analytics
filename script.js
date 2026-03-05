// script.js - Dynamic Dashboard with Real-time Updates

const API_BASE_URL = 'http://localhost:5000/api';
let flowChart = null;
let zoneChart = null;
let flowChartData = [];
let updateInterval = null;

// Initialize the dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');
    initializeDashboard();
    startDataUpdates();
});

// Initialize dashboard elements
function initializeDashboard() {
    // Initialize charts
    initFlowChart();
    initZoneChart();
    
    // Generate zone cards
    generateZoneCards();
    
    // Update status indicator
    updateConnectionStatus(true);
}

// Start fetching data every 2 seconds
function startDataUpdates() {
    // Fetch immediately on start
    fetchDashboardData();
    
    // Then fetch every 2 seconds
    updateInterval = setInterval(fetchDashboardData, 2000);
}

// Fetch all dashboard data from backend
async function fetchDashboardData() {
    try {
        const response = await fetch(`${API_BASE_URL}/all-data`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update all UI elements with fetched data
        updateDashboard(data);
        
        // Update connection status
        updateConnectionStatus(true);
        
    } catch (error) {
        console.error('Error fetching data:', error);
        updateConnectionStatus(false);
    }
}

// Update all dashboard elements
function updateDashboard(data) {
    // Update main stats
    document.getElementById('totalPeople').textContent = data.total_people || 0;
    document.getElementById('entryCount').textContent = data.entry_count || 0;
    document.getElementById('exitCount').textContent = data.exit_count || 0;
    document.getElementById('netCount').textContent = data.net_flow || 0;
    document.getElementById('lastUpdate').textContent = formatTime(new Date());
    
    // Update zone distribution
    updateZoneCards(data.zones || {});
    
    // Update charts
    updateFlowChart(data);
    updateZoneChartData(data.zones || {});
    
    // Add to activity log
    logActivity(`Data updated at ${formatTime(new Date())}`);
}

// Generate zone cards dynamically
function generateZoneCards() {
    const container = document.getElementById('zonesContainer');
    
    // Fetch zone names from config or use default
    const zones = {
        'Zone 1': 0,
        'Zone 2': 0
    };
    
    container.innerHTML = '';
    
    for (const [zoneName, count] of Object.entries(zones)) {
        const card = document.createElement('div');
        card.className = 'zone-card';
        card.id = `zone-${zoneName.replace(/\s+/g, '-')}`;
        card.innerHTML = `
            <div class="zone-header">
                <h3>${zoneName}</h3>
                <span class="zone-icon">📍</span>
            </div>
            <div class="zone-count">${count}</div>
            <div class="zone-footer">People in zone</div>
        `;
        container.appendChild(card);
    }
}

// Update zone card counts
function updateZoneCards(zones) {
    for (const [zoneName, count] of Object.entries(zones)) {
        const zoneId = `zone-${zoneName.replace(/\s+/g, '-')}`;
        const zoneCard = document.getElementById(zoneId);
        
        if (zoneCard) {
            const countElement = zoneCard.querySelector('.zone-count');
            if (countElement) {
                countElement.textContent = count || 0;
            }
        }
    }
}

// Initialize Flow Chart
function initFlowChart() {
    const ctx = document.getElementById('flowChart');
    if (!ctx) return;
    
    flowChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Entry Count',
                    data: [],
                    borderColor: 'rgba(75, 192, 75, 1)',
                    backgroundColor: 'rgba(75, 192, 75, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Exit Count',
                    data: [],
                    borderColor: 'rgba(255, 99, 99, 1)',
                    backgroundColor: 'rgba(255, 99, 99, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

// Initialize Zone Chart
function initZoneChart() {
    const ctx = document.getElementById('zoneChart');
    if (!ctx) return;
    
    zoneChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'People in Zone',
                data: [],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(201, 203, 207, 0.7)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(201, 203, 207, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

// Update Flow Chart with new data
function updateFlowChart(data) {
    if (!flowChart) return;
    
    const timestamp = new Date().toLocaleTimeString();
    
    // Keep only last 20 data points
    if (flowChart.data.labels.length > 20) {
        flowChart.data.labels.shift();
        flowChart.data.datasets[0].data.shift();
        flowChart.data.datasets[1].data.shift();
    }
    
    flowChart.data.labels.push(timestamp);
    flowChart.data.datasets[0].data.push(data.entry_count || 0);
    flowChart.data.datasets[1].data.push(data.exit_count || 0);
    
    flowChart.update();
}

// Update Zone Chart data
function updateZoneChartData(zones) {
    if (!zoneChart) return;
    
    const zoneNames = Object.keys(zones);
    const zoneCounts = Object.values(zones);
    
    zoneChart.data.labels = zoneNames;
    zoneChart.data.datasets[0].data = zoneCounts;
    zoneChart.update();
}

// Update connection status indicator
function updateConnectionStatus(isConnected) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    if (isConnected) {
        statusDot.className = 'status-dot connected';
        statusText.textContent = 'Connected';
    } else {
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = 'Disconnected';
    }
}

// Log activity
function logActivity(activity) {
    const activityLog = document.getElementById('activityLog');
    
    // Remove empty state message if it exists
    const emptyMsg = activityLog.querySelector('.log-empty');
    if (emptyMsg) {
        emptyMsg.remove();
    }
    
    // Create new log entry
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = `
        <span class="log-time">${formatTime(new Date())}</span>
        <span class="log-message">${activity}</span>
    `;
    
    // Add to top of log
    activityLog.insertBefore(logEntry, activityLog.firstChild);
    
    // Keep only last 10 entries
    const entries = activityLog.querySelectorAll('.log-entry');
    if (entries.length > 10) {
        entries[entries.length - 1].remove();
    }
}

// Format time for display
function formatTime(date) {
    return date.toLocaleTimeString();
}

// Stop updates on page unload
window.addEventListener('beforeunload', function() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});