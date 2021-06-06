import pickle, keyboard, os, webbrowser
import tkinter as tk
from tkinter import *
from tkinter import filedialog, ttk, messagebox

vars = {
    "steamid":"",
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
   "default_delay_after":3,
   "default_delay_before":5,
   "default_input_2k_time":12,
   "default_input_3k_time":15,
   "default_input_4k_time":20,
   "default_input_5k_time":30,
}

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

class CollapsiblePane(ttk.Frame): 
    """ 
     -----USAGE----- 
    collapsiblePane = CollapsiblePane(parent,  
                          expanded_text =[string], 
                          collapsed_text =[string]) 
  
    collapsiblePane.pack() 
    button = Button(collapsiblePane.frame).pack() 
    """
  
    def __init__(self, parent, expanded_text ="Collapse <<", 
                               collapsed_text ="Expand >>"): 
  
        ttk.Frame.__init__(self, parent) 
  
        # These are the class variable 
        # see a underscore in expanded_text and _collapsed_text 
        # this means these are private to class 
        self.parent = parent 
        self._expanded_text = expanded_text 
        self._collapsed_text = collapsed_text 
  
        # Here weight implies that it can grow it's 
        # size if extra space is available 
        # default weight is 0 
        self.columnconfigure(1, weight = 1) 
  
        # Tkinter variable storing integer value 
        self._variable = tk.IntVar() 
  
        # Checkbutton is created but will behave as Button 
        # cause in style, Button is passed 
        # main reason to do this is Button do not support 
        # variable option but checkbutton do
        self._button = ttk.Checkbutton(self, variable = self._variable, 
                            command = self._activate, style ="TButton") 
        self._button.grid(row = 0, column = 0) 
  
        # This wil create a seperator 
        # A separator is a line, we can also set thickness 
        self._separator = ttk.Separator(self, orient ="horizontal") 
        self._separator.grid(row = 0, column = 1, sticky ="we") 
  
        self.frame = ttk.Frame(self) 
  
        # This will call activate function of class 
        self._activate() 
  
    def _activate(self): 
        if not self._variable.get(): 
  
            # As soon as button is pressed it removes this widget 
            # but is not destroyed means can be displayed again 
            self.frame.grid_forget() 
  
            # This will change the text of the checkbutton 
            self._button.configure(text = self._collapsed_text) 
  
        elif self._variable.get(): 
            # increasing the frame area so new widgets 
            # could reside in this container 
            self.frame.grid(row = 1, column = 0, columnspan = 2) 
            self._button.configure(text = self._expanded_text) 
  
    def toggle(self): 
        """Switches the label frame to the opposite state."""
        self._variable.set(not self._variable.get()) 
        self._activate()

def guardar():
    global vars

    vars["start_hotkey"] = ent1.get()
    vars["stop_hotkey"] = ent2.get()
    vars["recordings_path"] = ent3.get()
    vars["steamid"] = ent15.get()

    input_is_valid = True

    if vars["recordings_path"]=="":
        error_message = "You need to choose NVIDIA Recordings folder!"
        input_is_valid = False

    try:
        vars["input_5k_time"] = float(ent7.get())
        vars["input_4k_time"] = float(ent6.get())
        vars["input_3k_time"] = float(ent5.get())
        vars["input_2k_time"] = float(ent4.get())
        vars["delay_before"] = float(ent8.get())
        vars["delay_after"] = float(ent9.get())
        vars["create_movie"] = cb1_value.get()
        vars["save_every_frag"] = cb4_value.get()
    except:
        error_message = "Advanced options are empty or not numbers!"
        input_is_valid = False

    try:
        vars["start_hotkey"]= vars["start_hotkey"].replace(" ", "").lower()
        vars["stop_hotkey"] = vars["stop_hotkey"].replace(" ", "").lower()
    except:
        error_message = "Hotkey is invalid! (example Alt+S)"
        input_is_valid = False
    
    try:
        #Outras vars de musica
        vars["spec_music_path"] = ent13.get()
        vars["spec_music_volume"] = float(ent14.get())
        vars["endround_music_volume"] = float(ent12.get())
        vars["endround_music_path"] = ent11.get()
        vars["spec_music"] = cb3_value.get()
        vars["endround_music"] = cb2_value.get()
        if vars["spec_music"]:
            if vars["spec_music_path"] == "":
                error_message = "Spectating music path is empty!"
                input_is_valid = False
        if vars["endround_music"]:
            if vars["endround_music_path"] == "":
                error_message = "End of round music path is empty!"
                input_is_valid = False
    except:
        error_message = "Music volumes are empty or not numbers!"
        input_is_valid = False

    # Guardar user configuration com o pickle
    if input_is_valid:
        path = os.path.dirname(os.path.abspath(__file__)) + "_user_config.pkl"
        with open(path, 'wb') as f:
            pickle.dump(vars["start_hotkey"], f, -1)
            pickle.dump(vars["stop_hotkey"], f, -1)
            pickle.dump(vars["recordings_path"], f, -1)
            pickle.dump(vars["input_5k_time"], f, -1)
            pickle.dump(vars["input_4k_time"], f, -1)
            pickle.dump(vars["input_3k_time"], f, -1)
            pickle.dump(vars["input_2k_time"], f, -1)
            pickle.dump(vars["delay_before"], f, -1)
            pickle.dump(vars["delay_after"], f, -1)
            pickle.dump(vars["create_movie"], f, -1)
            pickle.dump(vars["spec_music"], f, -1)
            pickle.dump(vars["endround_music"], f, -1)
            pickle.dump(vars["spec_music_path"], f, -1)
            pickle.dump(vars["endround_music_path"], f, -1)
            pickle.dump(vars["spec_music_volume"], f, -1)
            pickle.dump(vars["endround_music_volume"], f, -1)
            pickle.dump(vars["save_every_frag"], f, -1)
            pickle.dump(vars["steamid"], f, -1)
        root.after(100, root.destroy)
    else:
        messagebox.showwarning('Warning', error_message)
        #pop_up window with errors

