import json

import whisper
# import torch
# print('transcribenow',torch.cuda.is_available())
# print('transcribenow',torch.cuda.get_device_name(0))

def transcribenow(file_name):
    model = whisper.load_model("base")
    try:
        result = model.transcribe(file_name,word_timestamps=True)

        segmentation=result['segments']
        script = []
        transcript = []
        for index, dict in enumerate(result['segments']):
            for val in dict['words']:
                script.append(val)
                word = val['word']
                transcript.append(word)
        transcript = ' '.join(transcript)

        return script, transcript

    except Exception as e:
        print("no audio to whisper: ", e)


