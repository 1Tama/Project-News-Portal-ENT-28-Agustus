News Portal - Updated

Features:
- Admin panel with tabs: Articles and Admin management
- Admins can create/read/update/delete articles (title, content, banner image required for creation)
- Admins can create/delete other admin accounts (cannot delete self)
- Signup and login for users (users can read only)
- Content sanitized with Bleach (scripts removed; common tags allowed)
- Banner images are cropped to uniform thumbnails
- Logout confirmation and sticky hero-like navbar

Quickstart:
- Create venv: python -m venv .venv
- Activate: .venv\Scripts\activate  (Windows) or source .venv/bin/activate (Mac/Linux)
- Install: pip install -r requirements.txt
- Run: flask --app app run --debug
- Default admin: admin@example.com / admin123
