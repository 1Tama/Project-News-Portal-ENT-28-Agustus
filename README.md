# News Portal

This project is a simple news portal web application built with Flask, has plenty of features.
This project was made for OPREC ENT Gen 20 :D

## Features

- **User Roles:** Admins and writers - each with their own dashboard/panel
- **Article Management:** Create, edit, and delete articles with banner images
- **Markdown Support:** Write articles in Markdown format
- **Search:** Search articles by title from the navbar
- **Responsive Design:** Nice clean and responsive, mobile-friendly UI using Bootstrap 5
- **Secure:** Passwords are hashed, content is sanitized, and no sensitive user info is exposed
- **Slug URLs:** Articles use SEO-friendly slugs in URLs
- **Timezone-aware:** Article timestamps are shown in your local timezone

## What is used (tech stack)

- **Backend:** Flask, Flask-Login, Flask-SQLAlchemy
- **Frontend:** Bootstrap 5, Jinja2 templates
- **Markdown:** python-markdown
- **Sanitization:** bleach
- **Slug Generation:** python-slugify
- **Database:** SQLite

## Installation

1. **Donwload le code**

2. **Create a virtual environment**
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   .venv\Scripts\activate # Windows
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Setting up the database:**
   - The database will be created automatically if first time running
   - A default admin account is created if none exists

## To run the app :

```sh
flask run
```
or
```sh
python app.py
```

- open [http://127.0.0.1:5000/]

## Default Admin Login

- **Email:** admin@example.com
- **Password:** admin123

## Usage

- **Admins:** Can manage all articles and accounts (admins/writers)
- **Writers:** Can create and manage their own articles (only their own, if articles created by others dont show up in your panel as a writer just know it is intentional :DDD)
- **Markdown:** Write articles using Markdown syntax for formatting
- **Simple HTML:** Also supports simple html for article content
- **Search:** Use the search bar in the navbar to find articles by title

## Customization

- Change the default timezone in `app.py` (`LOCAL_TZ`).
- Update the background image by replacing `static/background.jpg`.
- Adjust allowed Markdown/HTML tags in `app.py` (`ALLOWED_TAGS`, `ALLOWED_ATTRS`).

## Licensing

MIT License
