from flask import Flask, request, redirect, render_template, session, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:password@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

app.secret_key = '1234abcd'

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.String(6000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner



#APP ROUTES / HANDLERS
#root directory just redirects to main blog page

@app.before_request
def require_login(): 
    allowed_routes = ['index','blog','login','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/',  methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['POST','GET'])
def blog():

   
    if request.method == "POST":
        new_title = request.form["title"]
        new_content = request.form["content"]

        if not new_title or not new_content:
            return render_template("newpost.html",title=new_title, content=new_content, error_message="Your post needs content!")
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(new_title, new_content, owner)
        db.session.add(new_post)
        db.session.commit()
        return redirect("/blog?id="+str(new_post.id))
    
    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template("singleUser.html", page_title = user.username + "'s Posts!", 
                                                      user_blogs=user_blogs)

    view_post_id = request.args.get("id")
    if view_post_id:
        view_post = Blog.query.get(int(view_post_id))
    else:
        view_post = ""
    
    posts = Blog.query.order_by(Blog.id.desc()).all()

    return render_template("blog.html", posts=posts, view_post=view_post)




    
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'GET':
        return render_template('newpost.html')
    if request.method == "POST":
        new_title = request.form["title"]
        new_content = request.form["content"]

        if not new_title or not new_content:
            return render_template("newpost.html",title=new_title, content=new_content, error_message="Your post needs content!")
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(new_title, new_content, owner) #takes 3 positional arguments, but 4 given
        db.session.add(new_post)
        db.session.commit()
        return redirect("/blog?id="+str(new_post.id))
   
    

@app.route("/viewpost", methods=["GET"])
def view_post():
    return render_template("viewpost.html")
   
@app.route("/signup", methods=['GET','POST'])
def signup():
    username_error = ''
    password_error = ''
    verify_error = ''

    if request.method == 'GET':
        return render_template("signup.html")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) < 3 or len(username) > 20:
            username_error = "Invalid username"

        if len(password) < 3 or len(password) > 20:
            password_error = "Invalid password"

        if password != verify:
            verify_error = "Passwords do not match"

        if username_error!='' or password_error!='' or verify_error!='':
            return render_template('signup.html', username=username, username_error=username_error,password_error=password_error,verify_error=verify_error)
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            username_error = "That username already exists"
            return render_template('signup.html', username_error=username_error)

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    else:
        return render_template('signup.html')

@app.route("/login", methods=['GET','POST'])
def login():

    if request.method == 'GET':
        if 'username' not in session:
            return render_template("login.html", page_title='Login')
        else:
            return redirect('/newpost')

    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

        if user and user.password != password:
            password_error = "Incorrect Password"
            return render_template('login.html', password_error=password_error)

        if not user:
            username_error = "Incorrect Username"
            return render_template('login.html', username_error=username_error)

    else:
        return render_template('login.html')
   
@app.route("/logout")
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()