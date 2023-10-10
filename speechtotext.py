import json

import whisper
import torch

def transcribenow(file_name):
    model = whisper.load_model("base")
    result = model.transcribe(file_name,word_timestamps=True)

    segmentation=result['segments']
    script=[]
    for index, dict in enumerate(result['segments']):
        for val in dict['words']:
            script.append(val)




    return (script)