def reset_settings():
    global vars

    ent4.delete(0, "end")
    ent5.delete(0, "end")
    ent6.delete(0, "end")
    ent7.delete(0, "end")
    ent8.delete(0, "end")
    ent9.delete(0, "end")
    ent4.insert(END, vars["default_input_2k_time"])
    ent5.insert(END, vars["default_input_3k_time"])
    ent6.insert(END, vars["default_input_4k_time"])
    ent7.insert(END, vars["default_input_5k_time"])
    ent8.insert(END, vars["default_delay_before"])
    ent9.insert(END, vars["default_delay_after"])
    tickbox_state = cb1_value.get()
    while tickbox_state == 1:
        cb1.toggle()
        tickbox_state = cb1_value.get()
    vars["create_movie"] = False
    tickbox2_state = cb4_value.get()
    while tickbox2_state == 0:
        cb4.toggle()
        tickbox2_state = cb4_value.get()
    vars["save_every_frag"] = True


def get_recordings_path():
    global vars
    vars["recordings_path"] =filedialog.askdirectory()
    ent3.delete(0, "end")
    ent3.insert(tk.END, vars["recordings_path"]) # add this

def get_endround_music_path():
    global vars
    vars["endround_music_path"] =filedialog.askdirectory()
    ent11.delete(0, "end")
    ent11.insert(tk.END, vars["endround_music_path"])

def get_spectating_music_path():
    global vars
    vars["spec_music_path"] =filedialog.askdirectory()
    ent13.delete(0, "end")
    ent13.insert(tk.END, vars["spec_music_path"])

def on_close():
    root.destroy()
    quit()
#-----------------------Tkinter Main--------------------
root=tk.Tk() #criar uma janela
root.title("highlightsCS by Fortnyce")
root.resizable(0,0) # remove o botao de maximizar
#root.geometry("700x300")
root.protocol("WM_DELETE_WINDOW",  on_close) # if close tinker, quit() python script

#----------Notebook para ter várias tabs
notebook = ttk.Notebook(root) # o notebook serve para ter várias tabs
notebook.pack()
frame_highlights = Frame(notebook)
frame_highlights.pack(fill="both", expand=1)
frame_music = Frame(notebook)
frame_music.pack(fill="both", expand=1)
notebook.add(frame_highlights, text="Highlights")
notebook.add(frame_music, text="Music")
#---------Tab highlights
l1 = tk.Label(frame_highlights,text="IMPORTANT: Set your Instant Replay Length to atleast 3 minutes",justify=LEFT, anchor="w", font=('Arial',9,'bold')).grid(row=7,column=1,sticky = W,pady=(20,0))
l2 = tk.Label(frame_highlights,text="NVIDIA Shadowplay turns on and off automatically",justify=LEFT, anchor="w",font=('Arial',9,'bold')).grid(row=8,column=1,sticky = W)
l3 = tk.Label(frame_highlights,text="Is this tool awesome and saves you a lot of work? You can thank me here :)",justify=LEFT, anchor="w", fg="#0645AD", font=('Arial',9,'bold','underline'))
l3.grid(sticky = W, row=9, column=1)
l3.bind("<Button-1>", lambda e: webbrowser.open_new("https://steamcommunity.com/tradeoffer/new/?partner=250118937&token=s8eat9SV"))
b1 = tk.Button(frame_highlights,text="Start!",font=('bold'), command=guardar, height=1)
b1.grid(row=9,column=2)

l18 = tk.Label(frame_highlights,text = "Your SteamID64: ").grid(row=2,column=1)
ent15=tk.Entry(frame_highlights,font=40,width=5)
ent15.grid(sticky=W,row=2,column=2)
ent15.insert(END, vars["steamid"])
l5 = tk.Label(frame_highlights,text = "Start Recording hotkey: ").grid(row=3,column=1)
ent1=tk.Entry(frame_highlights,font=40,width=5)
ent1.grid(sticky=W,row=3,column=2)
ent1.insert(END, vars["start_hotkey"])
l6 = tk.Label(frame_highlights,text = "Stop Recording hotkey: ").grid(row=4,column=1)
ent2=tk.Entry(frame_highlights,font=40,width=5)
ent2.grid(sticky=W,row=4,column=2)
ent2.insert(END, vars["stop_hotkey"])

