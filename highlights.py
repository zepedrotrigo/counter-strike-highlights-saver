import time, os, keyboard, json
from dotenv import dotenv_values
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from utils_ffmpeg import extract_subclip, concatenate_videoclips

vars = dotenv_values('.env')
vars["kills"] = []
vars["round_kills"] = 0
vars["SAVED_ROUND"] =  True
vars["SAVED_SCOREBOARD"] = False
clips = []
RECORDING = False

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

        round_kills = self.get_round_kills(payload)
        player_steamid = self.get_player_steamid(payload)
        map_phase = self.get_map_phase(payload)

        start(round_phase, round_kills, player_steamid, map_phase)

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
    _id = 0

    @classmethod
    def set_id(cls, value):
        cls._id = value

    @classmethod
    def increment_id(cls):
        cls._id += 1

    def __init__(self, start, end, type=""):
        self.__class__.increment_id()
        self.id = self.__class__._id
        self.start = (start - int(vars["DELAY_BEFORE"])) - int(vars["RECORDING_START_TIME"])
        self.end = (end + int(vars["DELAY_AFTER"])) - int(vars["RECORDING_START_TIME"])
        self.name = f"clip{self.id:02d}{type}"



def start_recording():
    global vars

    keyboard.press(vars["RECORDING_HOTKEY"])
    return time.time()

def save_kills_timestamps(round_kills):
    global vars

    if round_kills != vars["round_kills"]:
        vars[f"kills"].append(time.time())
        vars["round_kills"] = round_kills
        print(f"Kill {vars['round_kills']} detected at {time.strftime('%H:%M:%S')}")
    
def detect_highlights(clips):
    global vars

    ignore = []
    clips_sorted = {} # they key of this dict preservers the order of the clips
    kill_times = vars["kills"]
    max_times = [int(vars[f"MAX_{i+1}K_TIME"]) for i in range(0, vars["round_kills"])]

    if len(kill_times) > 1:
        for l in reversed(range(len(kill_times))):
            if l in ignore: continue

            for f in range(l):
                if f in ignore: continue
                elements = list(range(f, l+1))
                idx = len(elements) - 1

                if (kill_times[l] - kill_times[f] < max_times[idx]) and kill_times[l] and l: # "and l" because f != l needs to be true
                    ignore += elements
                    clips_sorted[f] = Clip(kill_times[f],kill_times[l], f"_{len(elements)}k") # they key of this dict preservers the order of the clips

    if vars["SAVE_EVERY_FRAG"]:
        for i in range(len(kill_times)):
            if i not in ignore and kill_times[i] != 0:
                clips_sorted[i] = Clip(kill_times[i],kill_times[i]) # they key of this dict preservers the order of the clips

    for k in sorted(clips_sorted): # append to clips by kill order
        clips.append(clips_sorted[k])

    print(f"Clips detected: {len(clips_sorted)}")
    return clips

def process_clips(clips):
    global vars
 
    if len(clips):
        os.system("cls")
        recording = str(sorted(Path(vars["RECORDINGS_PATH"]).iterdir(), key=(os.path.getmtime))[-1])
        dest_folder = vars["RECORDINGS_PATH"]+"\\"+(time.strftime("%d%b%Y_%Hh%Mmin")) #Create a new folder
        os.mkdir(dest_folder)

        for clip in clips:
            extract_subclip(recording, dest_folder, clip.name, clip.start, clip.end)
            print(f"Clip {clip.name} created")

        if vars["DELETE_RECORDING"]:
            os.remove(recording)
            print("Recording deleted")

        if vars["CREATE_MOVIE"]:
            clip_paths = sorted(Path(dest_folder).iterdir())
            f = open("concat_clips.txt", "w")

            for n in range(len(clips)):
                f.write("file '"  + str(clip_paths[n]) + "'\n")

            f.close()

            concatenate_videoclips("concat_clips.txt",dest_folder)
            os.remove("concat_clips.txt")
            print("Movie created")

def reset_vars():
    vars["kills"] = []
    vars["round_kills"] = 0
    vars["SAVED_ROUND"] = True

def start(round_phase, kills, player_steamid, map_phase):
    global clips, vars, RECORDING

    #time.sleep(1)
    #print(f"Round phase: {round_phase}, Kills: {kills}, Player steamid: {player_steamid}, Map phase: {map_phase}")
    if map_phase != None:
        if not RECORDING:
            vars["RECORDING_START_TIME"] = start_recording()
            RECORDING = True
            print("Recording started")

        if round_phase == "live" or (round_phase == "over" and not vars["SAVED_ROUND"]):
            if player_steamid == vars["STEAMID"] and kills: # if alive
                save_kills_timestamps(kills)
                vars["SAVED_ROUND"] = False
            
            if round_phase == "over":
                save_kills_timestamps(kills)
                clips = detect_highlights(clips)
                reset_vars()

        if map_phase == "gameover" and not vars["SAVED_SCOREBOARD"] and vars["SHOW_SCOREBOARD"] and Clip._id: # record final scoreboard
            start = time.time()+20
            clip1 = Clip(start, start+int(vars["SHOW_SCOREBOARD"]), "_scoreboard")
            clips.append(clip1)
            vars["SAVED_SCOREBOARD"] = True
            print("Scoreboard clip added.")
            reset_vars()
    
    # if match ends and clips exist, then process them
    elif map_phase == None and Clip._id:
        reset_vars()
        Clip.set_id(0) # reset clip id
        vars["SAVED_SCOREBOARD"] = False

        if RECORDING: # stop recording
            start_recording()
            RECORDING = False
            print("Recording stopped")

        process_clips(clips)


if __name__ == "__main__":
    try:
        server = MyServer(('localhost', 3000), MyRequestHandler)
        server.serve_forever()
    except:
        if RECORDING: # stop recording
            start_recording()