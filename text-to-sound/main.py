import os
import functions_framework
from pydub import AudioSegment
import re
import base64

@functions_framework.http
def text_to_sound(request):
    AudioSegment.converter = "ffmpeg"
    request_body = request.json
    sound = create_sound(request_body["notes"], request_body["bpm"])
    if sound is not None:
        sound.export("/tmp/sound.wav", format="wav", parameters=["-ac", "2", "-ar", "6000"])
        if os.path.isfile("/tmp/sound.wav"):
            return {"sound": str(base64.b64encode(open("/tmp/sound.wav", "rb").read()))}, 200
        else:
            return "", 500
    else:
        return "", 500


def create_sound(notes, bpm):
    extension = ".wav"
    samples_path = "samples/"

    time_quarter = (60.0 / bpm) + 0.2
    time_half = time_quarter * 2
    time_eight = time_quarter / 2
    time_sixteenth = time_eight / 4
    time_whole = time_quarter * 4

    if os.path.isfile(samples_path + "rest" + extension):
        prev_sound = AudioSegment.from_wav(samples_path + "rest" + extension)[0:0]
        curr_sound = AudioSegment.from_wav(samples_path + "rest" + extension)[0:0]
        for note in notes:
            splitted = re.split('-|_', note)
            if splitted[0] == "note" or splitted[0] == "rest":
                if splitted[0] == 'note':
                    if os.path.isfile(samples_path + splitted[1] + extension):
                        curr_sound = AudioSegment.from_wav(samples_path + splitted[1] + extension)
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
                    else:
                        curr_sound = None
                elif splitted[0] == 'rest':
                    if os.path.isfile(samples_path + splitted[0] + extension):
                        curr_sound = AudioSegment.from_wav(samples_path + splitted[0] + extension)
                        if splitted[1] == 'half':
                            curr_sound = curr_sound[0:time_half * 1000]
                        elif splitted[1] == 'quarter':
                            curr_sound = curr_sound[0:time_quarter * 1000]
                        elif splitted[1] == "eight":
                            curr_sound = curr_sound[0:time_eight * 1500]
                        else:
                            curr_sound = curr_sound[0:time_sixteenth * 1500]
                    else:
                        curr_sound = None
                if curr_sound is not None:
                    prev_sound = prev_sound + curr_sound
        return prev_sound
    else:
        return None
