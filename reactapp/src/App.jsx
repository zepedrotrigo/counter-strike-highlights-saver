import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import * as ws from 'ws';
import Home from './views/Home/Home';
import Spotify from './views/Spotify/Spotify';

function App() {
    const [ws, setWs] = useState(null);
    const [message, setMessage] = useState('');

    useEffect(() => {
        if (!ws) {
            const webSocket = new WebSocket('ws://localhost:3491');
            setWs(webSocket);
        }
        else {
            ws.onopen = () => {
                console.log('Connected to WebSocket server');
            };
            ws.onmessage = (event) => {
                setMessage(event.data);
                console.log(event.data);
            };

            ws.onclose = () => {
				console.log('Disconnected from WebSocket server');
				return () => {
					ws.close();
				};
            };
        }
    }, [ws]);
  
	function handleSend(message) {
	  ws.send(message);
	}
	
  return (
	<Router>
		<Routes>
			  <Route path="/" element={<Home />} />
			  <Route path="/spotify" element={<Spotify wsMessage={message} />} />
		</Routes>
	</Router>
  );
}

export default App;