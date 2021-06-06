import json, time, os, random, keyboard, collections, pickle, win32api
from http.server import BaseHTTPRequestHandler, HTTPServer
from re import MULTILINE
from pathlib import Path
from colorama import Fore
from pygame import mixer
from fortnyce_ffmpeg import extract_subclip, concatenate_videoclips
from win32gui import GetWindowText, GetForegroundWindow

vars = {
    "steamid":"76561198210384665",
    "delete_recording":False,
    "processed":False,
    "stop_hotkey":"alt+f9",
    "start_hotkey":"alt+f9",
    "save_every_frag":True,
    "endround_music_volume":100,
    "spec_music_volume":50,
    "spec_music":False,
    "endround_music":False,
    "endround_music_path":"",
    "spec_music_path":"",
    "endround_music":False,
    "create_movie":False,
    "delay_after":3,
    "delay_before":5,
    "input_2k_time":12,
    "input_3k_time":15,
    "input_4k_time":20,
    "input_5k_time":30,
    "recordings_path":"",
    "sound":"None",
    "endround_music_playing":False,
    "spec_music_playing":False,
    "recording":False,
    "recording_start_time":"None",
    "last_listen":"None",
    "round":1,
    "t1":0,
    "t2":0,
    "t3":0,
    "t4":0,
    "t5":0
}

epoch_timestamps = collections.OrderedDict()
timestamps = []
file_prefixes = []

os.system('cls')
os.system('python tkinter_interface.py') #call tkinter interface here

try:
    path = os.path.dirname(os.path.abspath(__file__)) + "_user_config.pkl"

    with open(path, 'rb') as f:
        vars["start_hotkey"] = pickle.load(f)
        vars["stop_hotkey"] = pickle.load(f)
        vars["recordings_path"] = pickle.load(f)
        vars["input_5k_time"] = pickle.load(f)
        vars["input_4k_time"] = pickle.load(f)
        vars["input_3k_time"] = pickle.load(f)
        vars["input_2k_time"] = pickle.load(f)
        vars["delay_before"] = pickle.load(f)
        vars["delay_after"] = pickle.load(f)
        vars["create_movie"] = pickle.load(f)
        vars["spec_music"] = pickle.load(f)
        vars["endround_music"] = pickle.load(f)
        vars["spec_music_path"] = pickle.load(f)
        vars["endround_music_path"] = pickle.load(f)
        vars["spec_music_volume"] = pickle.load(f)
        vars["endround_music_volume"] = pickle.load(f)
        vars["save_every_frag"] = pickle.load(f)
        vars["steamid"] = pickle.load(f)
except:
    pass

def start_recording(hotkey):
    global vars
    recording = vars["recording"]

    if not recording:
        while GetWindowText(GetForegroundWindow()) != "Counter-Strike: Global Offensive":
            time.sleep(1)

        keyboard.press_and_release(hotkey)
        vars["recording_start_time"] = time.time()
        vars["recording"] = True

def listen_to_kills(round_kills):
    global vars

    if round_kills != vars["last_listen"]:
        keyname = "t"+str(round_kills)
        vars[keyname] = time.time()
        vars["last_listen"] = round_kills

def play_music(path,volume, type):
    global vars

    mixer.init() # tem que estar aqui porcausa do garbage collector
    randomfile = random.choice(os.listdir(path))
    while "AlbumArt" in randomfile:
        randomfile = random.choice(os.listdir(path))

    song = path + '\\' + randomfile
    sound=mixer.Sound(song)
    sound.set_volume(volume*0.01)
    mixer.Sound.play(sound)

    if type == "spec":
        vars["spec_music_playing"] = True
    else:
        vars["endround_music_playing"] = True

    vars["sound"] = sound
    print("playing song: ", randomfile)

