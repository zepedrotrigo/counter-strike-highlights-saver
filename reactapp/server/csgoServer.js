const http = require('http');
const fs = require('fs');
const WebSocket = require('ws');
const { player: spotifyPlayer} = require('./spotifyServer');

const port = 3489;
const host = '127.0.0.1';

const userName = "Fortnyce"

/* --------------------------------- Server --------------------------------- */
const wsServer = new WebSocket.Server({ port: 3490 });

wsServer.on('connection', (ws) => {
	console.log('Client connected');
	ws.on('message', (message) => {
		console.log(`Received message: ${message}`);
	});
	ws.send('Server says hi!');
});

const server = http.createServer((req, res) => {
	res.writeHead(200, { 'Content-Type': 'text/html' });

	let eventInfo = '';

	req.on('data', (data) => {
		eventInfo += processPayload(JSON.parse(data.toString()));
	});

	req.on('end', () => {
		if (eventInfo !== '') {
			console.log(eventInfo);
		}

		res.end('');
	});
});

/* ----------------------------- Process Payload ---------------------------- */
function sendWebSocketMessage(message) {
	wsServer.send(message);
}

function processPayload(data) {
	const date = new Date(data.provider.timestamp * 1000);
	let output = '';
	console.log(data);
	if (isUserPlaying(data)) {
		console.log("User is Playing")
		try {
			spotifyPlayer.pause()
		} catch (error) {
			console.log(error)
		}
	} else {
		console.log("Spectating")
			try {
				spotifyPlayer.resume()
			} catch (error) {
			console.log(error)
		}
	}
	return output;
}

/* ------------------------------ My Functions ------------------------------ */
function isUserPlaying(data) {
	if (data["player"]["name"] !== userName) //|| data["map"]["phase"] !== "live")
		return false;
	
	return true;
}

/* -------------------------------------------------------------------------- */
server.listen(port, host);

console.log('Monitoring CS:GO rounds');