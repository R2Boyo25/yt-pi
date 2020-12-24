from flask import Flask, abort, render_template, redirect, url_for, request, session, send_from_directory, flash, jsonify
from markupsafe import escape
import random, os, database, json
from werkzeug.utils import secure_filename

# create the application object
app = Flask(__name__)

app.config['DataFolder'] = "/".join(os.path.abspath(__file__).split("/")[:-1]) + "/" + "data"

def CoSo(version):
    version = str(version)
    
    return render_template("comingSoon.html", ver=version)

@app.route("/")
def homePage():
    return render_template('homePage.html', version=database.Database("config.json").get("version"))

@app.route('/data/<path:filename>/')
def returnData(filename):
    return send_from_directory(app.config['DataFolder'],
                            filename)

@app.route('/videos/')
def videosList():
    
    links=['<!--This Page Was Auto Generated-->\n<div align=\"center\">\n<br>\n<input type="text" id="mySearch" onkeyup="myFunction()" placeholder="Search.." title="Type in a category">\n<br><ul id="myMenu">']
    f = []
    
    for (dirpath, dirnames, filenames) in os.walk(database.Database("config.json").get("videofolder")):
        f.extend(dirnames)
        break
        
    for thing in f:
        links.append("\n  <li><a align='center' href='{}'><img src='{}' height=10% width=15% /><br><b>{}</b></a><br></li>".format('/videos/'+thing, '/videos/'+thing+'/thumb',thing))
        
    links.append('</ul></div>')
    
    return render_template('videos.html', links=''.join(links))

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
            
            if file.endswith('.mp4'):
                
                return render_template("video.html", path='/vidfile/' + video + "/" + file, description=desc.replace("\n", "\n<br>"), title=video)
        
        break

@app.route('/videos/<video>/thumb')
def videoPageThumb(video):
    
    for root, dirs, files in os.walk(database.Database("config.json").get("videofolder") + '/' + video):
        
        print(files)
        
        for file in files:
            
            if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.webp'):
                
                return send_from_directory(database.Database("config.json").get("videofolder") + "/" + video + "/",
                            file)
                            
        break

@app.route("/vidfile/<folder>/<file>")
def videourlpagething(folder, file):
    
    return send_from_directory(database.Database("config.json").get("videofolder") + "/" + folder + "/",
                            file)

@app.route('/credits/')
def creditsPage():
    return render_template('credits.html')

@app.route('/add/')
def addVideoPage():
    return render_template('addVideo.html')

@app.route('/add/yt/', methods=['GET', 'POST']) 
def downloadYtVideo():
    if request.method == 'POST':
        
        url = request.form['url']
        
        if url != '':
            
            os.system("python3 -m youtube_dl -f best -o \"" + database.Database("config.json").get("videofolder") + "/%(title)s/%(title)s.%(ext)s\"" + " --write-thumbnail --write-description " + url)
            
            return redirect('/')
            
        else:
            
            return render_template('download.html', error='You must specify a URL!')
        
    else:
        
        return render_template("download.html")

@app.route('/add/upload/')
def uploadLocalVideo():
    return CoSo(1.1)

@app.route('/settings/')
def settingsPage():
    return CoSo(1.1)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e)

@app.errorhandler(400)
def bad_requesthandler(e):
    return render_template('400.html', error=e)

@app.errorhandler(403)
def permissiondeniedhandler(e):
    return render_template('403.html', error=e)

app.run(debug=True, host='0.0.0.0', port=database.Database("config.json").get("port"))