def stop_music(sound, type):
    global vars
    if vars["endround_music_playing"] or vars["spec_music_playing"]:
        try:
            mixer.Sound.stop(sound)
            mixer.quit() #garbage collector
        except:
            pass #TODO se houver problem da musica nao tocar, meter um try mixer.quit() dentro deste except

        if type == "spec":
            vars["spec_music_playing"] = False
        else:
            vars["endround_music_playing"] = False

        vars["sound"] = None
        print("Stopping music!")

def detect_highlights():
    global vars, epoch_timestamps, file_prefixes
    t1 = vars["t1"]
    t2 = vars["t2"]
    t3 = vars["t3"]
    t4 = vars["t4"]
    t5 = vars["t5"]

    if (t5 - t1 < vars["input_5k_time"]) and t5 != 0: # check if Penta kill
        epoch_timestamps[t5] = t1
        file_prefixes.append("_5K")
        print("Ace detected")

    elif (t5 - t2 < vars["input_4k_time"]) and t5 != 0: # check if quadra kill (case 5-2)
        if vars["save_every_frag"] and t1 != 0:
            epoch_timestamps[t1] = t1
            file_prefixes.append("")

        epoch_timestamps[t5] = t2
        file_prefixes.append("_4K")
        print("Quadra kill detected")

    elif (t4 - t1 < vars["input_4k_time"]) and t4 != 0: # check if quadra kill (case 4-1)
        epoch_timestamps[t4] = t1
        file_prefixes.append("_4K")
        print("Quadra kill detected")

        if vars["save_every_frag"] and t5 != 0:
            epoch_timestamps[t5] = t5
            file_prefixes.append("")

    elif (t5 - t3 < vars["input_3k_time"]) and t5 != 0: # check if triple kill (case 5-3)
        if (t2 - t1 < vars["input_2k_time"]) and t2 != 0: # triple kill (case 5-3) and double kill (case 2-1)
            epoch_timestamps[t2] = t1
            epoch_timestamps[t5] = t3
            file_prefixes.append("_2K")
            file_prefixes.append("_3K")
            print("Double kill + Triple kill detected")
        else: # save triple kill
            if vars["save_every_frag"]:
                if t1 != 0:
                    epoch_timestamps[t1] = t1
                    file_prefixes.append("")
                if t2 != 0:
                    epoch_timestamps[t2] = t2
                    file_prefixes.append("")

            epoch_timestamps[t5] = t3
            file_prefixes.append("_3K")
            print("Triple kill detected")

    elif (t4 - t2 < vars["input_3k_time"]) and t4 != 0: #check if triple kill (case 4-2)
        if vars["save_every_frag"]:
            if t1 != 0:
                epoch_timestamps[t1] = t1
                file_prefixes.append("")

        epoch_timestamps[t4] = t2
        file_prefixes.append("_3K")
        print("Triple kill detected")

        if vars["save_every_frag"]:
            if t5 != 0:
                epoch_timestamps[t5] = t5
                file_prefixes.append("")

    elif (t3 - t1 < vars["input_3k_time"]) and t3 != 0: #check if triple kill (case 3-1)
        if (t5 - t4 < vars["input_2k_time"]) and t5 != 0: #triple kill(3-1) amd double kill(5-4)
            epoch_timestamps[t3] = t1
            epoch_timestamps[t5] = t4
            file_prefixes.append("_3K")
            file_prefixes.append("_2K")
            print("Triple kill + double kill detected")
        else:
            epoch_timestamps[t3] = t1
            file_prefixes.append("_3K")
            print("Triple kill detected")

            if vars["save_every_frag"]:
                if t4 != 0:
                    epoch_timestamps[t4] = t4
                    file_prefixes.append("")
                if t5 != 0:
                    epoch_timestamps[t5] = t5
                    file_prefixes.append("")

    elif ( (t2 - t1 < vars["input_2k_time"]) and (t2 != 0) and # double kill case(2-1) AND
            (t4 - t3 < vars["input_2k_time"]) and (t4 != 0) ): # double kill case (4-3)
            epoch_timestamps[t2] = t1
            epoch_timestamps[t4] = t3
            file_prefixes.append("_2K")
            file_prefixes.append("_2K")
            print("Double kill + Double kill detected")

            if vars["save_every_frag"]:
                if t5 != 0:
                    epoch_timestamps[t5] = t5
                    file_prefixes.append("")

    elif ( (t2 - t1 < vars["input_2k_time"]) and (t2 != 0) and #double kill case(2-1) AND
            (t5 - t4 < vars["input_2k_time"]) and (t5 != 0) ): # double kill case (5-4)
            epoch_timestamps[t2] = t1
            epoch_timestamps[t5] = t4
            file_prefixes.append("_2K")
            file_prefixes.append("_2K")
            print("Double kill + Double kill detected")

            if vars["save_every_frag"]:
                if t5 != 0:
                    epoch_timestamps[t5] = t5
                    file_prefixes.append("")

    elif ( (t3 - t2 < vars["input_2k_time"]) and (t3 != 0) and #double kill case(3-2) AND
            (t5 - t4 < vars["input_2k_time"]) and (t5 != 0) ): #double kill case (5-4)
            epoch_timestamps[t3] = t2
            epoch_timestamps[t5] = t4
            file_prefixes.append("_2K")
            file_prefixes.append("_2K")
            print("Double kill + Double kill detected")

            if vars["save_every_frag"]:
                if t5 != 0:
                    epoch_timestamps[t5] = t5
                    file_prefixes.append("")

    elif (t2 - t1 < vars["input_2k_time"]) and t2 != 0: #double kill case(2-1)
        epoch_timestamps[t2] = t1
        file_prefixes.append("_2K")
        print("Double kill detected")

        if vars["save_every_frag"]:
            if t3 != 0:
                epoch_timestamps[t3] = t3
                file_prefixes.append("")
            if t4 != 0:
                epoch_timestamps[t4] = t4
                file_prefixes.append("")
            if t5 != 0:
                epoch_timestamps[t5] = t5
                file_prefixes.append("")

    elif (t3 - t2 < vars["input_2k_time"]) and t3 != 0: #double kill case (3-2)
        if vars["save_every_frag"]:
            if t1 != 0:
                epoch_timestamps[t1] = t1
                file_prefixes.append("")

        epoch_timestamps[t3] = t2
        file_prefixes.append("_2K")
        print("Double kill detected")

        if vars["save_every_frag"]:
            if t4 != 0:
                epoch_timestamps[t4] = t4
                file_prefixes.append("")
            if t5 != 0:
                epoch_timestamps[t5] = t5
                file_prefixes.append("")

    elif (t4 - t3 < vars["input_2k_time"]) and t4 != 0: #double kill case (4-3)
        if vars["save_every_frag"]:
            if t1 != 0:
                epoch_timestamps[t1] = t1
                file_prefixes.append("")
            if t2 != 0:
                epoch_timestamps[t2] = t2
                file_prefixes.append("")

        epoch_timestamps[t4] = t3
        file_prefixes.append("_2K")
        print("Double kill detected")

        if vars["save_every_frag"] and t5 != 0:
            epoch_timestamps[t5] = t5
            file_prefixes.append("")

    elif (t5 - t4 < vars["input_2k_time"]) and t5 != 0: #double kill case (5-4)
        if vars["save_every_frag"]:
            if t1 != 0:
                epoch_timestamps[t1] = t1
                file_prefixes.append("")
            if t2 != 0:
                epoch_timestamps[t2] = t2
                file_prefixes.append("")
            if t3 != 0:
                epoch_timestamps[t3] = t3
                file_prefixes.append("")

        epoch_timestamps[t5] = t4
        file_prefixes.append("_2K")
        print("Double kill detected")

        if vars["save_every_frag"]:
            if t5 != 0:
                epoch_timestamps[t5] = t5
                file_prefixes.append("")

    else: # no highlight detected
        if vars["save_every_frag"]:
            if t1 != 0:
                epoch_timestamps[t1] = t1
                file_prefixes.append("")
            if t2 != 0:
                epoch_timestamps[t2] = t2
                file_prefixes.append("")
            if t3 != 0:
                epoch_timestamps[t3] = t3
                file_prefixes.append("")
            if t4 != 0:
                epoch_timestamps[t4] = t4
                file_prefixes.append("")
            if t5 != 0:
                epoch_timestamps[t5] = t5
                file_prefixes.append("")

