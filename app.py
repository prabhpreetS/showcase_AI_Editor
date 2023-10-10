from flask import Flask,session,request, render_template, jsonify
from flask import Flask, session
from flask_session import Session
import os
import moviepy.editor as mp
from speechtotext import transcribenow
from flask import current_app
from moviepy.editor import AudioFileClip
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = '12qw'
Session(app)



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
            # Save the file to the "upload" folder in the "static" folder of project
            file.save(os.path.join(upload_dir, filename))

        return 'Files uploaded and saved successfully!'
    else:
        # Get a list of all the video files in the "upload" folder
        video_files = [f for f in os.listdir('static/upload') if f.endswith('.mp4')]
        # Render the HTML template and pass in the list of image and video files
        return render_template('index.html', video_files=video_files)

@app.route('/generate_script', methods=['POST'])
def generate_script():
    video_filenames = request.form.getlist('video_filenames[]')
    combined_script = []
    video_paths = []
    for index,video_filename in enumerate(video_filenames):
        video_path = os.path.join('static', 'upload', video_filename)
        video_paths.append(video_path)

        clip = mp.VideoFileClip(video_path)
        audio_path_mp3 = os.path.join('static', 'upload', os.path.splitext(video_filename)[0] + '.mp3')
        clip.audio.write_audiofile(audio_path_mp3)

        with open(audio_path_mp3, 'rb'):

            print('video : ', index+1)
            script = transcribenow(audio_path_mp3)
            combined_script.append(script)
    print(combined_script)

    session['video_path'] = video_paths
    print(session['video_path'])
    return render_template('trans.html', script=combined_script)


@app.route('/clips', methods=['POST'])
def extract_clips():

    if request.method == 'POST':
        multimedia = request.json['clip_timmings']

    extractedclips=[]
    #return multimedia;
    c = 0
    for vidname, vid_times in multimedia.items(): #loop on videos

        for i in vid_times: #loop on single video timings
            wstart = i['start_time']
            wend = i['end_time']
            video = session.get('video_path')[c]
            print('video path-->', video)
            videofile = mp.VideoFileClip(video)


            print('start-->',wstart,'end-->',wend)

            print(videofile)


            extracted_clip = videofile.subclip(wstart,wend)
            extractedclips.append(extracted_clip)
        combined_clip = mp.concatenate_videoclips(extractedclips)
        output_file_path = os.path.join('static', 'upload', 'combined_video.mp4')
        combined_clip.write_videofile(output_file_path, codec="libx264")

        c += 1



    return multimedia



if __name__ == '__main__':
    app.run(debug=True)