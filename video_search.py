import os
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from datetime import datetime

MAX_UPLOAD_SIZE_MB = 100
MAX_UPLOAD_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024
UPLOAD_FOLDER = './videos'
ALLOWED_EXTENSIONS = set(['mp4', 'flv', 'avi', 'wmv', 'mov'])  #what extensions should we allow?


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE_MB * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def main_search():
    return render_template('main_search.html')


def process_video(file):
    #do we want to store the video? for now processing the video will just be storing the video in a folder on this server

    #original_filename = secure_filename(file.filename) #original filename, don't know if we want to do anything with original filename
    original_extension = '.' + file.filename.rsplit('.', 1)[1].lower()
    filename = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3] #just make the filename the current time
    filename += original_extension
    save_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # app.logger.debug(save_filepath)
    file.save(save_filepath)

    #need to run the ML model on the video and return the results

    #also need to send the video to the backend DB and/or the tier 2 ML server

    return 'processed' #change return type or get rid of it as necessary

#returns whether the uploaded video is valid (it has a valid extension and is not over the size limit)
def file_valid():
    filename = request.files['video'].filename
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and \
        request.content_length is not None and request.content_length <= MAX_UPLOAD_SIZE


@app.route('/search', methods=['GET', 'POST'])
def search():
    #redirect to main page if there wasn't a valid POST request
    if request.method != 'POST' or \
        'video' not in request.files or \
        request.files['video'] == None or \
        request.files['video'].filename == '':
        return redirect(url_for('main_search'))

    #otherwise the video file was not the right format or too big
    elif(not file_valid()):
        flash('Invalid video. Please a select a video (.mp4, .flv, .avi, .wmv, .mov) at most ' + str(MAX_UPLOAD_SIZE_MB) + 'MB')
        return redirect(url_for('main_search'))

    #if the uploaded file is valid then process the video
    else:
        file = request.files['video']
        filename = file.filename
        process_video(file)
        return render_template('search_results.html', filename = filename)


app.secret_key = '\x1d%oW\x81w\xefH\xbf\xb6\xb0\xd3\xd6_?\x8f\x8b,\xd7\xaa;\xbc/\xd4' #this line is so we can use sessions, which is neccessary for flashes to work

# start the server
if __name__ == '__main__':
    app.run()
