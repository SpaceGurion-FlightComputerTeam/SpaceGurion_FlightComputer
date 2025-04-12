// Create charts for Altitude and Velocity
// Using Chart.js for rendering the charts
window.addEventListener('DOMContentLoaded', () => {
    const maxDataPoints = 30;

    const altCtx = document.getElementById('altitudeChart').getContext('2d');
    const velCtx = document.getElementById('velocityChart').getContext('2d');

    const commonOptions = {
        maintainAspectRatio: false,
        responsive: true,
        animation: { duration: 0 },   // short animations for better performance
        scales: {
            x: {
                ticks: { maxRotation: 0, autoSkip: true, color: '#aaa' },
                grid: { color: 'rgba(70, 70, 70, 0.2)' }
            },
            y: {
                ticks: { color: '#aaa' },
                grid: { color: 'rgba(70, 70, 70, 0.2)' },
                grace: '10%'
            }
        },
        elements: {
            line: { tension: 0.3 },
            point: { radius: 0 }
        },
        plugins: {
            legend: { labels: { color: '#aaa' } }
        }
    };

    const altitudeChart = new Chart(altCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Altitude (m)',
                data: [],
                borderColor: '#00ffcc',
                backgroundColor: 'rgba(0, 255, 204, 0.1)',
                fill: true
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    min: 0,
                    max: 2500,
                    ticks: { color: '#aaa', stepSize: 200 }
                }
            }
        }
    });

    const velocityChart = new Chart(velCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Velocity Z (m/s)',
                data: [],
                borderColor: '#ff8c00',
                backgroundColor: 'rgba(255, 140, 0, 0.1)',
                fill: true
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    min: -150,
                    max: 300,
                    ticks: { color: '#aaa', stepSize: 50 }
                }
            }
        }
    });

    // Store previous altitude for velocity calculation
    let previousAltitude = null;
    let previousTimestamp = null;

    const socket = new WebSocket('ws://localhost:8765');

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("[Data]", data); // Check if data is still coming in
        
        // Format timestamp for display (can be adjusted as needed)
        const timestamp = data.Timestamp || new Date().toISOString();
        const altitude = parseFloat(data["Altitude"]);

// Calculate velocity more accurately with actual time difference
        let velocityZ = 0;
        if (previousAltitude !== null && previousTimestamp !== null) {
            velocityZ = (altitude - previousAltitude) / 0.1;
        }
// Store current values for next calculation
        previousAltitude = altitude;
        previousTimestamp = timestamp;

        requestAnimationFrame(() => {
            updateChart(altitudeChart, timestamp, altitude);
            updateChart(velocityChart, timestamp, velocityZ);

            document.getElementById("altStat").textContent = altitude.toFixed(1);
            document.getElementById("velZStat").textContent = velocityZ.toFixed(1);
        });
    };

    socket.onopen = () => console.log("WebSocket connected");
    socket.onerror = (err) => console.error("WebSocket error:", err);

    function updateChart(chart, label, value) {
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(value);

         // Keep only the last N points
        if (chart.data.labels.length > maxDataPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        chart.update('none');
    }


    // Event listeners for buttons
    document.getElementById('clearBtn').addEventListener('click', () => {
        resetCharts();
    });

    // functions to handle button clicks
    function resetCharts() {
        previousAltitude = null;
        previousTimestamp = null;

        altitudeChart.data.labels = [];
        altitudeChart.data.datasets[0].data = [];
        altitudeChart.update();

        velocityChart.data.labels = [];
        velocityChart.data.datasets[0].data = [];
        velocityChart.update();
    }

    // TODO: Add event listener for data streaming start/stop buttons
});
