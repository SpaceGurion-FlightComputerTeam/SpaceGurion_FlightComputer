import { addMessageListener } from './sockets.js';
import { send } from './sockets.js';

// Create charts for Altitude and Velocity
// Using Chart.js for rendering the charts
window.addEventListener('DOMContentLoaded', () => {
    const maxDataPoints = 50;

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
                    max: 1500,
                    ticks: { color: '#aaa', stepSize: 100 }
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
                    //min: -150,
                    //max: 500,
                    ticks: { color: '#aaa', stepSize: 50 }
                }
            }
        }
    });

    // Store previous altitude for velocity calculation
    let previousAltitude = null;
    let previousTimestamp = null;


    document.getElementById("connectBtn").disabled = true;
    document.getElementById("startBtn").disabled = true;
    document.getElementById("stopBtn").disabled = true;


    let missionTimerStarted = false;


   // const socket = new WebSocket('ws://localhost:8765');
    addMessageListener((data) => {
        console.log("[Data]", data); // Check if data is still coming in
        // If it's a status message
        if (data.status) {
            if (data.status === "connected") {
                document.getElementById("connectionStatus").textContent = "✅ Connected";
                document.getElementById("startBtn").disabled = false;
                document.getElementById("connectBtn").textContent = "Connected";
                document.getElementById("connectBtn").disabled = true;
            } else if (data.status === "connection_failed") {
                document.getElementById("connectionStatus").textContent = "❌ Connection failed";
            }
            return;
        }
        
        // Start mission timer when first telemetry packet arrives
        if (!missionTimerStarted && data.Frame === 1) {
            startMissionTimer();
            missionTimerStarted = true;
        }

        // Format timestamp for display (can be adjusted as needed)
        const timestamp = parseFloat(data["time"]) || 0;
        const altitude = parseFloat(data["altitude"]) || 0;
        const tempartue = parseFloat(data["temp"]) || 0;
        const pressure = parseFloat(data["pres"]) || 0;
        const latitude = parseFloat(data["latitude"]) || 0;
        const longitude = parseFloat(data["longitude"]) || 0;

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

        // Update other stats
        document.getElementById("temperatureStat").textContent = tempartue.toFixed(1);
        document.getElementById("pressureStat").textContent = pressure.toFixed(1);
        document.getElementById("gpsLatStat").textContent = latitude.toFixed(6);
        document.getElementById("gpsLonStat").textContent = longitude.toFixed(6);
    });

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



    // ----------------------------- Function for mission timer------------------------
    let missionStartTime = null;
    let missionTimerInterval = null;

    function startMissionTimer() {
        missionStartTime = Date.now();
        missionTimerInterval = setInterval(updateMissionTimer, 1000);
    }
    
    function updateMissionTimer() {
        const now = Date.now();
        const elapsedMs = now - missionStartTime;
        const seconds = Math.floor(elapsedMs / 1000) % 60;
        const minutes = Math.floor(elapsedMs / 60000);

        const formattedTime = `T+ ${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        document.getElementById('missionTimer').textContent = formattedTime;
    }

    function stopMissionTimer() {
        clearInterval(missionTimerInterval);
        //document.getElementById('missionTimer').textContent = "T+ 00:00";
    }


    // ----------------------------- Function for buttons click------------------------
    // Event listeners for buttons
    document.getElementById('connectBtn').addEventListener('click', () => {
        connectSensors();
    });
    document.getElementById("abortBtn").addEventListener('click', () => {
      Abort();  
    })
    document.getElementById('startBtn').addEventListener('click', () => {
        startData();
    });
    document.getElementById('stopBtn').addEventListener('click', () => {
        //stopMissionTimer(); // Stop the mission timer when data stops
        stopData();
    });
    document.getElementById('clearBtn').addEventListener('click', () => {
        resetCharts();
    });



    function connectSensors() {
        send({ command: "connect" });
        document.getElementById("status").textContent = "Connecting...";
    }
    
    function Abort()
    {
        send({ command: "abort" });
        document.getElementById("status").textContent = "Aborting...";
    }

    function startData() {
        send({ command: "start" });
        document.getElementById("status").textContent = "Streaming...";
        document.getElementById("startBtn").disabled = true;
        document.getElementById("stopBtn").disabled = false;
    }

    function stopData() {
        send({ command: "stop" });
        document.getElementById("status").textContent = "Stopped";
        document.getElementById("startBtn").disabled = false;
        document.getElementById("stopBtn").disabled = true;
    }

    function resetCharts() {
        send({ command: "reset" });
        document.getElementById("status").textContent = "Resetting...";

        previousAltitude = null;
        previousTimestamp = null;

        altitudeChart.data.labels = [];
        altitudeChart.data.datasets[0].data = [];
        altitudeChart.update();

        velocityChart.data.labels = [];
        velocityChart.data.datasets[0].data = [];
        velocityChart.update();
    }

});