def save_highlights():
    global vars, timestamps, epoch_timestamps

    for key in epoch_timestamps:
        start_kill_time = epoch_timestamps[key]
        end_kill_time = key
        clip_start_time = (start_kill_time - vars["delay_before"]) - vars["recording_start_time"]
        clip_end_time = (end_kill_time + vars["delay_after"])- vars["recording_start_time"]
        timestamps.append([clip_start_time,clip_end_time])

def save_round(player_steamid, round_kills):
    global vars, epoch_timestamps, timestamps

    if player_steamid==vars["steamid"] and round_kills != 0: # needs to be here in case of last frag of the round
        listen_to_kills(round_kills)

    detect_highlights() # Check for highlights and save them (the timestamps) in an ordered dict
    
    if len(epoch_timestamps) != 0:
        save_highlights() # Save detected highlights by appending them to timestamps
        kill_1 = "{:.2f}s".format(max(0,vars["t1"]-vars["recording_start_time"]))
        kill_2 = "{:.2f}s".format(max(0,vars["t2"]-vars["recording_start_time"]))
        kill_3 = "{:.2f}s".format(max(0,vars["t3"]-vars["recording_start_time"]))
        kill_4 = "{:.2f}s".format(max(0,vars["t4"]-vars["recording_start_time"]))
        kill_5 = "{:.2f}s".format(max(0,vars["t5"]-vars["recording_start_time"]))
        print("--------------------------\nEnd of round {}. Clips Saved!\n\n1st kill: {} | 2nd kill: {} | 3rd kill: {} | 4th kill: {} | 5th kill: {}\n--------------------------\n\n".format(vars["round"],kill_1,kill_2,kill_3,kill_4,kill_5))
    else:
        print("--------------------------\nEnd of round {}. No clips Saved!\n--------------------------\n\n".format(vars["round"]))
    vars["t1"] = 0 #reset timers
    vars["t2"] = 0
    vars["t3"] = 0
    vars["t4"] = 0
    vars["t5"] = 0
    vars["round"] += 1
    vars["processed"] = False
    vars["saved_round"] = True

