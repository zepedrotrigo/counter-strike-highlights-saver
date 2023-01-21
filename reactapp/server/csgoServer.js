const http = require('http');
const fs = require('fs');
const WebSocket = require('ws');

const port = 3489;
const host = '127.0.0.1';

const userName = "Fortnyce"
let lastSentMessage;
/* --------------------------------- Server --------------------------------- */
const wsServer = new WebSocket.Server({ port: 3490 });
let connectedToWs = false;
let socket;


wsServer.on('connection', (ws) => {
	socket = ws; //Assign the webSocket object to the global variable
	console.log('Client connected');
	ws.on('message', (message) => {
		console.log(`Received message: ${message}`);
	});
	ws.send('Server says hi!');

	connectedToWs = true;
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
function processPayload(data) {
	const date = new Date(data.provider.timestamp * 1000);
	let output = '';
	console.log(data);
	
	if (isUserPlaying(data) && lastSentMessage !== "pause") {
		socket.send('pause');
		lastSentMessage = "pause";
	} else if (lastSentMessage !== "resume") {
		socket.send('resume');
		lastSentMessage = "resume";
	}

	return output;
}

/* ------------------------------ My Functions ------------------------------ */
function isUserPlaying(data) {
	return data["player"]["name"] == userName;
}


function waitForWebSocketsServerToStartHTTPServer() {
    if(connectedToWs === false) {
       setTimeout(waitForWebSocketsServerToStartHTTPServer, 1000); /* this checks the flag every 100 milliseconds*/
    } else {
		server.listen(port, host);
		console.log('Monitoring CS:GO rounds');
    }
}

/* ----- Create httpServer AFTER the websocket connection is established ---- */
waitForWebSocketsServerToStartHTTPServer()