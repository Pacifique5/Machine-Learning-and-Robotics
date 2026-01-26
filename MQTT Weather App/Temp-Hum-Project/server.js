const express = require('express');
const http = require('http');
const mqtt = require('mqtt');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Create an Express app
const app = express();

// Create an HTTP server to serve the frontend
const server = http.createServer(app);

// Connect to SQLite database
const db = new sqlite3.Database('./weather_data.db', (err) => {
    if (err) {
        console.error('Error opening database:', err.message);
    } else {
        console.log('Connected to SQLite database');
    }
});

// Create the table if it doesn't exist
db.run(`
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temperature REAL,
        humidity REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
`, (err) => {
    if (err) {
        console.error('Error creating table:', err.message);
    } else {
        console.log('Weather data table is ready');
    }
});

// Serve the index.html file directly from the root directory
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Connect to the MQTT broker
const mqttClient = mqtt.connect('ws://157.173.101.159:9001'); // Use your broker's WebSocket URL

// When MQTT is connected, subscribe to the necessary topics
mqttClient.on('connect', () => {
    console.log("Connected to MQTT Broker via WebSockets");
    mqttClient.subscribe("/work_group_01/room_temp/temperature");
    mqttClient.subscribe("/work_group_01/room_temp/humidity");
});

// Store the temperature and humidity data
let temperatureData = null;
let humidityData = null;

// Handle incoming MQTT messages and forward them to clients
mqttClient.on('message', (topic, message) => {
    const messageStr = message.toString();
    console.log(`Received message from ${topic}: ${messageStr}`);

    // Update the respective data based on the topic
    if (topic === "/work_group_01/room_temp/temperature") {
        temperatureData = messageStr;
        if (humidityData !== null) {
            // Insert both temperature and humidity into the database
            db.run(`INSERT INTO weather_data (temperature, humidity) VALUES (?, ?)`, [temperatureData, humidityData], function(err) {
                if (err) {
                    console.error('Error inserting data into weather_data:', err.message);
                } else {
                    console.log('Inserted temperature and humidity data into weather_data');
                }
            });
            humidityData = null; // Reset humidityData after inserting
        }
    } else if (topic === "/work_group_01/room_temp/humidity") {
        humidityData = messageStr;
        if (temperatureData !== null) {
            // Insert both temperature and humidity into the database
            db.run(`INSERT INTO weather_data (temperature, humidity) VALUES (?, ?)`, [temperatureData, humidityData], function(err) {
                if (err) {
                    console.error('Error inserting data into weather_data:', err.message);
                } else {
                    console.log('Inserted temperature and humidity data into weather_data');
                }
            });
            temperatureData = null; // Reset temperatureData after inserting
        }
    }
});

// Start the Express server
server.listen(3000, () => {
    console.log('Server running on http://localhost:3000');
});