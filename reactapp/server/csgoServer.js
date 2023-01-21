const http = require('http');
const fs = require('fs');
const WebSocket = require('ws');

const port = 3490;
const host = '127.0.0.1';

/* --------------------------------- Server --------------------------------- */
const wsServer = new WebSocket.Server({ port: 3491 });
let connectedToWs = false;
let socket;


wsServer.on('connection', (ws) => {
	socket = ws; //Assign the webSocket object to the global variable
	console.log('Client connected');
	ws.on('message', (message) => {
		console.log(`Received message: ${message}`);
	});

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
	let output = '';
	output += data["player"]

	isUserPlaying(data) ? socket.send('pause') : socket.send('resume');

	return output;
}

/* ------------------------------ My Functions ------------------------------ */
function isUserPlaying(data) {
	if ("state" in data["player"])
		return data["player"]["state"]["health"] !== 0 && data["player"]["steamid"] == data["provider"]["steamid"]
	else
		return data["player"]["activity"] !== "menu";
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