l7 = tk.Label(frame_highlights,text = "CSGO Recordings folder: ").grid(row=5,column=1)
ent3=tk.Entry(frame_highlights,font=40,width=5)
ent3.grid(sticky=W,row=5,column=2)
ent3.insert(END, vars["recordings_path"])
b2=tk.Button(frame_highlights,text="Search",command=get_recordings_path)
b2.grid(sticky=W,row=5,column=2,padx=80)

#-------------Expandable Pane
# Creating Object of Collapsible Pane Container 
cpane = CollapsiblePane(frame_highlights, 'Hide Advanced Settings', 'Show Advanced Settings') 
cpane.grid(row = 6, column = 1) 

# appear in collapsible pane container 
l8 = tk.Label(cpane.frame,text = "Maximum Double kill duration: ").grid(sticky=W,row=1,column=1)
ent4 = tk.Entry(cpane.frame,font=40,width=5)
ent4.grid(sticky=W,row=1,column=2)
ent4.insert(END, vars["input_2k_time"])
l9 = tk.Label(cpane.frame,text = "Maximum Triple kill duration: ").grid(sticky=W,row=2,column=1)
ent5=tk.Entry(cpane.frame,font=40,width=5)
ent5.grid(sticky=W,row=2,column=2)
ent5.insert(END, vars["input_3k_time"])
l10 = tk.Label(cpane.frame,text = "Maximum Quadra kill duration: ").grid(sticky=W,row=3,column=1)
ent6=tk.Entry(cpane.frame,font=40,width=5)
ent6.grid(sticky=W,row=3,column=2)
ent6.insert(END, vars["input_4k_time"])
l11 = tk.Label(cpane.frame,text = "Maximum Ace duration: ").grid(sticky=W,row=4,column=1)
ent7=tk.Entry(cpane.frame,font=40,width=5)
ent7.grid(sticky=W,row=4,column=2)
ent7.insert(END, vars["input_5k_time"])
l12 = tk.Label(cpane.frame,text = "Time delay at beginning of clip: ").grid(sticky=W,row=5,column=1)
ent8=tk.Entry(cpane.frame,font=40,width=5)
ent8.grid(sticky=W,row=5,column=2)
ent8.insert(END, vars["delay_before"])
l13 = tk.Label(cpane.frame,text = "Time delay at end of clip: ").grid(sticky=W,row=6,column=1)
ent9=tk.Entry(cpane.frame,font=40,width=5)
ent9.grid(sticky=W,row=6,column=2)
ent9.insert(END, vars["delay_after"])
cb1_value = tk.IntVar()
cb1 = Checkbutton(cpane.frame, text ="Create Movie",variable=cb1_value)
cb1.grid(sticky=W,row = 8, column = 1)
if vars["create_movie"]:
    cb1.toggle()
cb4_value = tk.IntVar()
cb4 = Checkbutton(cpane.frame, text ="Save every kill",variable=cb4_value)
cb4.grid(sticky=W,row = 9, column = 1)
if vars["save_every_frag"]:
    cb4.toggle()
b3 = tk.Button(cpane.frame,text="Reset", command=reset_settings, height=1)
b3.grid(sticky=W,row=10,column=1)


#----------------Tab Music------------------------
l14 = tk.Label(frame_music,text = "End of round music: ").grid(row=1,column=1,sticky=W)
ent11=tk.Entry(frame_music,font=40,width=5)
ent11.grid(sticky=W,row=1,column=2)
ent11.insert(END, vars["endround_music_path"])
b5=tk.Button(frame_music,text="Search",command=get_endround_music_path)
b5.grid(sticky=W,row=1,column=3)
l15 = tk.Label(frame_music,text = "Volume: ").grid(row=1,column=4,sticky=W)
ent12=tk.Entry(frame_music,font=40,width=5)
ent12.grid(sticky=W,row=1,column=5)
ent12.insert(END, vars["endround_music_volume"])
cb2_value = tk.IntVar()
cb2 = Checkbutton(frame_music,variable=cb2_value)
cb2.grid(sticky=W,row = 1, column = 6)
if vars["endround_music"]:
    cb2.toggle()

l16 = tk.Label(frame_music,text = "Spectating music: ").grid(row=2,column=1,sticky=W)
ent13=tk.Entry(frame_music,font=40,width=5)
ent13.grid(sticky=W,row=2,column=2)
ent13.insert(END, vars["spec_music_path"])
b6=tk.Button(frame_music,text="Search",command=get_spectating_music_path)
b6.grid(sticky=W,row=2,column=3)
l17 = tk.Label(frame_music,text = "Volume: ").grid(row=2,column=4,sticky=W)
ent14=tk.Entry(frame_music,font=40,width=5)
ent14.grid(sticky=W,row=2,column=5)
ent14.insert(END, vars["spec_music_volume"])
cb3_value = tk.IntVar()
cb3 = Checkbutton(frame_music,variable=cb3_value)
cb3.grid(sticky=W,row = 2, column = 6)
if vars["spec_music"]:
    cb3.toggle()
 
root.mainloop()