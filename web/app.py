# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os
from flask import Flask, render_template, flash, redirect, url_for, Markup, request, make_response, Response, send_from_directory
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import random
import time

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

bootstrap = Bootstrap(app)
basedir = os.path.abspath(os.path.dirname(__file__))
uploadDir = os.path.join(basedir, 'static/uploads')

user = {
    'username': 'Grey Li',
    'bio': 'A boy who loves movies and music.',
}

movies = [
    {'name': 'My Neighbor Totoro', 'year': '1988'},
    {'name': 'Three Colours trilogy', 'year': '1993'},
    {'name': 'Forrest Gump', 'year': '1994'},
    {'name': 'Perfect Blue', 'year': '1997'},
    {'name': 'The Matrix', 'year': '1999'},
    {'name': 'Memento', 'year': '2000'},
    {'name': 'The Bucket list', 'year': '2007'},
    {'name': 'Black Swan', 'year': '2010'},
    {'name': 'Gone Girl', 'year': '2014'},
    {'name': 'CoCo', 'year': '2017'},
]


@app.route('/watchlist')
def watchlist():
    return render_template('watchlist.html', user=user, movies=movies)


@app.route('/')
def index():
    return render_template('index.html')


# register template context handler
@app.context_processor
def inject_info():
    foo = 'I am foo.'
    return dict(foo=foo)  # equal to: return {'foo': foo}


# register template global function
@app.template_global()
def bar():
    return 'I am bar.'


# register template filter
@app.template_filter()
def musical(s):
    return s + Markup(' &#9835;')


# register template test
@app.template_test()
def baz(n):
    if n == 'baz':
        return True
    return False

@app.route('/progress')
def progress():
	def generate():
		x = 0
		
		while x <= 100:
			yield "data:" + str(x) + "\n\n"
			x = x + 1
			time.sleep(random.random()/5)

	return Response(generate(), mimetype= 'text/event-stream')

@app.route('/watchlist2')
def watchlist_with_static():
    return render_template('watchlist_with_static.html', user=user, movies=movies)

@app.route('/net_Choral', methods=['POST', 'GET'])
def net_Choral():
    if request.method == 'POST':
        f = request.files.get('fileupload')
        if not os.path.exists(uploadDir):
            os.makedirs(uploadDir)
        if f:
            filename = secure_filename(f.filename)
            types = ['mxl', 'midi', 'tif']
            if filename.split('.')[-1] in types:
                uploadpath = os.path.join(uploadDir, filename)
                f.save(uploadpath)
                flash('Upload Load Successful!', 'success')
            else:
                flash('Unknown Types!', 'danger')
        else:
            flash('No File Selected.', 'danger')
        return render_template('baseup_Choral.html', imagename=filename)
    return render_template('baseup_Choral.html')
    
@app.route('/net_Fugue', methods=['POST', 'GET'])
def net_Fugue():
    if request.method == 'POST':
        f = request.files.get('fileupload')
        if not os.path.exists(uploadDir):
            os.makedirs(uploadDir)
        if f:
            filename = secure_filename(f.filename)
            types = ['mxl', 'midi', 'tif']
            if filename.split('.')[-1] in types:
                uploadpath = os.path.join(uploadDir, filename)
                f.save(uploadpath)
                flash('Upload Load Successful!', 'success')
            else:
                flash('Unknown Types!', 'danger')
        else:
            flash('No File Selected.', 'danger')
        return render_template('baseup_Fugue.html', imagename=filename)
    return render_template('baseup_Fugue.html')

@app.route('/net_Jazz', methods=['POST', 'GET'])
def net_Jazz():
    if request.method == 'POST':
        f = request.files.get('fileupload')
        if not os.path.exists(uploadDir):
            os.makedirs(uploadDir)
        if f:
            filename = secure_filename(f.filename)
            types = ['mxl', 'midi', 'tif']
            if filename.split('.')[-1] in types:
                uploadpath = os.path.join(uploadDir, filename)
                f.save(uploadpath)
                flash('Upload Load Successful!', 'success')
            else:
                flash('Unknown Types!', 'danger')
        else:
            flash('No File Selected.', 'danger')
        return render_template('baseup_Jazz.html', imagename=filename)
    return render_template('baseup_Jazz.html')
    
