const http = require('http');
const fs = require('fs');

const port = 45027;
const host = '127.0.0.1';
let killTimestamps = {};

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

/**
 * Processes payloads to parse game events
 *
 * @param {object} data - Payload as JSON object
 * @return {string}
 */
function processPayload(data) {
    saveKillTimestamps(data);
    writeKillTimestampsToFileAndReset(data);
    return killTimestamps;
}


/**
 * Saves local player's kill timestamps for every round
 *
 * @param {object} data - Payload as JSON object
 * @return {object} - JSON object containing round numbers and kill timestamps
 */
function saveKillTimestamps(data) {
    const localPlayerSteamId = readProperty(data, 'provider.steamid');
    const roundNumber = readProperty(data, 'map.round');
    const killEvents = readProperty(data, 'added.player.kill');

    if (killEvents) {
        killEvents.forEach((killEvent) => {
            if (killEvent.killer === localPlayerSteamId) {
                const killTimestamp = killEvent.timestamp;

                if (killTimestamps.hasOwnProperty(roundNumber)) {
                    killTimestamps[roundNumber].push(killTimestamp);
                } else {
                    killTimestamps[roundNumber] = [killTimestamp];
                }
            }
        });
    }
}

// detect when the match is over and save the killTimestamps to a JSON file
function writeKillTimestampsToFileAndReset(data) {
    const previousMapPhase = readProperty(data, 'previously.map.phase');
    const currentMapPhase = readProperty(data, 'map.phase');

    if (previousMapPhase === 'live' && currentMapPhase === 'gameover') {
        const date = new Date();
        const formattedDate = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}-${String(date.getHours()).padStart(2, '0')}-${String(date.getMinutes()).padStart(2, '0')}`;
        const fileName = `${formattedDate}.json`;

        fs.writeFile(fileName, JSON.stringify(killTimestamps), (err) => {
            if (err) {
                console.error('Error writing JSON file:', err);
            } else {
                console.log(`Saved killTimestamps to ${fileName}`);
            }
        });

        // Clear the killTimestamps structure
        Object.keys(killTimestamps).forEach((key) => delete killTimestamps[key]);
    }
}


/**
 * Helper function to read values under nested paths from objects
 *
 * @param {object} container - Object container
 * @param {string} propertyPath - Path to the property in the container
 *                                separated by dots, e.g. 'map.phase'
 * @return {mixed} Null if the object has no requested property, property value
 *                 otherwise
 */
function readProperty(container, propertyPath) {
    let value = null;
    const properties = propertyPath.split('.');

    for (const p of properties) {
        if (!container.hasOwnProperty(p)) {
            return null;
        }

        value = container[p];
        container = container[p];
    }

    return value;
}

server.listen(port, host);

console.log('Monitoring CS:GO rounds');