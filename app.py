from flask import Flask, request, render_template, jsonify
import os
import moviepy.editor as mp
import json
import whisper
import torch
import numpy as np
from speechtotext import transcribenow
app = Flask(__name__)
model = whisper.load_model("medium")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Create the "upload" directory if it does not exist
        upload_dir = 'C:/Users/HD/PycharmProjects/whisper/static/upload'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Loop through each uploaded file
        for file in request.files.getlist('file'):
            filename = file.filename
            # Save the file to the "upload" folder in the "static" folder of your project
            file.save(os.path.join(upload_dir, filename))

        return 'Files uploaded and saved successfully!'
    else:
        # Get a list of all the image and video files in the "upload" folder
        image_files = [f for f in os.listdir('static/upload') if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        video_files = [f for f in os.listdir('static/upload') if f.endswith('.mp4')]
        # Render the HTML template and pass in the list of image and video files
        return render_template('index.html', image_files=image_files, video_files=video_files)

@app.route('/generate_script', methods=['POST'])
def generate_script():
    video_filenames = request.form.getlist('video_filenames[]')
    for video_filename in video_filenames:
        video_path = os.path.join('static', 'upload', video_filename)
        clip = mp.VideoFileClip(video_path)
        #duration = clip.duration
        audio_path_mp3 = os.path.join('static', 'upload', os.path.splitext(video_filename)[0] + '.mp3')
        clip.audio.write_audiofile(audio_path_mp3)
        with open(audio_path_mp3, 'rb'):


            script = transcribenow(audio_path_mp3)


    return render_template('trans.html', script=script)

    #return jsonify(script)

@app.route('/timings', methods=['GET', 'POST'])
def timings():
    if request.method == 'POST':
        video_filename = request.form['video_filename']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        # Convert start_time and end_time to float values
        start_time = float(start_time)
        end_time = float(end_time)

        # Construct the video path and audio path
        video_path = os.path.join('static', 'upload', video_filename)
        audio_path = os.path.join('static', 'upload', os.path.splitext(video_filename)[0] + '.wav')

        # Load the video clip using moviepy
        clip = mp.VideoFileClip(video_path)

        # Set the start and end times for cropping
        clip = clip.subclip(start_time, end_time)

        # Save the cropped video clip to a new file
        cropped_filename = os.path.splitext(video_filename)[0] + '_cropped.mp4'
        cropped_path = os.path.join('static', 'upload', cropped_filename)
        clip.write_videofile(cropped_path)

        return jsonify({'status': 'success', 'message': 'Video cropped successfully!', 'filename': cropped_filename})

    else:
        video_filenames = request.form.getlist('video_filenames[]')

        video_files = [f for f in os.listdir('static/upload') if f.endswith('.mp4')]
        print("video_files");
        return render_template('timings.html', video_filenames=video_files)



if __name__ == '__main__':
    app.run(debug=True)
