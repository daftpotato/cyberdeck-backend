import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import signal
import sys
import katosc
import os
import requests  # <- Needed for Pulsoid
from threading import Thread  # To fetch HR async

os.system('cls' if os.name == 'nt' else 'clear')

# Your Pulsoid token
PULSOID_TOKEN = "YOUR_PULSOID_TOKEN"

# Global heart rate variable
heart_rate = "--"

def fetch_heart_rate():
    global heart_rate
    while True:
        try:
            response = requests.get(
                "https://dev.pulsoid.net/api/v1/data/heart_rate",
                headers={"Authorization": f"Bearer {PULSOID_TOKEN}"}
            )
            if response.status_code == 200:
                data = response.json()
                heart_rate = data.get("data", {}).get("heart_rate", "--")
            else:
                heart_rate = "??"
        except Exception as e:
            heart_rate = "!!"
        time.sleep(2)

# Start HR fetcher in background
Thread(target=fetch_heart_rate, daemon=True).start()

def clamp_string(s, min_length, max_length):
    if len(s) < min_length:
        return s.ljust(min_length)
    elif len(s) > max_length:
        return s[:max_length]
    else:
        return s

def scrolling_text(string: str) -> list:
    new_list = []
    string = string.upper() + "   "
    for i in range(0, len(string)):
        if i != 0:
            string = string[1:] + string[:1]
        new_list.append(string)
    return new_list

kat = katosc.KatOsc()
kat.osc_enable_chatbox = False

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="0fd57134b7804b52b978d4d796a8858a",
    client_secret="dd829febe6d84fc4be2cdedee198c86b",
    redirect_uri='http://localhost:8881/callback',
    scope='user-read-playback-state,user-read-currently-playing'))

bar = ["[#-------]", "[-#------]", "[--#-----]", "[---#----]", "[----#---]", "[-----#--]", "[------#-]", "[-------#]"]
I = 0
old_track_name = ""
cur_track_name = ""
ScrTxt = []
J = 0

while True:
    current_track = sp.current_playback()
    if current_track is None:
        print("No track is currently playing.")
        os.system('cls' if os.name == 'nt' else 'clear')
    else:
        track_name = current_track['item']['name']
        artist_name = clamp_string(current_track['item']['artists'][0]['name'], 0, 30)
        if len(track_name) > 30:
            if track_name != old_track_name:
                old_track_name = track_name
                ScrTxt = scrolling_text(track_name)
                I = 0
            else:
                if I < (len(ScrTxt) - 1):
                    I = max(0, min(int((I + 5)), len(ScrTxt) - 1))
                else:
                    if I > (len(ScrTxt) - 2):
                        I = 1
            cur_track_name = clamp_string(ScrTxt[I], 0, 30)
        else:
            cur_track_name = clamp_string(track_name, 0, 30)

        current_tracklength = current_track['item']['duration_ms']
        current_trackpos = current_track['progress_ms']
        barpos = max(0, min(int((current_trackpos / current_tracklength) * len(bar)), len(bar) - 1))
        playback_icons = ["", "", "", ""]
        playback_icons[0] = {True: "/<", False: "|<"}.get(current_track['actions'].get('skipping_prev', False), False)
        playback_icons[1] = {True: "> ", False: "||"}.get(current_track['is_playing'], False)
        playback_icons[3] = {True: ">/", False: ">|"}.get(current_track['actions'].get('skipping_next', False), False)

        message = f"Now Playing:  <3 {heart_rate} bpm\n{cur_track_name}\nby {artist_name}\n{bar[int(barpos)]} {playback_icons[0]} {playback_icons[1]} {playback_icons[3]}"
        kat.show()
        kat.set_text(message)

        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"ThatEvanGokus Spotify Cyberdeck \n╔════════════════════════════╗\n {message}\n╚════════════════════════════╝\n powered by KillFrenzy Avatar Text (KAT)\nhttps://github.com/killfrenzy96/KillFrenzyAvatarText\nhttps://github.com/killfrenzy96/KatOscApp")
    time.sleep(2)
