import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import * as ws from 'ws';
import Home from './views/Home/Home';
import Spotify from './views/Spotify/Spotify';

function App() {
	const [ws, setWs] = useState(new WebSocket('ws://localhost:3490'));
	const [message, setMessage] = useState('');
  
	useEffect(() => {
	  ws.onopen = () => {
		  console.log('Connected to WebSocket server');
		  handleSend("Client says hi!");
	  };
	  ws.onmessage = (event) => {
			setMessage(event.data);
		  	console.log(event.data);
	  };
	}, [ws]);
  
	function handleSend(message) {
	  ws.send(message);
	}
	
  return (
	<Router>
		<Routes>
			  <Route path="/" element={<Home />} />
			  <Route path="/spotify" element={<Spotify />} />
		</Routes>
	</Router>
  );
}

export default App;