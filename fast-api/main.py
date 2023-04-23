import traceback, json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Set up CORS middleware
origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.post("/v1/highlights")
async def return_highlights(request: Request):
    already_in_a_clip = set()  # set of indexes that are already in a clip and therefore must be ignored
    clips = []  # dictionary of clips {"name": name, "type": type, "round": round, "duration": duration, "start": start, "end": end}

    try:
        # Process the request body
        request_body = await request.json()
        game_data = request_body["game_data"]
        user_preferences = request_body["user_preferences"]
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
                        clip = {"name": f"round{round_number}-{combination_size}k", "type": combination_size+"k", "round": round_number, "duration": (timestamps[first_n]-timestamps[last_n])//1000, "start": timestamps[first_n], "end": timestamps[last_n]}
                        clips.append(clip)

                        # add all the indexes in the combination to the already_in_a_clip set
                        already_in_a_clip.update(combination)

            # Save every frag as a clip
            if user_preferences["save_single_kills"]:
                for i in range(len(timestamps)):
                    if i not in already_in_a_clip and timestamps[i] != 0:
                        clip = {"name": f"round{round_number}-1k", "type": "1k", "round": round_number, "duration": 0, "start": timestamps[i], "end": timestamps[i]}
                        clips.append(clip)

        response = JSONResponse(content=sorted(clips, key=lambda x: x["start"]))
    except:
        traceback.print_exc()
        response = JSONResponse(status_code=500, content={"error": "Error processing request"})

    return response