@app.route('/net_Pop', methods=['POST', 'GET'])
def net_Pop():
    if request.method == 'POST':
        f = request.files.get('fileupload')
        if not os.path.exists(uploadDir):
            os.makedirs(uploadDir)
        if f:
            filename = secure_filename(f.filename)
            types = ['mxl', 'midi', 'tif']
            if filename.split('.')[-1] in types:
                uploadpath = os.path.join(uploadDir, filename)
                f.save(uploadpath)
                flash('Upload Load Successful!', 'success')
            else:
                flash('Unknown Types!', 'danger')
        else:
            flash('No File Selected.', 'danger')
        return render_template('baseup_Pop.html', imagename=filename)
    return render_template('baseup_Pop.html')

@app.route('/net_Choral_bar', methods=['POST', 'GET'])
def net_Choral_bar():
    if os.path.exists('/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/uploads/theme.mxl'):
    	return render_template('basebar_Choral.html')
    else:
        flash('No File Selected!', 'danger')
        return redirect(url_for('net_Choral'))
        
@app.route('/net_Fugue_bar', methods=['POST', 'GET'])
def net_Fugue_bar():
    if os.path.exists('/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/uploads/theme.mxl'):
    	return render_template('basebar_Fugue.html')
    else:
        flash('No File Selected!', 'danger')
        return redirect(url_for('net_Fugue'))
        
@app.route('/net_Jazz_bar', methods=['POST', 'GET'])
def net_Jazz_bar():
    if os.path.exists('/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/uploads/theme.mxl'):
    	return render_template('basebar_Jazz.html')
    else:
        flash('No File Selected!', 'danger')
        return redirect(url_for('net_Jazz'))
        
@app.route('/net_Pop_bar', methods=['POST', 'GET'])
def net_Pop_bar():
    if os.path.exists('/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/uploads/theme.mxl'):
    	return render_template('basebar_Pop.html')
    else:
        flash('No File Selected!', 'danger')
        return redirect(url_for('net_Pop'))

@app.route('/basedown_Choral', methods=['POST', 'GET'])
def basedown_Choral():
    flash('Process Successful!', 'success')
    if request.method == 'POST':
        flash('Process Successful!', 'success')
        return render_template('basedown_Choral.html')
    return render_template('basedown_Choral.html')
	
@app.route('/basedown_Jazz', methods=['POST', 'GET'])
def basedown_Jazz():
    flash('Process Successful!', 'success')
    if request.method == 'POST':
        flash('Process Successful!', 'success')
        return render_template('basedown_Jazz.html')
    return render_template('basedown_Jazz.html')

@app.route('/basedown_Fugue', methods=['POST', 'GET'])
def basedown_Fugue():
    flash('Process Successful!', 'success')
    if request.method == 'POST':
        flash('Process Successful!', 'success')
        return render_template('basedown_Fugue.html')
    return render_template('basedown_Fugue.html')

@app.route('/basedown_Pop', methods=['POST', 'GET'])
def basedown_Pop():
    flash('Process Successful!', 'success')
    if request.method == 'POST':
        flash('Process Successful!', 'success')
        return render_template('basedown_Pop.html')
    return render_template('basedown_Pop.html')

@app.route("/downloading_choral")
def downloading_choral():
    return send_from_directory("/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/downloads", "Choral.mxl", as_attachment=True)
    
@app.route("/downloading_fugue")
def downloading_fugue():
    return send_from_directory("/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/downloads", "Fugue.mxl", as_attachment=True)
    
@app.route("/downloading_jazz")
def downloading_jazz():
    return send_from_directory("/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/downloads", "Jazz.mxl", as_attachment=True)
    
@app.route("/downloading_pop")
def downloading_pop():
    return send_from_directory("/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/downloads", "Pop.mxl", as_attachment=True)

@app.route("/downloading_choral_pdf")
def downloading_choral_pdf():
    return send_from_directory("/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/downloads", "Choral.pdf", as_attachment=True)
    
@app.route("/downloading_fugue_pdf")
def downloading_fugue_pdf():
    return send_from_directory("/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/downloads", "Fugue.pdf", as_attachment=True)
    
@app.route("/downloading_jazz_pdf")
def downloading_jazz_pdf():
    return send_from_directory("/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/downloads", "Jazz.pdf", as_attachment=True)
    
@app.route("/downloading_pop_pdf")
def downloading_pop_pdf():
    return send_from_directory("/home/gyh/Desktop/编曲项目/网站建设/正式网页/static/downloads", "Pop.pdf", as_attachment=True)

@app.route('/introduction')
def introduction():
    return render_template('introduction.html', user=user, movies=movies)

# message flashing
@app.route('/flash')
def just_flash():
    flash('I am flash, who is looking for me?')
    return redirect(url_for('index'))


# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


# 500 error handler
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=8555)
