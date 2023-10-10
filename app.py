from flask import Flask,session,request, render_template, jsonify
from flask import Flask, session
from flask_session import Session
from flask import current_app
from moviepy.editor import AudioFileClip
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = '12qw'
Session(app)

import os
import moviepy.editor as mp
import json
import whisper
import torch
import numpy as np
from speechtotext import transcribenow
#app = Flask(__name__)
model = whisper.load_model("base")
mp3filepath=None
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Create the "upload" directory if it does not exist
        upload_dir = os.path.join('static', 'upload')
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
    combined_script = []
    video_paths = []
    for index,video_filename in enumerate(video_filenames):
        video_path = os.path.join('static', 'upload', video_filename)
        video_paths.append(video_path)

        clip = mp.VideoFileClip(video_path)
        #duration = clip.duration
        audio_path_mp3 = os.path.join('static', 'upload', os.path.splitext(video_filename)[0] + '.mp3')
        clip.audio.write_audiofile(audio_path_mp3)
        #session['audio_path_mp3'] = audio_path_mp3

        with open(audio_path_mp3, 'rb'):

            print('video : ',index+1)
            script = transcribenow(audio_path_mp3)
            # script=json.loads(script)
            combined_script.append(script)
            # combined_script=json.dumps(combined_script)
            #print('video--------------------------------------------------------------------------------------------')
    print(combined_script)

    session['video_path'] = video_paths
    print(session['video_path'])
    return render_template('trans.html', script=combined_script)

    #return jsonify(script)

@app.route('/clips', methods=['POST'])
def extract_clips():
    #global mp3filepath

    if request.method == 'POST':
        multimedia = request.json['clip_timmings']

    extractedclips=[]
    #return multimedia;
    c = 0
    for vidname, vid_times in multimedia.items(): #loop on videos
        #return vid_times

        for i in vid_times: #loop on single video timings
            #return vid
            wstart=i['start_time']
            wend=i['end_time']
            #audio = session.get('audio_path_mp3')
            video=session.get('video_path')[c]
            print('video path-->', video)
            videofile=mp.VideoFileClip(video)
            #audiofile=AudioFileClip(audio)

            print('start-->',wstart,'end-->',wend)
            #print(audiofile)
            print(videofile)


            extracted_clip = videofile.subclip(wstart,wend)
            extractedclips.append(extracted_clip)
        combined_clip = mp.concatenate_videoclips(extractedclips)
        output_file_path = os.path.join('static', 'upload', 'combined_video.mp4')
        #combined_clip.write_audiofile(output_file_path, codec="mp4")
        combined_clip.write_videofile(output_file_path, codec="libx264")

        c += 1
        #save output path in list


    #return jsonify({'status': 'success', 'message': 'Clips extracted and combined successfully!',
                    #'filename': 'combined_audio.mp3'})

    return multimedia

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