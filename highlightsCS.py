import json, time, os
from http.server import BaseHTTPRequestHandler, HTTPServer
from obswebsocket import obsws, requests
from pathlib import Path
from fortnyce_ffmpeg import extract_subclip, concatenate_videoclips

clips = []
f1 = open("config.cfg", 'r')
lines = f1.readlines()
f1.close()

RECORDING_START_TIME = ROUND_KILLS = T1 = T2 = T3 = T4 = T5 = SAVED_ROUND = RECORDING = 0
CLIP_COUNTER = 1
for line in lines: # locals()["var1"] = 1 -> var1 = 1
    var = line.split()[0].upper()
    val = line.split()[1]
    val = int(val) if val.isnumeric() else val.replace('"','')
    locals()[var] = val # STEAMID, DELETE_RECORDING, SAVE_EVERY_FRAG, CREATE_MOVIE, DELAY_AFTER, DELAY_BEFORE, MAX_2K_TIME, MAX_3K_TIME, MAX_4K_TIME, MAX_5K_TIME

#----------------------------------------------------Classes--------------------------------------------------------------------
class MyServer(HTTPServer):
    def __init__(self, server_address, token, RequestHandler):
        self.auth_token = token

        super(MyServer, self).__init__(server_address, RequestHandler)

        # You can store states over multiple requests in the server 
        self.round_phase = None

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode('utf-8')

        self.parse_payload(json.loads(body))

        self.send_header('Content-type', 'text/html')
        #self.send_response(200)
        self.end_headers()

    def is_payload_authentic(self, payload):
        if 'auth' in payload and 'token' in payload['auth']:
            return payload['auth']['token'] == server.auth_token
        else:
            return False

    def parse_payload(self, payload):
        # Ignore unauthenticated payloads
        if not self.is_payload_authentic(payload):
            return None

        round_phase = self.get_round_phase(payload)

        if round_phase != self.server.round_phase:
            self.server.round_phase = round_phase
            #print('New round phase: %s' % round_phase)

        round_kills = self.get_round_kills(payload)
        player_steamid = self.get_player_steamid(payload)
        map_phase = self.get_map_phase(payload)

        my_logic(round_phase, round_kills, player_steamid, map_phase)

    def get_player_steamid(self, payload):
        if 'player' in payload and 'steamid' in payload['player']:
            return payload['player']['steamid']
        else:
            return None

    def get_round_kills(self, payload):
        if 'player' in payload and 'state' in payload['player'] and 'round_kills' in payload['player']['state']:
            return payload['player']['state']['round_kills']
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

class Clip:
    def __init__(self, start_time, end_time, clip_counter, sufix):
        self.start_time = (start_time - DELAY_BEFORE) - RECORDING_START_TIME
        self.end_time = (end_time + DELAY_AFTER) - RECORDING_START_TIME
        self.name = "clip"+str(clip_counter)+sufix

    def __str__(self) -> str:
        return f"Name: {self.name} Start: {self.start_time:.2f} End: {self.end_time:.2f}"

def start_recording():
    ws.call(requests.StartRecording())
    return time.time()


def stop_recording():
    ws.call(requests.StopRecording())

def listen_to_kills(round_kills, prev_val):
    global T1, T2, T3, T4, T5

    if round_kills != prev_val:
        globals()["T"+str(round_kills)] = time.time() # globals()["T"+"1"] = 123 -> T1 = 123
        prev_val += 1
    
    return prev_val

