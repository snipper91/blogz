from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blog@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, blog, user):
        self.title = title
        self.body = blog
        self.user = user

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['index', 'blog', 'mypost', 'signup', 'login']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():

    return render_template('index.html')

@app.route('/blog', methods=['POST','GET'])
def blog():

    author = request.arg.get('user')
    if author:
        blogs = Blog.query.filter_by(user_id=author)
        user[author] = User.query.filter_by(id=author)
        return render_template('blog.html', blogs=blogs, user_dict=user)

    blogs = Blog.query.all()
    user_dict = {}
    users = User.query.all()
    for user in users:
        user_dict[user.id] = user.username

    return render_template('blog.html', blogs=blogs, user_dict=user_dict)

@app.route('/newpost', methods=['POST','GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['title']
        blog = request.form['blog']
        title_error = ''
        text_error = ''
        if title == '':
            title_error = 'Enter a title for the blog post.'
        if blog == '':
            text_error = 'Enter a blog post.'
        if title_error != '' or text_error != '':
            return render_template('newpost.html', title_error=title_error, text_error=text_error)
        else:
            user = User.query.filter_by(username=session['username']).first()
            blog_post = Blog(title, blog, user)
            db.session.add(blog_post)
            db.session.commit()
            query_param_url = '/mypost?id=' + str(blog_post.id)
            return redirect(query_param_url)

    return render_template('newpost.html')

@app.route('/mypost', methods=['POST', 'GET'])
def mypost():

    id = request.args.get('id')
    post = Blog.query.get(id)

    return render_template('mypost.html', post=post)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']
    user = User.query.filter_by(username=username).first()
    if not username:
        user_error = 'Please enter a username.'
        return render_template('signup.html', user_error=user_error)
    if not password:
        password_error = 'Please enter a password.'
        return render_template('signup.html', password_error=password_error)
    if user:
        user_error = 'That user already exists.'
        return render_template('signup.html', user_error=user_error)
    if password != verify:
        password_error = 'Passwords do not match.'
        return render_template('signup.html', password_error=password_error)
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    session['username'] = username
    return redirect('/newpost')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if not user:
        username_error = 'That user does not exist.'
        return render_template('login.html', username_error=username_error)
    if password != user.password:
        password_error = 'Wrong password.'
        return render_template('login.html', password_error=password_error)
    session['username'] = username
    return redirect('/newpost')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()