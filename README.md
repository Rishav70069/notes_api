# 📝 Notes API

A robust, secure RESTful API for managing personal notes, built with FastAPI and PostgreSQL. This API provides a complete set of features for user authentication, email verification, and note organization.

## ✨ Features

- **User Management**
  - 🔐 **Secure Registration**: Create accounts with hashed passwords.
  - 📧 **Email Verification**: Mandatory OTP (One-Time Password) verification via email.
  - 🔑 **Password Recovery**: "Forgot Password" flow with OTP-based resets.
  - 👤 **Profile Management**: Ability to delete user accounts.

- **Notes Management**
  - 📝 **Full CRUD**: Create, Read, Update, and Delete your personal notes.
  - 🔍 **Advanced Search**: Search notes by title or content.
  - 📊 **Organization**:
    - Pagination (limit/skip).
    - Sorting by title or creation date.
    - Marking notes as **Pinned**, **Favorite**, or **Archived**.
  - 🔒 **Ownership Security**: Users can only access, modify, or delete their own notes.

- **Authentication & Security**
  - 🛡️ **JWT Authentication**: Secure access tokens using OAuth2.
  - ⏱️ **Token Expiration**: Configurable access token lifetime.
  - ⚙️ **Environment-based Config**: Sensitive data managed via `.env` files.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Language**: Python 3.10+
- **Database**: PostgreSQL
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Validation**: [Pydantic](https://docs.pydantic.dev/)
- **Email Service**: Resend (integrated for OTP delivery)
- **Auth**: OAuth2 + JWT

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- PostgreSQL instance
- A Resend API key for email functionality

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rishav70069/notes_api.git
   cd notes-api
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the root directory and fill in your credentials:

```env
DATABASE=postgresql
DATABASE_DRIVER=psycopg2
DATABASE_USERNAME=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_NAME=notes_db

SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

RESEND_API_KEY=re_your_resend_api_key
```

### Database Setup

Initialize the database using Alembic:

```bash
alembic upgrade head
```

### Running the Application

Start the server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
You can access the interactive Swagger documentation at `http://127.0.0.1:8000/docs`.

## 📖 API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/login` | Authenticate and get JWT token | No |

### Users
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/users/create` | Register a new user (triggers OTP email) | No |
| `POST` | `/users/verify-email` | Verify account using OTP | No |
| `POST` | `/users/resend-otp` | Request a new verification OTP | No |
| `POST` | `/users/forgot-password` | Request password reset OTP | No |
| `POST` | `/users/reset-password` | Reset password using OTP | No |
| `DELETE` | `/users/{id}` | Delete your account | Yes |

### Notes
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/notes/` | Create a new note | Yes |
| `GET` | `/notes/` | List notes (search, sort, paginate) | Yes |
| `GET` | `/notes/{id}` | Get a specific note | Yes |
| `PATCH` | `/notes/{id}` | Update note details/status | Yes |
| `DELETE` | `/notes/{id}` | Delete a note | Yes |

## 📂 Project Structure

```text
notes_api/
├── app/
│   ├── routers/      # API route handlers (auth, users, notes)
│   ├── schemas/      # Pydantic models for request/response validation
│   ├── main.py       # Application entry point
│   ├── models.py     # SQLAlchemy database models
│   ├── database.py   # DB connection and session management
│   ├── config.py     # Configuration and environment settings
│   ├── oauth2.py     # JWT and OAuth2 logic
│   └── utility.py    # Helper functions (hashing, email)
├── alembic/          # Database migration scripts
├── .env              # Environment variables (local)
└── README.md         # Project documentation
```
