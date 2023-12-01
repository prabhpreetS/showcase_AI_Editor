from flask import Flask,session,request, render_template, jsonify,redirect,url_for
from flask_session import Session
import os
import logging
import moviepy.editor as mp
from speechtotext import transcribenow
import subprocess
logging.basicConfig(level=logging.INFO)
from pychannel import audio_channel_extraction
from sd import transcribenow1
from new import transcribenow2
app = Flask(__name__, template_folder='templates', static_folder='static')

app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = '12qw'
Session(app)



def convert_to_mp4(input_file, output_file):

    """This function converts the mts file to mp4 for better processing and functioning"""
    # Use ffmpeg to convert input_file to output_file
    cmd = [
        'ffmpeg',
        '-y',
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

        #input:- mts file
        #output:- mp4 file


mp3filepath = None


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global response
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
        audio_files = [f for f in os.listdir('static/upload/separate_audio') if f.endswith('.mp3')]

        for video_file in video_files:
            output_directory = os.path.join(upload_dir, "separate_audio/")
            os.makedirs(output_directory, exist_ok=True)
            video_loc = os.path.join(upload_dir, video_file)
            try:
                audio_channel_extraction(video_loc,output_directory)
                response={'status': 'conversion success', 'message': 'audio is available'}
            except Exception as e:
                print(f'error during conversion{e}')
                response = {'status': 'conversion failed', 'message': 'audio is not available'}

        audio_files = [f for f in os.listdir('static/upload/separate_audio') if f.endswith('.mp3')]

        app.logger.info("recieved post req:")
        app.logger.info(request.form)
        app.logger.info(request.files)
        return render_template('index.html', video_files=video_files, response=response,audio_files=audio_files)

    else:
        # Get a list of all the video files in the "upload" folder
        video_files = [f for f in os.listdir('static/upload') if f.endswith('.mp4')]
        app.logger.info('recieved get req:')
        app.logger.info(request.form)
        app.logger.info(request.files)
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
        print('videopath::'+video_path)

        with mp.VideoFileClip(video_path) as clip:
            audio_path_mp3 = os.path.join('static', 'upload', os.path.splitext(video_filename)[0] + '.mp3')

            try:
                clip.audio.write_audiofile(audio_path_mp3)
                print(f'conversion successful: {audio_path_mp3}')
                response = {'status': 'conversion successful', 'message': 'audio written successfully'}
                app.logger.info(response)
            except Exception as e:
                print(f'error during conversion{e}')
                response = {'status': 'conversion failed', 'message': 'audio is not available'}
            finally:

                clip.close()

        with open(audio_path_mp3, 'rb'):

            print('video : ', index+1)
            script = transcribenow1(audio_path_mp3)
            combined_script.append(script)
    print('combined_script::',combined_script)
    #app.logger.info('this is video paths: ', len(video_paths))
    app.logger.info(combined_script)
    session['video_path'] = video_paths
    app.logger.info(session['video_path'])
    return render_template('trans.html', script=combined_script,response=response)

@app.route('/delete_video_single', methods=['POST'])
def delete_video_single():
    filename = request.form.get('filename')

    # Assuming the videos are stored in the 'upload' folder
    video_path = os.path.join('static', 'upload', filename)

    # Remove the video file
    if os.path.exists(video_path):
        print(video_path,'before')
        os.remove(video_path)
        print(video_path, 'after')
        app.logger.info(f"video_path-{video_path}")

    #return jsonify({'message': 'File deleted successfully'})
    #return redirect(url_for('upload_file'))
    return render_template('index.html', video_path=video_path)




@app.route('/clips', methods=['POST'])
def extract_clips():

    if request.method == 'POST':
        multimedia = request.json['clip_timmings']

    extractedclips=[]
    #return multimedia;
    c = 0
    for vidname, vid_times in multimedia.items():
#        #loop on videos

        print(vidname)
        result_string = vidname[len("content"):]
        result_string = (int(result_string)-1)
        print(len(vid_times))
        if len(vid_times)>0:
            for i in vid_times:

#loop on single video timings

                wstart = i['start_time']
                wend = i['end_time']
                video = session.get('video_path')[result_string]
                print('video path-->', video)
                videofile = mp.VideoFileClip(video)
                app.logger.info(videofile)
#               #with mp.VideoFileClip(video) as videofile

                extracted_clip = videofile.subclip(wstart,wend)
                extractedclips.append(extracted_clip)
#               #videofile.close()
            print(extractedclips)
            combined_clip = mp.concatenate_videoclips(extractedclips)
            output_file_path = os.path.join('static', 'upload', 'combined_video.mp4')
            combined_clip.write_videofile(output_file_path, codec="libx264")

        c += 1
    app.logger.info(videofile)
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

#        #return jsonify({'status': 'success', 'message': 'Video cropped successfully!', 'filename': cropped_filename})
        return redirect(url_for('combined_video'))


    else:
        video_filenames = request.form.getlist('video_filenames[]')

        video_files = [f for f in os.listdir('static/upload') if f.endswith('.mp4')]
        print("video_files");
#        #return render_template('timings.html', video_filenames=video_files)
        return redirect(url_for('combined_video'))


@app.route('/delete_videos', methods=['GET'])
def delete_videos():
    video_dir = os.path.join('static', 'upload')
    audio_dir = os.path.join('static', 'upload', 'separate_audio/')


    # Delete all video files in the directory
    for filename in os.listdir(video_dir):
        if filename.endswith('.mp4') or filename.endswith('.mts'):
            file_path = os.path.join(video_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                app.logger.info(f"file_path-{file_path}")

    for filename in os.listdir(audio_dir):
        if filename.endswith('.mp3') or filename.endswith('.mts'):
            file_path = os.path.join(audio_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                app.logger.info(f"file_path-{file_path}")
    # Redirect to the homepage to reload the page
    return redirect(url_for('upload_file'))


@app.route('/combined_video', methods=['GET', 'POST'])
def combined_video():
    # Get the path of the combined video
    combined_video_path = os.path.join('static', 'upload', 'combined_video.mp4')

    return render_template('combined_video.html', combined_video_path=combined_video_path)


if __name__ == '__main__':
    app.run(debug=True)