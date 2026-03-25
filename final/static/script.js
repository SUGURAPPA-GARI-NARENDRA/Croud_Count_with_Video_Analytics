// ===== Global variables =====
let socket;
let flowChart, zoneChart;
let totalCounter, entryCounter, exitCounter, netCounter;
let zoneCounters = {};

// ===== Initialize on page load =====
document.addEventListener('DOMContentLoaded', () => {
  initSocket();
  initCharts();
  initCounters();
});

// ===== Socket.IO connection =====
function initSocket() {
  socket = io('http://' + window.location.host);

  socket.on('connect', () => {
    updateStatus(true);
    addLog('Connected to server');
  });

  socket.on('disconnect', () => {
    updateStatus(false);
    addLog('Disconnected from server');
  });

  socket.on('data_update', (data) => {
    updateDashboard(data);
  });

  socket.on('connected', (msg) => {
    console.log(msg.message);
  });
}

function updateStatus(connected) {
  const dot = document.querySelector('#statusIndicator .dot');
  const text = document.querySelector('#statusIndicator .status-text');
  if (connected) {
    dot.classList.add('connected');
    dot.classList.remove('disconnected');
    text.textContent = 'Connected';
  } else {
    dot.classList.add('disconnected');
    dot.classList.remove('connected');
    text.textContent = 'Disconnected';
  }
}

// ===== Initialize CountUp instances =====
// FIX: Using countUp.CountUp for UMD library compatibility
function initCounters() {
  totalCounter = new countUp.CountUp('totalPeople', 0, { duration: 1, separator: ',' });
  entryCounter = new countUp.CountUp('entryCount', 0, { duration: 1, separator: ',' });
  exitCounter = new countUp.CountUp('exitCount', 0, { duration: 1, separator: ',' });
  netCounter = new countUp.CountUp('netCount', 0, { duration: 1, separator: ',' });

  if (!totalCounter.error) totalCounter.start();
  if (!entryCounter.error) entryCounter.start();
  if (!exitCounter.error) exitCounter.start();
  if (!netCounter.error) netCounter.start();
}

function initCharts() {
  const flowOptions = {
    chart: {
      type: 'area',
      height: 300,
      animations: { enabled: true, easing: 'easeinout', speed: 800 },
      toolbar: { show: false },
      background: 'transparent'
    },
    series: [
      { name: 'Entry', data: [] },
      { name: 'Exit', data: [] }
    ],
    xaxis: { type: 'datetime', labels: { show: false } },
    yaxis: { labels: { style: { colors: '#fff' } } },
    colors: ['#00e396', '#ff4560'],
    fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.3 } },
    dataLabels: { enabled: false },
    stroke: { curve: 'smooth', width: 2 },
    legend: { labels: { colors: '#fff' } },
    tooltip: { theme: 'dark' }
  };
  flowChart = new ApexCharts(document.querySelector('#flowChart'), flowOptions);
  flowChart.render();

  const zoneOptions = {
    chart: { type: 'donut', height: 300, animations: { enabled: true }, background: 'transparent' },
    series: [],
    labels: [],
    colors: ['#36a2eb', '#ff6384', '#ffce56', '#4bc0c0', '#9966ff'],
    dataLabels: { enabled: false },
    legend: { position: 'bottom', labels: { colors: '#fff' } },
    tooltip: { theme: 'dark', y: { formatter: (val) => val + ' people' } },
    plotOptions: { pie: { donut: { size: '65%', labels: { show: true, name: { color: '#fff' }, value: { color: '#fff', fontSize: '16px' } } } } },
    stroke: { show: false },
    fill: { type: 'gradient' }
  };
  zoneChart = new ApexCharts(document.querySelector('#zoneChart'), zoneOptions);
  zoneChart.render();
}

// FEATURE 4: Generate Report
function downloadReport() {
    window.location.href = '/api/download-report';
    addLog('System: Report generation started...', 'info');
}

// FEATURE 1, 2 & 5: Enhanced Monitoring
f// FEATURE 1, 2 & 5: Enhanced Monitoring
function updateDashboard(data) {
    // 1. Numerical Counts
    totalCounter.update(data.total_people);
    entryCounter.update(data.entry_count);
    exitCounter.update(data.exit_count);
    netCounter.update(data.net_flow);

    // 2. Traffic Flow (Area Chart)
    updateFlowChart(data); 

    // 3. Zone Occupancy & Distribution (Donut Chart & Cards)
    if (data.zones) {
        updateZoneChart(data.zones); 
        updateZoneCards(data.zones); 
    }

    document.getElementById('lastUpdate').textContent = data.timestamp;

    // --- NEW: Crowd Alert Logic ---
    const banner = document.getElementById('overloadBanner');
    if (banner) {
        if (data.total_people > 0) {        // Alert triggers at > 15 people
            banner.classList.remove('hidden');
            document.querySelector('.video-card').classList.add('overload-border');
        } else {
            banner.classList.add('hidden');
            document.querySelector('.video-card').classList.remove('overload-border');
        }
    }
}
// Listen for dedicated system logs
socket.on('system_log', (data) => {
    const logContainer = document.getElementById('systemLogs');
    const entry = document.createElement('div');
    entry.className = `log-entry ${data.type === 'alert' ? 'text-red' : ''}`;
    entry.innerHTML = `<span>${new Date().toLocaleTimeString()}</span>: ${data.message}`;
    logContainer.prepend(entry);
});

