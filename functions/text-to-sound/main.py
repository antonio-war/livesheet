import os

import functions_framework
from pydub import AudioSegment
import re


@functions_framework.http
def text_to_sound(request):
    request_body = request.json
    create_sound(request_body["id"], request_body["notes"])
    return "", 200


def create_sound(filename, notes):
    bpm = 120
    extension = ".wav"

    # *********************** Inizio Sezione Locale ***************************
    os.chdir("/Users/admin/Desktop/livesheet/resources")
    samples_path = "/samples/"
    results_path = "/results/"
    # *********************** Fine Sezione Locale ***************************

    time_quarter = (60.0 / bpm) + 0.2
    time_half = time_quarter * 2
    time_eight = time_quarter / 2
    time_sixteenth = time_eight / 4
    time_whole = time_quarter * 4

    # *********************** Inizio Sezione Locale ***************************
    if os.path.isfile(os.getcwd() + samples_path + "rest" + extension):
        prev_sound = AudioSegment.from_wav(os.getcwd() + samples_path + "rest" + extension)[0:0]
        curr_sound = AudioSegment.from_wav(os.getcwd() + samples_path + "rest" + extension)[0:0]
    else:
        return
    # *********************** Fine Sezione Locale ***************************

    for note in notes:
        splitted = re.split('-|_', note)
        if splitted[0] == "note" or splitted[0] == "rest":
            if splitted[0] == 'note':
                # *********************** Inizio Sezione Locale ***************************
                if os.path.isfile(os.getcwd() + samples_path + splitted[1] + extension):
                    curr_sound = AudioSegment.from_wav(os.getcwd() + samples_path + splitted[1] + extension)
                    # *********************** Fine Sezione Locale ***************************
                    if splitted[2] == 'whole':
                        curr_sound = curr_sound[0:time_whole * 1000]
                    elif splitted[2] == 'half':
                        curr_sound = curr_sound[0:time_half * 1000]
                    elif splitted[2] == 'half.':
                        curr_sound = curr_sound[0:(time_half + time_half / 2) * 1000]
                    elif splitted[2] == 'quarter':
                        curr_sound = curr_sound[0:time_quarter * 1000]
                    elif splitted[2] == 'quarter.':
                        curr_sound = curr_sound[0:(time_quarter + time_quarter / 2) * 1000]
                    elif splitted[2] == "eight":
                        curr_sound = curr_sound[0:time_eight * 1500]
                    elif splitted[2] == "eight.":
                        curr_sound = curr_sound[0:(time_eight + time_eight / 2) * 1500]
                    elif splitted[2] == "sixteenth":
                        curr_sound = curr_sound[0:time_sixteenth * 1500]
                    else:
                        curr_sound = curr_sound[0:(time_sixteenth + time_sixteenth / 2) * 1500]
            elif splitted[0] == 'rest':
                # *********************** Inizio Sezione Locale ***************************
                if os.path.isfile(os.getcwd() + samples_path + splitted[0] + extension):
                    curr_sound = AudioSegment.from_wav(os.getcwd() + samples_path + splitted[0] + extension)
                    # *********************** Fine Sezione Locale ***************************
                    if splitted[1] == 'half':
                        curr_sound = curr_sound[0:time_half * 1000]
                    elif splitted[1] == 'quarter':
                        curr_sound = curr_sound[0:time_quarter * 1000]
                    elif splitted[1] == "eight":
                        curr_sound = curr_sound[0:time_eight * 1500]
                    else:
                        curr_sound = curr_sound[0:time_sixteenth * 1500]
            prev_sound = prev_sound + curr_sound
    prev_sound.export(os.getcwd() + results_path + filename + extension, format="wav")