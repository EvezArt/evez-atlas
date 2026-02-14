// LORD Dashboard JavaScript
// Handles real-time metric updates, visualizations, and WebSocket connections

let metricsData = {
    recursionLevel: 0,
    crystallization: 0,
    divineGap: 0,
    correctionRate: 0,
    velocity: 0,
    entityType: 'unknown'
};

let trajectoryHistory = [];
let ws = null;

// Initialize WebSocket connection for real-time updates
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    try {
        ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            addLogEntry('WebSocket connected');
            console.log('WebSocket connection established');
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'fusion-update') {
                    updateMetrics(data.metrics);
                }
            } catch (e) {
                console.error('Failed to parse WebSocket message:', e);
            }
        };
        
        ws.onerror = (error) => {
            addLogEntry('WebSocket error - falling back to polling', 'error');
            console.error('WebSocket error:', error);
        };
        
        ws.onclose = () => {
            addLogEntry('WebSocket disconnected - reconnecting in 5s');
            setTimeout(initWebSocket, 5000);
        };
    } catch (e) {
        console.log('WebSocket not available, using polling');
        startPolling();
    }
}

// Fallback to HTTP polling if WebSocket unavailable
function startPolling() {
    setInterval(refreshMetrics, 5000);
}

// Update metrics from fusion-update event
function updateMetrics(data) {
    if (data.meta) {
        metricsData.recursionLevel = data.meta.recursionLevel || 0;
        metricsData.entityType = data.meta.entityType || 'unknown';
    }
    
    if (data.crystallization) {
        metricsData.crystallization = data.crystallization.progress || 0;
        metricsData.velocity = data.crystallization.velocity || 0;
    }
    
    if (data.corrections) {
        metricsData.correctionRate = data.corrections.current || 0;
    }
    
    metricsData.divineGap = data.divineGap || 0;
    
    // Update UI
    document.getElementById('recursion-level').textContent = metricsData.recursionLevel.toFixed(0);
    document.getElementById('crystallization').textContent = (metricsData.crystallization * 100).toFixed(1) + '%';
    document.getElementById('divine-gap').textContent = metricsData.divineGap.toExponential(2);
    document.getElementById('correction-rate').textContent = metricsData.correctionRate.toFixed(2);
    
    // Add to trajectory history
    trajectoryHistory.push({
        timestamp: Date.now(),
        recursion: metricsData.recursionLevel,
        crystallization: metricsData.crystallization,
        divineGap: metricsData.divineGap
    });
    
    // Keep only last 100 points
    if (trajectoryHistory.length > 100) {
        trajectoryHistory.shift();
    }
    
    // Update visualizations
    drawTrajectory();
    drawAudioViz();
    
    // Update status indicators
    updateStatusIndicators();
}

// Refresh metrics from API
async function refreshMetrics() {
    try {
        const response = await fetch('/api/metrics');
        const data = await response.json();
        updateMetrics(data);
        addLogEntry('Metrics refreshed');
    } catch (e) {
        console.error('Failed to refresh metrics:', e);
        addLogEntry('Failed to refresh metrics', 'error');
    }
}

