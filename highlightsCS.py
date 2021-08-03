import json, time, os, collections
from http.server import BaseHTTPRequestHandler, HTTPServer
from obswebsocket import obsws, requests
from pathlib import Path
from fortnyce_ffmpeg import extract_subclip, concatenate_videoclips

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
        self.send_response(200)
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
    global DELAY_BEFORE, DELAY_AFTER, RECORDING_START_TIME

    def __init__(self, start_time, end_time, sufix, round=ROUND):
        self.start_time = (start_time - DELAY_BEFORE) - RECORDING_START_TIME
        self.end_time = (end_time + DELAY_AFTER) - RECORDING_START_TIME
        self.name = "clip"+round+sufix


def start_recording():
    global RECORDING_START_TIME

    ws.call(requests.StartRecording())
    RECORDING_START_TIME = time.time()

def stop_recording():
    ws.call(requests.StopRecording())

def listen_to_kills(round_kills):
    global ROUND_KILLS, T1, T2, T3, T4, T5

    if round_kills != ROUND_KILLS:
        locals()["T"+str(round_kills)] = time.time() # locals()["var1"] = 1 -> var1 = 1
        ROUND_KILLS = round_kills

def detect_highlights():
    global SAVE_EVERY_FRAG, MAX_2K_TIME, MAX_3K_TIME, MAX_4K_TIME, MAX_5K_TIME, T1, T2, T3, T4, T5, clips

    if (T5 - T1 < MAX_5K_TIME) and T5: # check if Penta kill
        clips.append(Clip(T5, T1, "_5k"))

    elif (T5 - T2 < MAX_4K_TIME) and T5: # check if quadra kill (case 5-2)
        if SAVE_EVERY_FRAG and T1 != 0:
            clips.append(Clip(T1, T1, ""))

        clips.append(Clip(T5, T2, "_4k"))

    elif (T4 - T1 < MAX_4K_TIME) and T4: # check if quadra kill (case 4-1)
        clips.append(Clip(T4, T1, "_4k"))

        if SAVE_EVERY_FRAG and T5:
            clips.append(Clip(T5, T5, ""))

    elif (T5 - T3 < MAX_3K_TIME) and T5: # check if triple kill (case 5-3)
        if (T2 - T1 < MAX_2K_TIME) and T2: # triple kill (case 5-3) and double kill (case 2-1)
            clips.append(Clip(T2, T1, "_2k"))
            clips.append(Clip(T5, T3, "_3k"))

        else: # save triple kill
            if SAVE_EVERY_FRAG:
                if T1:
                    clips.append(Clip(T1, T1, ""))
                if T2:
                    clips.append(Clip(T2, T2, ""))

            clips.append(Clip(T5, T3, "_3k"))

    elif (T4 - T2 < MAX_3K_TIME) and T4: #check if triple kill (case 4-2)
        if SAVE_EVERY_FRAG:
            if T1:
                clips.append(Clip(T1, T1, ""))

        clips.append(Clip(T4, T2, "_3k"))

        if SAVE_EVERY_FRAG:
            if T5:
                clips.append(Clip(T5, T5, ""))

    elif (T3 - T1 < MAX_3K_TIME) and T3: #check if triple kill (case 3-1)
        if (T5 - T4 < MAX_2K_TIME) and T5: #triple kill(3-1) amd double kill(5-4)
            clips.append(Clip(T3, T1, "_3k"))
            clips.append(Clip(T5, T4, "_2k"))

        else:
            clips.append(Clip(T3, T1, "_3k"))

            if SAVE_EVERY_FRAG:
                if T4:
                    clips.append(Clip(T4, T4, ""))
                if T5:
                    clips.append(Clip(T5, T5, ""))

    elif ( (T2 - T1 < MAX_2K_TIME) and T2 and # double kill case(2-1) AND
            (T4 - T3 < MAX_2K_TIME) and T4 ): # double kill case (4-3)
            clips.append(Clip(T2, T1, "_2k"))
            clips.append(Clip(T4, T3, "_2k"))

            if SAVE_EVERY_FRAG:
                if T5:
                    clips.append(Clip(T5, T5, ""))

    elif ( (T2 - T1 < MAX_2K_TIME) and T2 and #double kill case(2-1) AND
            (T5 - T4 < MAX_2K_TIME) and T5 ): # double kill case (5-4)
            clips.append(Clip(T2, T1, "_2k"))
            clips.append(Clip(T5, T4, "_2k"))

            if SAVE_EVERY_FRAG:
                if T5:
                    clips.append(Clip(T5, T5, ""))

    elif ( (T3 - T2 < MAX_2K_TIME) and T3 and #double kill case(3-2) AND
            (T5 - T4 < MAX_2K_TIME) and T5 ): #double kill case (5-4)
            clips.append(Clip(T3, T2, "_2k"))
            clips.append(Clip(T5, T4, "_2k"))

            if SAVE_EVERY_FRAG:
                if T5:
                    clips.append(Clip(T5, T5, ""))

    elif (T2 - T1 < MAX_2K_TIME) and T2: #double kill case(2-1)
        clips.append(Clip(T2, T1, "_2k"))

        if SAVE_EVERY_FRAG:
            if T3:
                clips.append(Clip(T3, T3, ""))
            if T4:
                clips.append(Clip(T4, T4, ""))
            if T5:
                clips.append(Clip(T5, T5, ""))

    elif (T3 - T2 < MAX_2K_TIME) and T3: #double kill case (3-2)
        if SAVE_EVERY_FRAG:
            if T1:
                clips.append(Clip(T1, T1, ""))

        clips.append(Clip(T3, T2, "_2k"))

        if SAVE_EVERY_FRAG:
            if T4:
                clips.append(Clip(T4, T4, ""))
            if T5:
                clips.append(Clip(T5, T5, ""))

    elif (T4 - T3 < MAX_2K_TIME) and T4: #double kill case (4-3)
        if SAVE_EVERY_FRAG:
            if T1:
                clips.append(Clip(T1, T1, ""))
            if T2:
                clips.append(Clip(T2, T2, ""))

        clips.append(Clip(T4, T3, "_2k"))

        if SAVE_EVERY_FRAG and T5:
            clips.append(Clip(T5, T5, ""))

    elif (T5 - T4 < MAX_2K_TIME) and T5: #double kill case (5-4)
        if SAVE_EVERY_FRAG:
            if T1:
                clips.append(Clip(T1, T1, ""))
            if T2:
                clips.append(Clip(T2, T2, ""))
            if T3:
                clips.append(Clip(T3, T3, ""))

        clips.append(Clip(T5, T4, "_2k"))

        if SAVE_EVERY_FRAG:
            if T5:
                clips.append(Clip(T5, T5, ""))

    else: # no highlight detected
        if SAVE_EVERY_FRAG:
            if T1:
                clips.append(Clip(T1, T1, ""))
            if T2:
                clips.append(Clip(T2, T2, ""))
            if T3:
                clips.append(Clip(T3, T3, ""))
            if T4:
                clips.append(Clip(T4, T4, ""))
            if T5:
                clips.append(Clip(T5, T5, ""))

