import React, { useState, useEffect } from 'react';
import WebPlayback from '../../components/Spotify/WebPlayback';
import Login from '../../components/Spotify/Login';
import './Spotify.css';

function Spotify(props) {
	const [token, setToken] = useState('');

	useEffect(() => {

		async function getToken() {
			const response = await fetch('/auth/token');
			const json = await response.json();
			setToken(json.access_token);
		}

		getToken();

	}, []);

	return (
		<>
			{(token === '') ? <Login /> : <WebPlayback token={token} wsMessage={props.wsMessage}/> }
		</>
	);
}

export default Spotify;