def process_clips():  
    global vars, timestamps, epoch_timestamps, file_prefixes

    subclips_created = 0

    if len(os.listdir(vars["recordings_path"])) != 0 and len(timestamps) != 0:
        files_paths = sorted(Path(vars["recordings_path"]).iterdir(), key=(os.path.getmtime))
        recording_path = str(files_paths[-1])
        counter2 = len(timestamps) # sufix name (_clip1)
        dirname = vars["recordings_path"]+"\\"+(time.strftime("%d%b%Y_%Hh%Mmin")) #Create a new folder
        os.mkdir(dirname)

        for lst in reversed(timestamps):
            try: # Este try tem que estar aqui caso haja uma colateral (2 mortes ao mesmo tempo com 1 tiro fica tudo fodido)
                file_prefix = file_prefixes.pop() #obter prefix_name (2k_, 3k_, 4k_, 5k_)
            except:
                file_prefix = ""
            clip_start_time = lst[0]
            clip_end_time = lst[1]
            subclip_name = "clip"+str(counter2)+file_prefix
            extract_subclip(recording_path, clip_start_time, clip_end_time,dirname, subclip_name)
            counter2 -= 1
            subclips_created += 1

        if vars["delete_recording"]:
            os.remove(recording_path)

        if vars["create_movie"]:
            clips_to_merge_paths = sorted(Path(dirname).iterdir(), key=(os.path.getmtime))
            list_of_clips_by_order = []

            for n in range(0, subclips_created):
                clip_to_merge_path = str(clips_to_merge_paths[-n-1]) # counter = -1 para ir buscar os videos mais recentes
                list_of_clips_by_order.append(clip_to_merge_path)

            f = open("concat_clips.txt", "w")
            for path in list_of_clips_by_order:
                f.write("file '"  + path + "'\n")
            f.close()

            concatenate_videoclips("concat_clips.txt",dirname)
            os.remove("concat_clips.txt")

        vars["processed"] = True
        timestamps = []
        epoch_timestamps = collections.OrderedDict()
        file_prefixes = []

        os.system('cls')
        print("steamcommunity.com/id/fortnyce  github.com/zepedrotrigo")
        print(Fore.GREEN + "Don't close. Keep open\nVideos created!" + Fore.WHITE)

