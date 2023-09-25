import whisper
import torch
#print(torch.cuda.is_available())
def transcribenow(file_name):
    model = whisper.load_model("medium")
    result = model.transcribe(file_name,word_timestamps=True)

    # print(result["text"])
    #segmentation=result['segments']
    #print(segmentation)
    # values=[]
    # for index, dict in enumerate(result['segments']):
    #     # print(index,'-'*5,'>',dict)
    #     for val in dict['words']:
    #         #print(val.values())
    #         values.append(list(val.values()))
    script = []
    for index, dict in enumerate(result['segments']):
        # print(index,' '*5,dict)
        for val in dict['words']:
            # if val=='words':

            print(val)
            script.append(val)
            # for word in val:
            #     print(val['word'])


    # words=[]
    # start_time=[]
    # end_time=[]
    # for i in values:
    #     words.append(i[0])
    #     start_time.append(i[1])
    #     end_time.append(i[2])
    #
    # script=''.join(words)

    return script
# print(start_time)
# print(end_time)

# transcribenow('chris.wav')
