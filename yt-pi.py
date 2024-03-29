from flask import Flask, abort, render_template, redirect, url_for, request, session, send_from_directory, flash, jsonify
from markupsafe import escape
import random
import os
import database
import json
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['DataFolder'] = "/".join(
    os.path.abspath(__file__).split("/")[:-1]) + "/" + "data"

app.secret_key = os.urandom(24)
youtubedl = False

@app.template_filter("clean_video_name")
def clean_video_name(video_name: str) -> str:
    return video_name.replace("_", " ").replace("  ", " ").replace("  ", " ")


def getConfig():
    return database.Database("config.json")


def getVideoFolder():
    return os.path.expanduser(getConfig().get("videofolder"))


def getVideos():
    videofolder = getVideoFolder()
    return sorted(os.listdir(videofolder), key=lambda x: -os.path.getmtime(videofolder + "/" + x))


def programExists(name):
    """Check whether `name` is on PATH and marked as executable."""

    from shutil import which

    return which(name) is not None


def showError(error, back, title="Error!", extra=None, errorcode=500):
    extra = extra if extra else ""

    return render_template("error.html", e=error, url=back, error=title, extra=extra), errorcode


def CoSo(version):
    version = str(version)

    return render_template("comingSoon.html", ver=version)


@app.route("/", methods=['GET'])
def homePage():
    try:
        popup = request.args['popup']

    except Exception as e:
        popup = None

    return render_template('homePage.html', version=getConfig().get("version"), popup=popup, videos = getVideos()[:18])


@app.route('/data/<path:filename>')
def returnData(filename):
    return send_from_directory(app.config['DataFolder'],
                               filename)


@app.route('/videos/')
def videosList():
    return render_template('videos.html', videos = getVideos())


def getDescription(video_name: str) -> str:
    for root, dirs, files in os.walk(getVideoFolder() + '/' + video_name):
        for file in files:
            if file.endswith('.description'):
                with open(root + '/' + file, 'r') as de:
                    return de.read().replace("\n", "\n<br>")

    return ''


@app.route('/videos/<video>')
def videoPage(video):
    for root, dirs, files in os.walk(getVideoFolder() + '/' + video):
        for file in files:
            if file.endswith('.mp4') or file.endswith('.webm'):
                # perhaps switch to urllib.parse.quote() ?
                return render_template("video.html", path='/vidfile/' + video.replace("'", "%27") + "/" + file, description=getDescription(video), title=video, videos = getVideos()[:18])

        break

    return render_template("unfinished.html", title=video)


@app.route('/videos/<video>/thumb')
def videoPageThumb(video):
    for root, dirs, files in os.walk(getVideoFolder() + '/' + video):
        for file in files:
            if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.webp') or file.endswith('.jpeg') or file.endswith(".svg"):
                return send_from_directory(getVideoFolder() + "/" + video + "/",
                                           file)

        break

    return send_from_directory("data", "eye.png")


@app.route("/vidfile/<folder>/<file>")
def videourlpagething(folder, file):
    return send_from_directory(getVideoFolder() + "/" + folder + "/",
                               file)


@app.route('/credits/')
def creditsPage():
    return render_template('credits.html')


@app.route('/add/')
def addVideoPage():
    return render_template('addVideo.html')


@app.route('/add/yt/', methods=['GET', 'POST'])
def downloadYtVideo():
    if not youtubedl:
        return showError('yt-dlp is not installed or is not on your PATH.', request.url)

    if request.method == 'POST':
        url = request.form['url']

        if url != '':
            os.system("python3 -m yt_dlp -f bestvideo+bestaudio -o \"" + getVideoFolder() +
                      "/%(title)s/%(title)s.%(ext)s\"" + " --write-thumbnail --write-description --all-subs --embed-subs " + url)

            return redirect('/')

        else:
            return render_template('download.html', error='You must specify a URL!')

    else:
        return render_template("download.html")


@app.route('/add/mp4/', methods=['GET', 'POST'])
def downloadYtMP4():
    if not youtubedl:
        return showError('yt-dlp is not installed or is not on your PATH.', request.url)

    if request.method == 'POST':
        url = request.form['url']

        if url != '':
            if os.path.exists("download.mp4"):
                os.rm("download.mp4")

            os.system("python3 -m yt_dlp -f best -o " +
                      "download0.mp4 " + url)

            return send_from_directory(".",
                                       "download0.mp4", as_attachment=True)

        else:
            return render_template('download.html', error='You must specify a URL!')

    else:
        return render_template("download.html")


@app.route('/add/upload/', methods=['GET', 'POST'])
def uploadLocalVideo():
    if request.method == 'POST':
        if 'file' not in request.files:
            return showError('No selected file', request.url)

        file = request.files['file']

        if file.filename == '':
            return showError('No selected file', request.url)

        elif request.form['title'] == '':
            return showError('Title is required', request.url)

        else:
            filename = secure_filename(file.filename)

            os.mkdir(getVideoFolder() +
                     "/" + request.form['title'])

            file.save(os.path.join(getVideoFolder() +
                      "/"+request.form['title'], filename))

            with open(getVideoFolder() + "/"+request.form['title'] + '/' + request.form['title'] + ".description", 'w') as file1:
                file1.write(request.form['nm'])

            return redirect('/videos/{}'.format(request.form['title']))

        return "Nothing happened???"

    else:
        return render_template("upload.html")


@app.route('/settings/', methods=['GET', 'POST'])
def settingsPage():
    if request.method == 'POST':
        config = getConfig()

        for field in request.form:
            config.set(field, request.form[field])

        return redirect("/?popup=Settings%20Successfully%20Saved")

    else:
        config = getConfig()

        return render_template("settings.html", config=config)


@app.route("/random_video", methods=['GET'])
def randomVideo():
    if from_video := request.args.get('from'):
        return redirect("/videos/" + random.choice(list(filter(lambda x: x != from_video, getVideos()))))

    return redirect("/videos/" + random.choice(getVideos()))
    

@app.errorhandler(404)
def page_not_found(e):
    return showError(e, url_for("homePage"), "404: Not Found", "Feature you want added? Submit a request at <a href=https://github.com/r2boyo25/yt-pi/issues/new/choose>my GitHub page. </a>", errorcode=404)


@app.errorhandler(400)
def bad_requesthandler(e):
    return showError(e, url_for("homePage"), "404: Not Found", "Submit a bug report at <a href=https://github.com/r2boyo25/yt-pi/issues/new/choose>my GitHub page. </a>", errorcode=400)


if __name__ == "__main__":
    try:
        currentConfig = json.loads(requests.get(
            "https://raw.githubusercontent.com/R2Boyo25/yt-pi/master/config.json").text)

        if float(currentConfig["version"]) > float(getConfig().get('version')):
            if not ("/" + ('/'.join(os.path.abspath(getVideoFolder()).split("/"))) in os.path.abspath("yt-pi.py")):
                os.chdir("./..")

                os.system("rm -rf yt-pi")

                os.system("git clone https://github.com/r2boyo25/yt-pi")

                os.chdir("yt-pi")

    except Exception:
        print("Cannot connect to github - update checker unavailable.")

    youtubedl = not os.system("python3 -m pip freeze | grep yt-dlp")

    app.run(debug=True, host='0.0.0.0', port=getConfig().get("port"))
