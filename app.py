import os, uuid
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import bleach
from datetime import datetime

# --- Flask app and config ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','devkey')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static','uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png','jpg','jpeg','gif'}
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

# --- Database and Login setup ---
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Allowed HTML tags and attributes for article content ---
ALLOWED_TAGS = ['h1','h2','h3','p','b','i','em','strong','ul','ol','li','br','a','img']
ALLOWED_ATTRS = {'a':['href','title'],'img':['src','alt']}

# --- Helper function to check allowed file extensions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- User model for authentication ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    def is_admin(self):
        return self.role == 'admin'

# --- Article model for news articles ---
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # <-- Add this line

# --- User loader for Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Homepage: show all articles or search results ---
@app.route('/')
def index():
    q = request.args.get('q', '').strip()
    if q:
        articles = Article.query.filter(Article.title.ilike(f'%{q}%')).order_by(Article.id.desc()).all()
    else:
        articles = Article.query.order_by(Article.id.desc()).all()
    return render_template('index.html', articles=articles)

# --- Article detail page ---
@app.route('/article/<int:article_id>')
def article_detail(article_id):
    a = Article.query.get_or_404(article_id)
    return render_template('article.html', article=a)

# --- User registration ---
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        confirm = request.form.get('confirm','')
        if not email or not password:
            flash('Email and password required','danger'); return redirect(url_for('register'))
        if password != confirm:
            flash('Passwords do not match','danger'); return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered','danger'); return redirect(url_for('register'))
        u = User(email=email, password=generate_password_hash(password), role='user')
        db.session.add(u); db.session.commit()
        flash('Account created — please log in','success')
        return redirect(url_for('login'))
    return render_template('register.html')

# --- User login ---
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in','success')
            return redirect(url_for('index'))
        flash('Invalid credentials','danger')
    return render_template('login.html')

# --- User logout ---
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out','success')
    return redirect(url_for('index'))

# --- Decorator to restrict access to admins only ---
def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admins only','danger')
            return redirect(url_for('index'))
        return fn(*args, **kwargs)
    return wrapper

# --- Admin dashboard: manage articles and admins ---
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    articles = Article.query.order_by(Article.id.desc()).all()
    admins = User.query.filter(User.role=='admin').all()
    return render_template('admin_dashboard.html', articles=articles, admins=admins)

# --- Create a new article (admin only) ---
@app.route('/admin/article/new', methods=['GET','POST'])
@login_required
@admin_required
def admin_article_new():
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        content = request.form.get('content','').strip()
        file = request.files.get('image')
        if not title or not content or not file or file.filename=='':
            flash('Title, content, and banner image are required','danger'); return redirect(url_for('admin_article_new'))
        if not allowed_file(file.filename):
            flash('Invalid image type','danger'); return redirect(url_for('admin_article_new'))
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        safe = bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
        art = Article(title=title, content=safe, image=filename)
        db.session.add(art); db.session.commit()
        flash('Article created','success'); return redirect(url_for('admin_dashboard'))
    return render_template('admin_article_edit.html', article=None)

# --- Edit an existing article (admin only) ---
@app.route('/admin/article/edit/<int:article_id>', methods=['GET','POST'])
@login_required
@admin_required
def admin_article_edit(article_id):
    art = Article.query.get_or_404(article_id)
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        content = request.form.get('content','').strip()
        file = request.files.get('image')
        if not title or not content:
            flash('Title and content are required','danger'); return redirect(url_for('admin_article_edit', article_id=article_id))
        if file and file.filename!='':
            if not allowed_file(file.filename):
                flash('Invalid image type','danger'); return redirect(url_for('admin_article_edit', article_id=article_id))
            filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            art.image = filename
        art.title = title
        art.content = bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
        db.session.commit()
        flash('Article updated','success'); return redirect(url_for('admin_dashboard'))
    return render_template('admin_article_edit.html', article=art)

# --- Delete an article (admin only) ---
@app.route('/admin/article/delete/<int:article_id>', methods=['POST'])
@login_required
@admin_required
def admin_article_delete(article_id):
    art = Article.query.get_or_404(article_id)
    db.session.delete(art); db.session.commit()
    flash('Article deleted','success'); return redirect(url_for('admin_dashboard'))

# --- Create a new admin user (admin only) ---
@app.route('/admin/admins/new', methods=['POST'])
@login_required
@admin_required
def admin_create_admin():
    email = request.form.get('email','').strip().lower()
    password = request.form.get('password','')
    if not email or not password:
        flash('Email and password required','danger'); return redirect(url_for('admin_dashboard'))
    if User.query.filter_by(email=email).first():
        flash('User already exists','danger'); return redirect(url_for('admin_dashboard'))
    u = User(email=email, password=generate_password_hash(password), role='admin')
    db.session.add(u); db.session.commit()
    flash('Admin account created','success'); return redirect(url_for('admin_dashboard'))

# --- Delete an admin user (admin only) ---
@app.route('/admin/admins/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_admin(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash('You cannot delete yourself','danger'); return redirect(url_for('admin_dashboard'))
    db.session.delete(u); db.session.commit()
    flash('Admin deleted','success'); return redirect(url_for('admin_dashboard'))

# --- Serve uploaded images ---
@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Initialize the database and create a default admin if none exists ---
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin = User(email='admin@example.com', password=generate_password_hash('admin123'), role='admin')
        db.session.add(admin); db.session.commit()

# --- Run the app ---
if __name__ == '__main__':
    app.run(debug=True)
