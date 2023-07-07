import time, os, keyboard, json
from http.server import BaseHTTPRequestHandler, HTTPServer

PLAYING_MUSIC = False

class MyServer(HTTPServer):
    def __init__(self, server_address, RequestHandler):
        super(MyServer, self).__init__(server_address, RequestHandler)
        self.round_phase = None
        print(f'Server started on {server_address}')


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode('utf-8')
        self.parse_payload(json.loads(body))
        #self.send_header('Content-type', 'text/html')
        #self.end_headers()

    def parse_payload(self, payload):
        round_phase = self.get_round_phase(payload)

        if round_phase != self.server.round_phase:
            self.server.round_phase = round_phase
            #print('New round phase: %s' % round_phase)

        player_steamid = self.get_player_steamid(payload)
        provider_steamid = self.get_provider_steamid(payload)
        map_phase = self.get_map_phase(payload)
        player_health = self.get_player_health(payload)
        start(provider_steamid, player_steamid, map_phase, round_phase, player_health)

    def get_provider_steamid(self, payload):
        if 'provider' in payload and 'steamid' in payload['provider']:
            return payload['provider']['steamid']
        else:
            return None

    def get_player_steamid(self, payload):
        if 'player' in payload and 'steamid' in payload['player']:
            return payload['player']['steamid']
        else:
            return None

    def get_map_phase(self, payload):
        if 'map' in payload and 'phase' in payload['map']:
            return payload['map']['phase']
        else:
            return None

    def get_round_phase(self, payload):
        if 'round' in payload and 'phase' in payload['round']:
            return payload['round']['phase']
        else:
            return None

    def get_player_health(self, payload):
        if 'player' in payload and 'state' in payload['player'] and 'health' in payload['player']['state']:
            return payload['player']['state']['health']
        else:
            return None


def toggle_play():
    global PLAYING_MUSIC
    print("Toggling play/pause")
    keyboard.send('play/pause')
    PLAYING_MUSIC = not PLAYING_MUSIC

def start(provider_steamid, player_steamid, map_phase, round_phase, player_health):
    global PLAYING_MUSIC

    if map_phase == 'live':
        if player_steamid != provider_steamid:
            return 

        if round_phase == "live":
            if PLAYING_MUSIC and player_health != 0:
                toggle_play()
            elif not PLAYING_MUSIC and player_health == 0:
                toggle_play()

    
    elif not PLAYING_MUSIC:
        toggle_play()

if __name__ == "__main__":
    server = MyServer(('localhost', 3000), MyRequestHandler)
    server.serve_forever()