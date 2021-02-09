from flask import Flask, abort, render_template, redirect, url_for, request, session, send_from_directory, flash, jsonify
from markupsafe import escape
import random, os, database, json
from werkzeug.utils import secure_filename

# create the application object
app = Flask(__name__)

app.config['DataFolder'] = "/".join(os.path.abspath(__file__).split("/")[:-1]) + "/" + "data"

app.secret_key = os.urandom(24)

def eflash(error, back, title="Error!", backt=None, extra=None):

    extra = extra if extra else ""

    backt = backt if backt else ""

    return render_template("error.html", e=error, url=back, error=title, urlt=backt, extra=extra)

def CoSo(version):
    version = str(version)
    
    return render_template("comingSoon.html", ver=version, background=database.Database("config.json").get('background'))

@app.route("/", methods=['GET'])
def homePage():

    try:

        popup = request.args['popup']

    except Exception as e:

        popup = None

    return render_template('homePage.html', version=database.Database("config.json").get("version"), popup = popup, background=database.Database("config.json").get('background'))

@app.route('/data/<path:filename>/')
def returnData(filename):
    return send_from_directory(app.config['DataFolder'],
                            filename)

@app.route('/videos/')
def videosList():
    
    links=['<!--This Page Was Auto Generated-->\n<div align=\"center\">\n<br>\n<a href=/ ><img src=/data/home.png height=17px /></a>  <input type="text" id="mySearch" onkeyup="myFunction()" placeholder="Search.." title="Type in a category">\n<br><br><ul id="myMenu">']
    f = []
    
    for (dirpath, dirnames, filenames) in os.walk(database.Database("config.json").get("videofolder")):
        f.extend(dirnames)
        break
        
    for thing in f:
        links.append("\n  <li><a align='center' href='{}'><img src='{}' height=12% width=15% /><br><b>{}</b></a><br></li>".format('/videos/'+thing.replace("'", "%27"), '/videos/'+thing.replace("'", "%27")+'/thumb',thing))
        
    links.append('</ul></div>')
    
    return render_template('videos.html', links=''.join(links), background=database.Database("config.json").get('background'))

@app.route('/videos/<video>')
def videoPage(video):
    
    for root, dirs, files in os.walk(database.Database("config.json").get("videofolder") + '/' + video):
        
        for file in files:
            
            if file.endswith('.description'):
                
                with open(database.Database("config.json").get("videofolder") + '/' + video + '/' + file, 'r') as de:
                
                    desc = de.read()
        
        try:
            
            desc
        
        except:
            
            desc=''
        
        break
    
    for root, dirs, files in os.walk(database.Database("config.json").get("videofolder") + '/' + video):
        
        for file in files:
            
            if file.endswith('.mp4') or file.endswith('.webm'):
                
                return render_template("video.html", path='/vidfile/' + video.replace("'", "%27") + "/" + file, description=desc.replace("\n", "\n<br>"), title=video, background=database.Database("config.json").get('background'))
        
        break

@app.route('/videos/<video>/thumb')
def videoPageThumb(video):
    
    for root, dirs, files in os.walk(database.Database("config.json").get("videofolder") + '/' + video):
        
        print(files)
        
        for file in files:
            
            if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.webp') or file.endswith('.jpeg'):
                
                return send_from_directory(database.Database("config.json").get("videofolder") + "/" + video + "/",
                            file)
                            
        break

    return send_from_directory("data", "eye.png")

@app.route("/vidfile/<folder>/<file>")
def videourlpagething(folder, file):
    
    return send_from_directory(database.Database("config.json").get("videofolder") + "/" + folder + "/",
                            file)

@app.route('/credits/')
def creditsPage():
    return render_template('credits.html', background=database.Database("config.json").get('background'))

@app.route('/add/')
def addVideoPage():
    return render_template('addVideo.html', background=database.Database("config.json").get('background'))

@app.route('/add/yt/', methods=['GET', 'POST']) 
def downloadYtVideo():
    if request.method == 'POST':
        
        url = request.form['url']
        
        if url != '':
            
            os.system("python3 -m youtube_dl -f best -o \"" + database.Database("config.json").get("videofolder") + "/%(title)s/%(title)s.%(ext)s\"" + " --write-thumbnail --write-description " + url)
            
            return redirect('/')
            
        else:
            
            return render_template('download.html', error='You must specify a URL!', background=database.Database("config.json").get('background'))
        
    else:
        
        return render_template("download.html", background=database.Database("config.json").get('background'))

@app.route('/add/upload/', methods=['GET', 'POST'])
def uploadLocalVideo():

    if request.method == 'POST':

        if 'file' not in request.files:
            return eflash('No selected file', request.url)

        file = request.files['file']

        if file.filename == '':
        
            return eflash('No selected file', request.url)

        elif request.form['title'] == '':

            return eflash('Title is required', request.url)

        else:

            filename = secure_filename(file.filename)

            os.mkdir(database.Database("config.json").get("videofolder") + "/" + request.form['title'])

            file.save(os.path.join(database.Database("config.json").get("videofolder") + "/"+request.form['title'], filename))

            with open(database.Database("config.json").get("videofolder") + "/"+request.form['title'] + '/' + request.form['title'] + ".description", 'w') as file1:

                file1.write(request.form['nm'])

            return redirect('/videos/{}'.format(request.form['title']))
        
        return "Nothing happened???"
        
    else:
        
        return render_template("upload.html", background=database.Database("config.json").get('background'))

@app.route('/settings/', methods=['GET', 'POST'])
def settingsPage():

    if request.method == 'POST':

        config = database.Database("config.json")

        for field in request.form:

            config.set(field, request.form[field])

        return redirect("/?popup=Settings%20Successfully%20Saved")

    else:

        config = database.Database("config.json")
        
        return render_template("settings.html", config=config, background=database.Database("config.json").get('background'))

@app.errorhandler(404)
def page_not_found(e):
<<<<<<< HEAD
    
    return eflash(e, url_for("homePage"), "404: Not Found", "Go Home", "Feature you want added? Submit a request at <a href=https://github.com/r2boyo25/yt-pi/issues/new/choose>my GitHub page. </a>")

    #return render_template('404.html', error=e)

@app.errorhandler(400)
def bad_requesthandler(e):

    return eflash(e, url_for("homePage"), "404: Not Found", "Go Home", "Submit a bug report at <a href=https://github.com/r2boyo25/yt-pi/issues/new/choose>my GitHub page. </a>")

    #return render_template('400.html', error=e)
=======
    return render_template('404.html', error=e, background=database.Database("config.json").get('background'))

@app.errorhandler(400)
def bad_requesthandler(e):
    return render_template('400.html', error=e, background=database.Database("config.json").get('background'))
>>>>>>> 8054d15e2096892e6f0c82e8c4015f7f4326fa03

if __name__ == "__main__":

    app.run(debug=True, host='0.0.0.0', port=database.Database("config.json").get("port"))