function updateZoneCards(zones) {
  const container = document.getElementById('zonesContainer');
  // We only clear the innerHTML if the number of zones changed to avoid flickering
  const currentZoneKeys = Object.keys(zones || {});
  if (container.children.length !== currentZoneKeys.length) {
      container.innerHTML = '';
      if (currentZoneKeys.length === 0) {
          container.innerHTML = '<div class="zone-item">No zones defined</div>';
          return;
      }
  }

  for (const [zoneName, count] of Object.entries(zones)) {
    const zoneId = `zone-${zoneName.replace(/\s+/g, '')}`;
    let zoneElement = document.getElementById(zoneId);

    if (!zoneElement) {
      const card = document.createElement('div');
      card.className = 'zone-item';
      card.innerHTML = `
        <i class="fas fa-${getZoneIcon(zoneName)}"></i>
        <div class="zone-name">${zoneName}</div>
        <div class="zone-count" id="${zoneId}">${count}</div>
      `;
      container.appendChild(card);
      
      // FIX: Added 'countUp.' prefix
      zoneCounters[zoneName] = new countUp.CountUp(zoneId, count, { duration: 1 });
      zoneCounters[zoneName].start();
    } else {
      if (zoneCounters[zoneName]) {
          zoneCounters[zoneName].update(count);
      }
    }
  }
}

function getZoneIcon(zoneName) {
  const name = zoneName.toLowerCase();
  if (name.includes('entrance') || name.includes('entry')) return 'door-open';
  if (name.includes('exit')) return 'door-closed';
  if (name.includes('lobby')) return 'couch';
  if (name.includes('hall')) return 'building';
  if (name.includes('room')) return 'bed';
  return 'map-pin';
}

// ===== FIX: Update flow chart without appendData crash =====
function updateFlowChart(data) {
  const timestamp = new Date().getTime();
  const series = flowChart.w.config.series;

  series[0].data.push({ x: timestamp, y: data.entry_count });
  series[1].data.push({ x: timestamp, y: data.exit_count });

  if (series[0].data.length > 20) {
    series[0].data.shift();
    series[1].data.shift();
  }
  flowChart.updateSeries(series);
}

function updateZoneChart(zones) {
  if (!zones || Object.keys(zones).length === 0) return;
  zoneChart.updateOptions({
    labels: Object.keys(zones),
    series: Object.values(zones)
  });
}

function addLog(message) {
  const log = document.getElementById('activityLog');
  const empty = log.querySelector('.log-empty');
  if (empty) empty.remove();

  const entry = document.createElement('div');
  entry.className = 'log-entry';
  entry.innerHTML = `<span class="time">${new Date().toLocaleTimeString()}</span><span class="message">${message}</span>`;
  log.prepend(entry);
  if (log.children.length > 10) log.removeChild(log.lastElementChild);
}
socket.on('data_update', (data) => {
  // ... existing updates ...
  const banner = document.getElementById('overloadBanner');
  if (data.total_people > 15) {        // threshold from config
    banner.classList.remove('hidden');
    // Optional: add a red border to the video card
    document.querySelector('.video-card').classList.add('overload-border');
  } else {
    banner.classList.add('hidden');
    document.querySelector('.video-card').classList.remove('overload-border');
  }
});
async function loadAlertGallery() {
    const response = await fetch('/api/alerts-list');
    const files = await response.json();
    const container = document.getElementById('alertGallery');
    
    if (files.length === 0) return;

    container.innerHTML = ''; // Clear the "No alerts" message
    
    files.forEach(filename => {
        const div = document.createElement('div');
        div.className = 'alert-item';
        
        // Format the filename for a pretty label (optional)
        const timeLabel = filename.replace('crowd_alert_', '').replace('.jpg', '');
        
        div.innerHTML = `
            <img src="/static/alerts/${filename}" alt="Crowd Alert">
            <div class="timestamp">${timeLabel}</div>
        `;
        container.appendChild(div);
    });
}

// Load the gallery automatically when the page starts
document.addEventListener('DOMContentLoaded', () => {
    loadAlertGallery();
});