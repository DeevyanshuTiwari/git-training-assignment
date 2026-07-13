# CircleUp - Connect, Collaborate, Grow

CircleUp is a modern, full-stack web application designed to help people discover, join, and manage activities in their local area. Whether you're looking to start a book club, find a hiking group, or just meet people with similar interests, CircleUp provides a sleek and intuitive platform to bring communities together.

## 🚀 Key Features

*   **User Authentication:** Secure sign-up and login functionality.
*   **Activity Discovery:** Browse and search for activities happening around you.
*   **Activity Management:** Create, edit, and delete your own activities.
*   **Participation:** Join activities created by others or leave if you can no longer attend.
*   **User Dashboard:** Keep track of activities you are organizing or participating in.
*   **Responsive UI:** A modern, glassmorphism-inspired design with smooth animations that works well on all devices.

## 🛠️ Technology Stack

### Backend
*   **Framework:** [FastAPI](https://fastapi.tiangolo.com/) - A modern, fast web framework for building APIs with Python.
*   **Database:** PostgreSQL (with `psycopg2`).
*   **ORM:** SQLAlchemy - For database interactions.
*   **Migrations:** Alembic - For handling database schema changes.
*   **Authentication:** JWT-based authentication using `python-jose` and `passlib` for password hashing.
*   **Testing:** `pytest` and `pytest-cov` for testing the API.

### Frontend
*   **Structure & Style:** HTML5, CSS3 (Custom properties, Flexbox/Grid, Glassmorphism).
*   **Interactivity:** Vanilla JavaScript.
*   **Icons:** [Phosphor Icons](https://phosphoricons.com/) - Lightweight and modern SVG icons.

## 📁 Project Structure

```text
Capstone_CircleUp/
├── backend/                  # FastAPI Application
│   ├── alembic/              # Database migration scripts
│   ├── app/                  # Main backend logic
│   │   ├── core/             # Configuration and security
│   │   ├── db/               # Database setup
│   │   ├── enums/            # Enumerations
│   │   ├── models/           # SQLAlchemy models
│   │   ├── repositories/     # Database queries/operations
│   │   ├── routes/           # API endpoints (auth, user, activity, participation)
│   │   ├── schemas/          # Pydantic models for request/response validation
│   │   ├── services/         # Business logic
│   │   └── main.py           # Application entry point
│   ├── tests/                # Pytest suite
│   ├── requirements.txt      # Python dependencies
│   └── alembic.ini           # Alembic configuration
└── frontend/                 # Vanilla JS/HTML/CSS Application
    ├── assets/               # CSS, JS, Images
    ├── pages/                # Application views (dashboard, profile, etc.)
    └── index.html            # Landing page
```

## ⚙️ Setup and Installation

### Prerequisites
*   Python 3.9+
*   PostgreSQL database
*   Live Server (or any static file server) for the frontend

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv myvenv
    # On Windows:
    myvenv\Scripts\activate
    # On macOS/Linux:
    source myvenv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the `backend` directory based on `.env.example` (if present) or add the following required variables:
    ```env
    DATABASE_URL=postgresql://user:password@localhost/circleup
    SECRET_KEY=your_super_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

5.  **Apply Database Migrations:**
    ```bash
    alembic upgrade head
    ```

6.  **Run the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The backend API will be running at `http://127.0.0.1:8000`. You can access the automatic API documentation at `http://127.0.0.1:8000/docs`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
2.  **Serve the files:**
    Since it's a Vanilla HTML/CSS/JS app, you can simply open `index.html` in your browser. For a better development experience (to handle CORS and routing correctly), use a local development server like VS Code's "Live Server" extension, or Python's built-in HTTP server:
    ```bash
    python -m http.server 5500
    ```
    Then visit `http://127.0.0.1:5500/index.html`.

## 🧪 Testing

To run the backend test suite:
1. Ensure your virtual environment is activated and you're in the `backend/` directory.
2. Run pytest:
    ```bash
    pytest tests/
    ```
3. To view test coverage:
    ```bash
    pytest --cov=app tests/
    ```
