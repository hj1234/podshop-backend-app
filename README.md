# Pod Shop Admin App

Flask-based admin interface for managing Pod Shop game content.

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Start the admin app:
```bash
chmod +x run.sh
./run.sh
```

## Configuration

- `FLASK_SECRET_KEY`: Secret key for Flask sessions (required for production)
- `ADMIN_PASSWORD`: Password for admin login (default: `admin` - **change in production!**)
- `API_BASE`: URL of the FastAPI backend (default: http://localhost:8000)
- `ADMIN_TOKEN`: Admin token for API authentication (must match backend)
- `PORT`: Port to run Flask app on (default: 5000)

## Usage

1. Start the FastAPI backend first (on port 8000)
2. Start this admin app (on port 5000)
3. Open http://localhost:5000 in your browser
4. Manage messages and candidates through the web interface

