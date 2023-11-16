from flask import Flask,session,request, render_template, jsonify,redirect,url_for
from flask_session import Session
import os
import moviepy.editor as mp
from speechtotext import transcribenow
import subprocess

from flask import current_app
# from moviepy.editor import AudioFileClip
from moviepy.editor import VideoFileClip
app = Flask(__name__, template_folder='templates', static_folder='static')

app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = '12qw'
Session(app)

# def convert_to_mp4(input_file, output_file):
#     clip = VideoFileClip(input_file)
#     clip.write_videofile(output_file, codec='libx264')
#     clip.close()

def convert_to_mp4(input_file, output_file):
    # Use ffmpeg to convert input_file to output_file
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',  # Video codec
        '-preset', 'ultrafast',
        '-threads', '4',  # Adjust the number of threads based on my cpu
        '-crf', '23',       # Constant Rate Factor (0 to 51, lower is better quality)
        '-c:a', 'aac',      # Audio codec
        '-strict', 'experimental',  # Required for certain audio codecs
        output_file
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Conversion successful: {input_file} -> {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")

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

            # Save the file to the "upload" folder in the "static" folder of the project
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            print(f"Uploaded file: {filename}, Extension: {os.path.splitext(filename)[1]}")

            # Check if the uploaded file is in MTS format
            if filename.lower().endswith('.mts'):
                # Convert MTS to MP4
                mp4_filename = os.path.splitext(filename)[0] + '.mp4'
                mp4_file_path = os.path.join(upload_dir, mp4_filename)
                convert_to_mp4(file_path, mp4_file_path)

        video_files = [f for f in os.listdir('static/upload') if f.endswith('.mp4')]
        return render_template('index.html', video_files=video_files)

    else:
        # Get a list of all the video files in the "upload" folder
        video_files = [f for f in os.listdir('static/upload') if f.endswith('.mp4') or f.endswith('.mts')]
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
        clip.close()

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

        print(vidname)
        result_string = vidname[len("content"):]
        result_string = (int(result_string)-1)


        for i in vid_times: #loop on single video timings
            wstart = i['start_time']
            wend = i['end_time']
            video = session.get('video_path')[result_string]
            print('video path-->', video)
            videofile = mp.VideoFileClip(video)
            #with mp.VideoFileClip(video) as videofile




            extracted_clip = videofile.subclip(wstart,wend)
            extractedclips.append(extracted_clip)
            #videofile.close()

        combined_clip = mp.concatenate_videoclips(extractedclips)
        output_file_path = os.path.join('static', 'upload', 'combined_video.mp4')
        combined_clip.write_videofile(output_file_path, codec="libx264")

        c += 1

    return redirect(url_for('combined_video'))

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

        #return jsonify({'status': 'success', 'message': 'Video cropped successfully!', 'filename': cropped_filename})
        return redirect(url_for('combined_video'))


    else:
        video_filenames = request.form.getlist('video_filenames[]')

        video_files = [f for f in os.listdir('static/upload') if f.endswith('.mp4')]
        print("video_files");
        #return render_template('timings.html', video_filenames=video_files)
        return redirect(url_for('combined_video'))


@app.route('/delete_videos', methods=['GET'])
def delete_videos():
    video_dir = os.path.join('static', 'upload')



    # Delete all video files in the directory
    for filename in os.listdir(video_dir):
        if filename.endswith('.mp4') or filename.endswith('.mts'):
            file_path = os.path.join(video_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)

    # Redirect to the homepage to reload the page
    return redirect(url_for('upload_file'))

@app.route('/combined_video', methods=['GET', 'POST'])
def combined_video():
    # Get the path of the combined video
    combined_video_path = os.path.join('static', 'upload', 'combined_video.mp4')

    return render_template('combined_video.html', combined_video_path=combined_video_path)



if __name__ == '__main__':
    app.run(debug=True)