def my_logic(round_phase, round_kills, player_steamid, map_phase, bomb_state):
    global vars, epoch_timestamps, timestamps, file_prefixes
    if map_phase == "live":
        if round_phase == "live":
            start_recording(vars["start_hotkey"])  
            vars["endround_music_playing"] = False

            if player_steamid==vars["steamid"]: # if alive
                if round_kills != 0:
                    listen_to_kills(round_kills)

                if vars["spec_music_playing"]:
                    stop_music(vars["sound"], "spec")

            elif player_steamid != vars["steamid"]: #if dead
                if vars["spec_music"] and not vars["spec_music_playing"]:
                    play_music(vars["spec_music_path"], vars["spec_music_volume"], "spec")

            vars["saved_round"] = False

        elif round_phase == "over":
            if vars["spec_music_playing"]:
                stop_music(vars["sound"], "spec")
            try:
                if vars["endround_music"] and not vars["endround_music_playing"] and bomb_state != "defused":
                    play_music(vars["endround_music_path"], vars["endround_music_volume"], "endround")
            except:
                print(vars["endround_music_playing"])
                print(vars)

            if not vars["saved_round"]:
                save_round(player_steamid, round_kills)

    elif not vars["processed"] and map_phase == None:
        stop_music(vars["sound"], "spec")

        if vars["recording"]:
            keyboard.press(vars["start_hotkey"])
            time.sleep(0.1)
            keyboard.release(vars["start_hotkey"])
            vars["recording"] = False
            process_clips()

def on_exit(signal_type):
    global vars
    recording = vars["recording"]

    if recording:
        keyboard.press_and_release(vars["stop_hotkey"])
    pass

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
        bomb_state = self.get_bomb_state(payload)

        my_logic(round_phase, round_kills, player_steamid, map_phase, bomb_state)

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

    def get_bomb_state(self, payload):
        if 'round' in payload and 'bomb' in payload['round']:
            return payload['round']['bomb']
        else:
            return None

    def log_message(self, format, *args):
        """
        Prevents requests from printing into the console
        """
        return

#---------------------------------------------------------MAIN---------------------------------------------------------------
win32api.SetConsoleCtrlHandler(on_exit, True)

server = MyServer(('localhost', 3000), 'MYTOKENHERE', MyRequestHandler)
os.system('cls')
print(Fore.GREEN + "Program started. Don't close. Keep open" + Fore.WHITE)
print("steamcommunity.com/id/fortnyce  github.com/zepedrotrigo")
try:
    server.serve_forever()
except (KeyboardInterrupt, SystemExit):
    recording = vars["recording"]

    if recording:
        keyboard.press_and_release(vars["stop_hotkey"])
    pass

server.server_close()
print(time.asctime(), '-',Fore.GREEN + 'Program finished' + Fore.WHITE)