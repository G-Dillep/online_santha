# Online Santha

This is a Django-based web application for managing accounts, products, orders, and dashboards.

## Prerequisites
- Python 3.10+
- pip (Python package manager)
- (Optional) Virtual environment tool (venv or virtualenv)

## Setup Instructions

1. **Clone the repository**
   ```powershell
   git clone <repository-url>
   cd online_santha
   ```

2. **Create and activate a virtual environment (recommended)**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```powershell
   python manage.py migrate
   ```

5. **Create a superuser (admin account)**
   ```powershell
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```powershell
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure
- `accounts/` - User authentication and profile management
- `common/` - Common/shared functionality
- `dashboard/` - Dashboard views and logic
- `orders/` - Order management
- `products/` - Product management
- `media/` - Uploaded media files
- `static/` - Static files (CSS, JS, images)
- `templates/` - HTML templates
- `config/` - Project settings and configuration

## Notes
- Default database: SQLite (`db.sqlite3`)
- Static and media files are served locally in development.
- For production, configure static/media file hosting and update settings as needed.

## License
Specify your license here.
