# MQTT Weather Station

This project allows real-time monitoring of temperature and humidity data received via MQTT and displays them on a webpage. Data is stored in an SQLite database, and the average values for the last 5 minutes are calculated and visualized using a chart.

## Setup Instructions

1. **Install Dependencies**
   - Ensure you have [Node.js](https://nodejs.org/) installed.
   - Clone the repository:
   ```bash
   git clone <repository-url>
   cd mqtt-weather-station