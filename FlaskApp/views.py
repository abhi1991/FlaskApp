import  os
from flask import session,render_template,url_for,request,redirect,send_from_directory,flash,g
from werkzeug.utils import secure_filename
from flask.ext.login import login_user, logout_user, current_user, login_required
from FlaskApp import app, db, lm, oid
from FlaskApp import cluster
from forms import LoginForm,ContactForm
from models import User, ROLE_USER, ROLE_ADMIN
from flask.ext.mail import Message , Mail
mail =Mail()
import cluster

UPLOAD_FOLDER ='/home/ubuntu/uploads/'
DOWNLOAD_FOLDER ='/home/ubuntu/downloads'

#=============config=============
ALLOWED_EXTENSIONS = set(['txt'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'contact@keywordgrouper.net'
app.config["MAIL_PASSWORD"] = 'mother1991'
 

app.secret_key = "guesswhat"

#==========Database code===========

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
#=======G user===================
@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
#@login_required
def index():
    user = g.user
    return render_template("index.html")

def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

#=============upload code======
@app.route('/',methods = ['GET','POST'])
def upload_file():
        if request.method == 'POST':
                file = request.files['file']
                if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        global path
                        path = UPLOAD_FOLDER+"/"+filename
                        #filename(filename)
                        #counts elements in file and if it is more than x then redirect it to login page
                        count = word_count(path)
                        if count < 2500:
                                processing(str(path))
                                return download()#,ofile=filename[:-4]+".csv")),csvfile = path[9:-4]+".csv"))
                        elif count> 2500 and count <= 2501:
                            processing(str(path))
                            return redirect(url_for('login'))
                        else:
                            return render_template("limit.html")
                        
                return render_template("other.html")
    
#=================Download===============
@app.route('/download')
def download():
    return redirect('downloadfile') and render_template("download.html")

#====================download link =================
@app.route('/Keyword_group.csv',methods = ['GET','POST'])
def downloadfile():
    
    return send_from_directory(DOWNLOAD_FOLDER,
                               cluster.gen_file)

#==================login======================
@app.route('/login', methods = ['GET','POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('download'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])
#=================================Invalid login handler=================
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index2'))

#=======================Logout ===============
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#===============clustering process==========
def processing(path):
        cluster.grouper(path)

def word_count(filename):
        with open(filename) as f:
                count = sum(1 for _ in f)
                return count
        
#========Contact=======================
@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()
 
  if request.method == 'POST':
    if form.validate() == False:
      flash('All fields are required.')
      return render_template('contact.html', form=form)
    else:
      msg = Message(form.subject.data, sender='contact@keywordgrouper.net', recipients=['abhishek.raj1991@gmail.com'])
      msg.body = """
      From: %s &lt;%s&gt;
      %s
      """ % (form.name.data, form.email.data, form.message.data)
      mail.send(msg)
 
      return render_template('contact.html', success=True)
 
  elif request.method == 'GET':
    return render_template('contact.html', form=form)
mail.init_app(app)

#=====================Error handing===================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

#===================Sitemap and robot.txt ==================
@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder,request.path[1:])

#==============================================================
