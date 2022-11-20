from flask import Flask
from flask import render_template, request, redirect
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
import os
import pytz

app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SECRET_KEY'] = os.urandom(24)
# initialize the app with the extension
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                    default=datetime.now(pytz.timezone('Asia/Tokyo')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(12))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(username=username, password=generate_password_hash(password, method='sha256'))

        db.session.add(user) # 追加
        db.session.commit() # DBにコミット

        return redirect('/login')

    # アクセスする場合
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first() #最初の値を取得※複数存在しないため
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """
    ログアウト
    """
    logout_user()
    return redirect('/login')
    
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    初期表示
    """
    if request.method == 'GET':
        todos = Todo.query.all()
        return render_template('index.html', todos=todos)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    新規登録
    """
    # 投稿する場合
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        todo = Todo(title=title, body=body)

        db.session.add(todo) # 追加
        db.session.commit() # DBにコミット

        return redirect('/')

    # アクセスする場合
    else:
        return render_template('create.html')

@app.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    編集
    """
    todo = Todo.query.get(id)

    # アクセスする場合
    if request.method == 'GET':
        return render_template('edit.html', todo=todo)

    # 更新する場合
    else:
        todo.title = request.form.get('title')
        todo.body = request.form.get('body')

        db.session.commit() # DBにコミット

        return redirect('/')

@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    """
    削除
    """
    todo = Todo.query.get(id)

    db.session.delete(todo)
    db.session.commit()

    return redirect('/')


@app.route('/<int:id>/detail', methods=['GET', 'POST'])
@login_required
def detail(id):
    """
    編集
    """
    todo = Todo.query.get(id)

    # アクセスする場合
    if request.method == 'GET':
        return render_template('detail.html', todo=todo)
    else:
        return redirect('/')