const socket = new WebSocket('ws://localhost:8765');

socket.onopen = function () {
    document.getElementById('status').innerText = 'Connected to server';
};

socket.onmessage = function (event) {
    document.getElementById('status').innerText = event.data;
};

socket.onerror = function (error) {
    console.error('WebSocket Error:', error);
    document.getElementById('status').innerText = 'Error connecting to server';
};

socket.onclose = function () {
    document.getElementById('status').innerText = 'Disconnected from server';
};

document.getElementById('schedule-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const onTime = document.getElementById('on-time').value;
    const offTime = document.getElementById('off-time').value;
    if (!onTime || !offTime) {
        alert('Please set both ON and OFF times');
        return;
    }
    const schedule = { onTime, offTime };
    try {
        socket.send(JSON.stringify(schedule));
        console.log('Schedule sent:', schedule);
    } catch (error) {
        console.error('Error sending schedule:', error);
        document.getElementById('status').innerText = 'Error sending schedule';
    }
});