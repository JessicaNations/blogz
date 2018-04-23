from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key='1234abcd'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

@app.before_request
def require_login():
    safe_routes = ['index','blog_total','login','signup']
    if 'username' not in session:
        if request.endpoint not in safe_routes: 
                return redirect('/login')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/',  methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['POST','GET'])
def login():
    
    if ('username' in session):
        flash('You are already logged in')
        return redirect('/')

    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        existing_user=User.query.filter_by(username=username).first()
        username_error = ''
        password_error = ''
        
        if not existing_user:
            username_error = 'User does not exist. Please check your spelling'
            return render_template('login.html', username=username, username_error=username_error)

        if password != existing_user.password:
            password_error='Password error'
            return render_template('login.html', username=username, password_error=password_error)

        if existing_user and existing_user.password==password:
            session['username']=username
            flash('Logged in')
            return redirect('/newpost')

    else:
        return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        verify=request.form['verify']
        existing_user=User.query.filter_by(username=username).first()
        have_error=False
        username_error=''
        password_error=''
        verify_error = ''

        #validate if existing user
        if existing_user:
            username_error='username already registered for a user'
            return render_template('signup.html',username=username,username_error=username_error)

        #validate username
        if not username:
            username_error='username required'
            have_error=True

        if ' ' in username:
            username_error='No blank spaces'
            have_error=True
        
        if len(username) <3 or len(username) >20:
                username_error='Username must contain 3-20 characters and no blank spaces'
                have_error=True
        
        #validate password
        if not password:
            password_error='password required'
            have_error=True

        if ' ' in password:
            password_error='No blank spaces'
            have_error=True

        if len(password)<3 or len(password)>20:
                password_error='Password must contain 3-20 characters and no blank spaces'
                have_error=True
        
        #validate verify
        if verify != password:
            verify_error='Passwords must match'
            have_error=True

        #validate not existing user
        if not existing_user and have_error==False:
            new_user=User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username']=username
            return redirect('/blog')
        else:
            return render_template('signup.html',username=username,username_error=username_error,password_error=password_error,verify_error=verify_error) 
        
    return render_template('signup.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog_total():
    if request.method == 'GET' and request.args.get('id'):
        id = request.args.get('id')
        all_posts = Blog.query.filter_by(id=id).all()
        return render_template('allpost.html', all_posts=all_posts)

    if request.method == 'GET' and request.args.get('username'):
        username = request.args.get("username")
        user_id = User.query.get(username)
        user_posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template("singleuser.html", user_posts=user_posts)
   
    else:
        all_posts=Blog.query.order_by(Blog.id).all()
        return render_template('allpost.html', all_posts=all_posts)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        title_error = ''
        content_error = ''
        owner = User.query.filter_by(username=session['username']).first()

        if not title:
            title_error = "title required"
        if not content:
            content_error = "text required"
        if not title_error and not content_error:
            title = title
            content = content
            owner = owner
            new_post = Blog(title, content, owner)
            db.session.add(new_post)
            db.session.commit()
            flash("New post added")
            
            id = new_post.id
            
            id = str(id)
            return redirect('/blog?id='+id)
        else:
            flash("title and text required")
            return render_template('newpost.html',title=title,content=content,title_error=title_error,content_error=content_error)
    else:
        title=''
        content=''
        return render_template('newpost.html',title=title,content=content)

@app.route('/singlepost', methods=['GET','POST'])
def single_post():
    post_ided = Blog.query.get(id)
    print(post_ided)
    singlepost="?id="+ post_ided
    print(singlepost)
    return redirect('/blog{singlepost}' .format(singlepost=singlepost))

if __name__ == '__main__':
    app.run()