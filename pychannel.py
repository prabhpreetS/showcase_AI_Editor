import os
from pydub import AudioSegment


def audio_channel_extraction(file_path, output_path):
    count = 0
    video = AudioSegment.from_file(file_path)
    print(f"Stereo number channels:{video.channels}")
    channels = video.split_to_mono()
    for channel in channels:

        # print(f"Split number channels: {channels[0]}, {channels[1]}")
        print('channel:::', channel)
        # audio1 = channels[0]
        # audio2 = channels[1]
        count += 1
        audio = channel
        basename = os.path.splitext(os.path.basename(file_path))[0]
        audio.export(out_f=f"{output_path}{basename}_channel_{count}.mp3", format="mp3")
