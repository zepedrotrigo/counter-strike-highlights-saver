import json

def detect_highlights(game_data, user_preferences):
    already_in_a_clip = set()  # set of indexes that are already in a clip and therefore must be ignored
    clips = []  # dictionary of clips {"name": name, "type": type, "round": round, "duration": duration, "start": start, "end": end}

    max_times = user_preferences["max_times"]

    for round_number,timestamps in game_data.items():
        for last_n in reversed(range(len(timestamps))):
            if last_n in already_in_a_clip:
                continue

            for first_n in range(last_n):
                if first_n in already_in_a_clip:
                    continue

                # Generate a list of indexes from first_n to last_n
                combination = list(range(first_n, last_n + 1))
                combination_size = len(combination) - 1

                # Check if the time elapsed between first_n and last_n is less than the maximum time defined by the user
                if (timestamps[last_n] - timestamps[first_n] < max_times[combination_size] and timestamps[last_n] and last_n):  
                    
                    # Create a new clip with start and end times, counter, and a name based on the number of kills
                    clip = {"name": f"round{round_number}-{combination_size}k", "type": combination_size+"k", "round": {round_number}, "duration": (timestamps[first_n]-timestamps[last_n])//1000, "start": timestamps[first_n], "end": timestamps[last_n]}
                    clips.append(clip)

                    # add all the indexes in the combination to the already_in_a_clip set
                    already_in_a_clip.update(combination)

        # Save every frag as a clip
        if user_preferences["save_single_kills"]:
            for i in range(len(timestamps)):
                if i not in already_in_a_clip and timestamps[i] != 0:
                    clip = {"name": f"round{round_number}-1k", "type": "1k", "round": {round_number}, "duration": 0, "start": timestamps[i], "end": timestamps[i]}
                    clips.append(clip)

    return sorted(clips, key=lambda x: x["start"])


game_data = {
    "2": [ 1682213250605, 1682213277117, 1682213277739 ],
    "5": [ 1682213477830 ],
    "7": [ 1682213651248 ],
    "9": [ 1682213782471, 1682213795556 ],
    "12": [ 1682213965416 ],
    "16": [ 1682214309272 ],
    "18": [ 1682214442309 ],
    "19": [ 1682214585420, 1682214604420, 1682214637518 ],
    "24": [ 1682215004040, 1682215014177 ],
    "25": [ 1682215099260 ],
    "26": [ 1682215181574, 1682215198006 ],
    "27": [ 1682215271874 ],
    "28": [ 1682215317832 ],
    "29": [ 1682215427394 ]
  }

user_preferences = {"save_single_kills": True, "max_times": [10, 15, 20, 30]}
print(detect_highlights(game_data, user_preferences))