# 📰 My Project News Portal Website for ENT :D

A simple **Flask-based news portal** with authentication and role-based permissions.  
- **Admins** can create, read, update, delete (CRUD) news articles.  
- **Users** can register/login and read articles only.  
- Articles can include a **banner image** (JPG, JPEG, PNG, GIF).  
- Uses **Bootstrap 5** for responsive design.  

## Features
- Admin & User login system
- User self-registration
- Admin-only CRUD for articles
- Banner image upload with type restrictions
- Responsive Bootstrap UI
- Supports safe HTML in article content (`<h1>`, `<p>`, `<img>`, etc.), scripts are stripped

## Requirements / Dependencies
- Python 3.9+  
- Flask  
- Flask-Login  
- Flask-SQLAlchemy  
- Werkzeug  
- Bleach  
- Bootstrap (via CDN)

### Install

make a virtual enviroment
```bash
python -m venv .venv
```

activate for windows
```bash
.venv\Scripts\activate
```
for mac/linux 
```bash
source .venv/bin/activate
```

and then dependencies install
```bash
pip install -r requirements.txt

```

## Running the App
```bash
flask --app app run
```
Then open: [http://127.0.0.1:5000]


## Admin Login
- **Email:** admin@example.com  
- **Password:** admin123  


## Project Structure
```
news-portal/
├─> app.py
├─> requirements.txt
├─> static/uploads/
└─> templates/
```

## 🇮🇩 Dokumentasi Bahasa Indonesia

### Fitur-Fitur
- Sistem login Admin & User  
- Registrasi mandiri untuk User  
- CRUD artikel hanya untuk Admin  
- Upload gambar banner (JPG, JPEG, PNG, GIF)  
- Tampilan responsif dengan Bootstrap  
- Konten artikel mendukung HTML simple (judul, paragraf, gambar), script otomatis dihapus

### Syarat/Dependency (ketergantungan? apa ya terjemahannya)
- Python 3.9+  
- Flask  
- Flask-Login  
- Flask-SQLAlchemy  
- Werkzeug  
- Bleach  
- Bootstrap (via CDN)

### install:
```bash
pip install -r requirements.txt
```

### run app :DDD
```bash
flask --app app run
```
Buka di browser: [http://127.0.0.1:5000]

### struktur proyek

news-portal/
├─> app.py
├─> requirements.txt
├─> static/uploads/
└─> templates/

### Login Admin default
- **Email:** admin@example.com  
- **Password:** admin123  

License MIT

ok thenks