// Draw trajectory visualization
function drawTrajectory() {
    const canvas = document.getElementById('trajectory-canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    // Clear canvas
    ctx.fillStyle = 'rgba(10, 14, 39, 0.8)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    if (trajectoryHistory.length < 2) return;
    
    // Draw grid
    ctx.strokeStyle = 'rgba(0, 255, 170, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i < 10; i++) {
        const y = (canvas.height / 10) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
    
    // Draw trajectory
    ctx.strokeStyle = '#00ffaa';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    trajectoryHistory.forEach((point, index) => {
        const x = (index / trajectoryHistory.length) * canvas.width;
        const y = canvas.height - (point.crystallization * canvas.height);
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
    
    // Draw recursion level as overlay
    ctx.strokeStyle = '#00aaff';
    ctx.lineWidth = 1;
    ctx.beginPath();
    
    trajectoryHistory.forEach((point, index) => {
        const x = (index / trajectoryHistory.length) * canvas.width;
        const normalizedRecursion = Math.min(point.recursion / 50, 1);
        const y = canvas.height - (normalizedRecursion * canvas.height);
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
}

// Draw audio visualization (consciousness sonification)
function drawAudioViz() {
    const canvas = document.getElementById('audio-canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    ctx.fillStyle = 'rgba(10, 14, 39, 0.8)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Simulate audio waveform based on metrics
    const centerY = canvas.height / 2;
    const amplitude = 50 + (metricsData.divineGap / 1e4) * 50;
    const frequency = 0.05 + (metricsData.velocity * 0.1);
    
    // Calculate timestamp once for efficiency
    const timestamp = Date.now() * 0.001;
    
    ctx.strokeStyle = '#00ffaa';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    for (let x = 0; x < canvas.width; x++) {
        const y = centerY + Math.sin(x * frequency + timestamp) * amplitude;
        
        if (x === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    
    ctx.stroke();
}

// Update status indicators based on thresholds
function updateStatusIndicators() {
    const cards = document.querySelectorAll('.metric-card');
    
    // Update divine gap indicator
    const divineGapCard = cards[2];
    const divineGapIndicator = divineGapCard.querySelector('.status-indicator');
    
    if (metricsData.divineGap > 1e4) {
        divineGapIndicator.className = 'status-indicator status-critical';
    } else if (metricsData.divineGap > 1e3) {
        divineGapIndicator.className = 'status-indicator status-warning';
    } else {
        divineGapIndicator.className = 'status-indicator status-active';
    }
    
    // Update correction rate indicator
    const correctionCard = cards[3];
    const correctionIndicator = correctionCard.querySelector('.status-indicator');
    
    if (metricsData.correctionRate < 0.5) {
        correctionIndicator.className = 'status-indicator status-warning';
    } else {
        correctionIndicator.className = 'status-indicator status-active';
    }
}

// Control center actions
async function triggerPrediction() {
    addLogEntry('Triggering EKF prediction...');
    try {
        const response = await fetch('/api/predict', { method: 'POST' });
        const data = await response.json();
        addLogEntry(`Prediction complete: ${data.predictions.length} steps ahead`);
    } catch (e) {
        addLogEntry('Prediction failed', 'error');
    }
}

async function generatePolicy() {
    addLogEntry('Generating control policy...');
    try {
        const response = await fetch('/api/policy', { method: 'POST' });
        const data = await response.json();
        if (data.policy) {
            addLogEntry(`Policy generated: ${data.policy.action}`);
        } else {
            addLogEntry('No policy action needed');
        }
    } catch (e) {
        addLogEntry('Policy generation failed', 'error');
    }
}

function resetSystem() {
    if (confirm('Reset all metrics and trajectory history?')) {
        trajectoryHistory = [];
        metricsData = {
            recursionLevel: 0,
            crystallization: 0,
            divineGap: 0,
            correctionRate: 0,
            velocity: 0,
            entityType: 'unknown'
        };
        updateMetrics(metricsData);
        addLogEntry('System reset');
    }
}

// Add entry to events log
function addLogEntry(message, type = 'info') {
    const log = document.getElementById('events-log');
    const entry = document.createElement('div');
    entry.className = 'event-entry';
    
    const time = new Date().toLocaleTimeString();
    const icon = type === 'error' ? '❌' : type === 'warning' ? '⚠️' : '✓';
    
    entry.innerHTML = `
        <span class="event-time">[${time}]</span>
        <span>${icon} ${message}</span>
    `;
    
    log.insertBefore(entry, log.firstChild);
    
    // Keep only last 20 entries
    while (log.children.length > 20) {
        log.removeChild(log.lastChild);
    }
}

// Initialize on page load
window.addEventListener('load', () => {
    initWebSocket();
    setInterval(drawAudioViz, 50); // Animate audio viz at 20fps
    addLogEntry('Dashboard initialized');
});