def save_round(player_steamid, round_kills):
    global T1, T2, T3, T4, T5, STEAMID, RECORDING_START_TIME, PROCESSED, SAVED_ROUND, epoch_timestamps, timestamps

    if player_steamid == STEAMID: # needs to be here in case of last frag of the round
        listen_to_kills(round_kills)

    detect_highlights() # Check for highlights and save them (the timestamps) in an ordered dict

    T1, T2, T3, T4, T5, PROCESSED = 0
    SAVED_ROUND = 1

def process_clips():  
    global DELETE_RECORDING, RECORDINGS_PATH, CREATE_MOVIE, PROCESSED, clips


    if len(os.listdir(RECORDINGS_PATH)) and len(clips):
        recording = str(sorted(Path(RECORDINGS_PATH).iterdir(), key=(os.path.getmtime))[-1])
        dest_folder = RECORDINGS_PATH+"\\"+(time.strftime("%d%b%Y_%Hh%Mmin")) #Create a new folder
        os.mkdir(dest_folder)

        for clip in clips:
            extract_subclip(recording, dest_folder, clip.name, clip.start_time, clip.end_time)

        if DELETE_RECORDING:
            os.remove(recording)

        if CREATE_MOVIE:
            clip_paths = sorted(Path(dest_folder).iterdir(), key=(os.path.getmtime))
            f = open("concat_clips.txt", "w")

            for n in range(0, len(clips)):
                f.write("file '"  + str(clip_paths[-n-1]) + "'\n")

            f.close()

            concatenate_videoclips("concat_clips.txt",dest_folder)
            os.remove("concat_clips.txt")

        PROCESSED = True

def my_logic(round_phase, round_kills, player_steamid, map_phase):
    global SAVED_ROUND, PROCESSED, RECORDING, ROUND
    if map_phase == "live":
        if round_phase == "live":
            if not RECORDING:
                start_recording()  

            if player_steamid==vars["steamid"] and round_kills: # if alive
                listen_to_kills(round_kills)

            SAVED_ROUND = False

        elif round_phase == "over" and not SAVED_ROUND and round_kills:
            save_round(player_steamid, round_kills)
            ROUND += 1

    elif not PROCESSED and map_phase == None:
        if RECORDING:
            stop_recording()

        process_clips()

try:
    clips = []
    f1 = open("config.cfg", 'r')
    lines = f1.readlines()
    f1.close()

    RECORDING_START_TIME = ROUND_KILLS = T1 = T2 = T3 = T4 = T5 = PROCESSED = SAVED_ROUND = RECORDING = 0
    ROUND = 1
    for line in lines: # locals()["var1"] = 1 -> var1 = 1
        locals()[line.split()[0].upper()] = line.split()[1] # STEAMID, RECORDINGS_PATH, DELETE_RECORDING, SAVE_EVERY_FRAG, CREATE_MOVIE, DELAY_AFTER, DELAY_BEFORE, MAX_2K_TIME, MAX_3K_TIME, MAX_4K_TIME, MAX_5K_TIME

    ws = obsws("localhost", 4444, "secret")
    ws.connect()
    server = MyServer(('localhost', 3000), 'MYTOKENHERE', MyRequestHandler)
    server.serve_forever()

except (KeyboardInterrupt, SystemExit):
    if RECORDING:
        ws.call(requests.StopRecording())

    server.server_close()
    ws.disconnect()