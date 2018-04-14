from flask import Flask, request, redirect, render_template, session, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://build-a-blog:YES@localhost:8889/build-a-blog"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(50))
    signup_date = db.Column(db.DateTime)

    def __init__(self, username, password): #, signup_date=None
        self.username = username
        self.password = password
        #if signup_date is None:
        #    signup_date = datetime.utcnow()
       # self.signup_date = signup_date


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.String(6000))
   

    def __init__(self, title, content):
        self.title = title
        self.content = content



#APP ROUTES / HANDLERS
#root directory just redirects to main blog page

@app.route("/")
@app.route('/index')
def index():

    if 'username' in session:
        print("[index] logged in as " + session['username'])

    users = User.query.order_by(User.signup_date.desc()).all()
    print(users)

    return render_template('index.html', users=users)

@app.route("/")
def redirector():
    return redirect("/blog")

@app.route("/blog", methods=["POST", "GET"])
def blog():
    #the form should direct to /newpost instead, it would make error handling a lot cleaner         
    if request.method == "POST":
        new_title = request.form["title"]
        new_content = request.form["content"]

        if not new_title or not new_content:
            return render_template("newpost.html",title=new_title, content=new_content, error_message="Error, try again")

        new_post = Blog(new_title, new_content)
        db.session.add(new_post)
        db.session.commit()
        return redirect("/blog?id="+str(new_post.id))
    
    view_post_id = request.args.get("id")
    if view_post_id:
        view_post = Blog.query.get(int(view_post_id))
    else:
        view_post = ""
    
    posts = Blog.query.order_by(Blog.id.desc()).all()

    return render_template("blog.html", posts=posts, view_post=view_post)

@app.route("/newpost", methods=["GET"])
def newpost():
    return render_template("newpost.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=session['username']).first()
        user_password = user.password

        if user_password != password:
            wrong_pwd = "Incorrect password entered."
            return render_template('login.html', wrong_pwd=wrong_pwd)

        print("[login] logged in as " + session['username'])
        return redirect(url_for('newpost'))

    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('blog'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        print(username + " " + password)

        if not password == verify:
            verify_error = "Passwords Don't Match"
            return render_template('signup.html', verify_error=verify_error)

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = request.form['username']
            return redirect(url_for('newpost', user=new_user.username))
        else:
            username_error = "A user with that username already exists"
            return render_template('signup.html', username_error=username_error)

    return render_template('signup.html')

# set the secret key.  keep this really secret:
app.secret_key = '1234'


#if __name__ == '__main__':
 #   app.run(debug=True)

#only run when supposed to
if __name__ == "__main__":
    app.run()