def detect_highlights(clips, kill_times, max_times, save_every_frag):
    global CLIP_COUNTER
    ignore = []
    clips_sorted = {} # they key of this dict preservers the order of the clips

    if len(kill_times) > 1:
        for l in reversed(range(len(kill_times))):
            if l in ignore: continue

            for f in range(l):
                if f in ignore: continue

                if (kill_times[l] - kill_times[f] < max_times[l]) and kill_times[l] and l: # "and l" because f != l needs to be true
                    elements = list(range(f, l+1))
                    ignore += elements
                    clips_sorted[f] = Clip(kill_times[f],kill_times[l], CLIP_COUNTER, f"_{len(elements)}k") # they key of this dict preservers the order of the clips
                    CLIP_COUNTER += 1

    if save_every_frag:
        for i in range(len(kill_times)):
            if i not in ignore and kill_times[i] != 0:
                clips_sorted[i] = Clip(kill_times[i],kill_times[i], CLIP_COUNTER, "") # they key of this dict preservers the order of the clips
                CLIP_COUNTER += 1

    for k in sorted(clips_sorted): # append to clips by kill order
        clips.append(clips_sorted[k])

    return clips

def process_clips(clips, delete_recording, recordings_path, create_movie):  
    if len(clips):
        recording = str(sorted(Path(recordings_path).iterdir(), key=(os.path.getmtime))[-1])
        dest_folder = recordings_path+"\\"+(time.strftime("%d%b%Y_%Hh%Mmin")) #Create a new folder
        os.mkdir(dest_folder)

        for clip in clips:
            extract_subclip(recording, dest_folder, clip.name, clip.start_time, clip.end_time)

        if delete_recording:
            os.remove(recording)

        if create_movie:
            clip_paths = sorted(Path(dest_folder).iterdir())
            f = open("concat_clips.txt", "w")

            for n in range(len(clips)):
                f.write("file '"  + str(clip_paths[n]) + "'\n")

            f.close()

            concatenate_videoclips("concat_clips.txt",dest_folder)
            os.remove("concat_clips.txt")

def my_logic(round_phase, round_kills, player_steamid, map_phase):
    global clips, SAVED_ROUND, RECORDING, RECORDING_START_TIME, CLIP_COUNTER, STEAMID, ROUND_KILLS, SAVE_EVERY_FRAG, DELETE_RECORDING, RECORDINGS_PATH, CREATE_MOVIE
    global T1, T2, T3, T4, T5, MAX_2K_TIME, MAX_3K_TIME, MAX_4K_TIME, MAX_5K_TIME

    if map_phase == "live":
        if round_phase == "live":
            if not RECORDING:
                RECORDING_START_TIME = start_recording()
                RECORDING = 1

            if player_steamid == STEAMID and round_kills: # if alive
                ROUND_KILLS = listen_to_kills(round_kills, ROUND_KILLS) # ROUND_KILLS is the prev value to see if it was evaluated already or not
            
            SAVED_ROUND = 0

        elif round_phase == "over" and not SAVED_ROUND and round_kills:            
            if STEAMID == player_steamid: # needs to be here in case of last frag of the round
                listen_to_kills(round_kills, ROUND_KILLS) # ROUND_KILLS is the prev value to see if it was evaluated already or not
            
            clips = detect_highlights(clips, [T1,T2,T3,T4,T5], [0,MAX_2K_TIME,MAX_3K_TIME,MAX_4K_TIME,MAX_5K_TIME], SAVE_EVERY_FRAG)
            T1 = T2 = T3 = T4 = T5 = ROUND_KILLS = 0
            SAVED_ROUND = 1

    elif map_phase == None and CLIP_COUNTER != 1:
        if RECORDING:
            stop_recording()
            RECORDING = 0

        process_clips(clips, DELETE_RECORDING, RECORDINGS_PATH, CREATE_MOVIE)
        clips = []
        CLIP_COUNTER = 1

try:
    ws = obsws("localhost", 4444, "secret")
    ws.connect()
    recording_path = ws.call(requests.GetRecordingFolder())
    RECORDINGS_PATH = recording_path.datain["rec-folder"]
    server = MyServer(('localhost', 3000), 'MYTOKENHERE', MyRequestHandler)
    server.serve_forever()

except (KeyboardInterrupt, SystemExit):
    if RECORDING:
       stop_recording()

    server.server_close()
    ws.disconnect()