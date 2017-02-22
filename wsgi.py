import os
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, session, g
from werkzeug import secure_filename
from functools import wraps
'''from flask.ext.mysql import MySql
mysql = MySql()'''

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['html', 'py'])
app.secret_key = 'some_secret'

#MySql configurations
'''app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '20022013'
app.config['MYSQL_DATABASE_DB'] = 'db_file_handling'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in app.config['ALLOWED_EXTENSIONS']

def read_session(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        session.permanent = True
        try:
            if session['user'] is False:
                flash('Username or Password is Invalid')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        except KeyError:
            flash('Your session is time out, login first')
            return redirect(url_for('index'))
    return wrap

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session.pop('user', None)

        if request.form['password'] == '20022013':
            session['user'] = request.form['username']
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/logout')
def loguot():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/home')
@read_session
def home():
    return render_template('home.html')

@app.route('/upload')
@read_session
def upload():
    return render_template('upload.html')

@app.route('/upload_handling', methods = ['POST'])
@read_session
def upload_handling():
    try:
        file = request.files['file']
        if file and not allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('list_files'))
        else:
            return ('Ekstensi file tidak diperbolehkan')
    except Exception as e:
        return {'error': str(e)}

@app.route('/files/delete_item', methods = ['GET', 'POST'])
@read_session
def delete_handling():
    if request.method == 'POST':
        filename = request.form['filename']
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('list_files')) #('Deleted')
        except Exception as e:
            return {'error': str(e)}

@app.route('/files', methods = ['GET'])
@read_session
def list_files():
    path = os.path.expanduser(u'uploads/')
    return render_template('files.html', tree=make_tree(path))

def make_tree(path):
    i = 0
    tree = dict(name=os.path.basename(path), children=[])
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                i=i+1
                tree['children'].append(dict(name=name, i=i))
    return tree

@app.route('/files/view/<filename>')
@read_session
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
