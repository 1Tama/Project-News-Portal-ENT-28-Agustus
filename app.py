import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import bleach

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB limit

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Sanitization rules
ALLOWED_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'b', 'i', 'u', 'em', 'strong',
    'a', 'ul', 'ol', 'li', 'br', 'span',
    'img'
]
ALLOWED_ATTRS = {
    'a': ['href', 'title'],
    'img': ['src', 'alt']
}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    articles = Article.query.all()
    return render_template("index.html", articles=articles)

@app.route("/article/<int:article_id>")
def article(article_id):
    art = Article.query.get_or_404(article_id)
    return render_template("article.html", article=art)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("register"))
        user = User(email=email, password=password, role="user")
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("index"))
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        sanitized_content = bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
        file = request.files.get("image")
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = str(uuid.uuid4()) + "_" + filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        article = Article(title=title, content=sanitized_content, image=filename)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for("index"))
    articles = Article.query.all()
    return render_template("admin.html", articles=articles)

@app.route("/admin/edit/<int:article_id>", methods=["GET", "POST"])
@login_required
def edit_article(article_id):
    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("index"))
    article = Article.query.get_or_404(article_id)
    if request.method == "POST":
        article.title = request.form["title"]
        content = request.form["content"]
        article.content = bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
        file = request.files.get("image")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = str(uuid.uuid4()) + "_" + filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            article.image = filename
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit_article.html", article=article)

@app.route("/admin/delete/<int:article_id>")
@login_required
def delete_article(article_id):
    if current_user.role != "admin":
        flash("Access denied")
        return redirect(url_for("index"))
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for("admin"))

# Create default admin on first run
@app.before_request
def create_admin():
    db.create_all()
    if not User.query.filter_by(role="admin").first():
        admin = User(email="admin@example.com", password=generate_password_hash("admin123"), role="admin")
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
