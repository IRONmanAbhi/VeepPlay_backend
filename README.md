# VeePlay
## 1. Project Overview

### 1.1. Introduction
VeePlay Backend is a Flask-based REST API that powers a video streaming platform with authentication, account management, content delivery, and user watch history tracking.
It is designed to be modular, scalable, and secure, using **PostgreSQL** as the primary database (hosted via **Neon Console**) and **JWT-based authentication** for secure API access.
The API supports both user-facing features (e.g., login, account updates, streaming links) and admin operations (e.g., adding, updating, deleting content).
Deployed seamlessly on **Render** for production use, the backend integrates AWS S3 for media storage and presigned URL generation.

### 1.2. Features

- **User Authentication & Authorization**
    - Secure registration and login with **bcrypt** password hashing
    - JWT-based token authentication with configurable expiry
    - Password reset via email with time-limited token
- **Account Management**
    - Fetch and update user details
    - Manage profile pictures and account settings
- **Content Management**
    - Browse available content (movies, shows, seasons, episodes)
    - Admin-only CRUD for content items
    - AWS S3 presigned URL generation for secure media streaming
- **Watch History Tracking**
    - Save and retrieve watch history for each user
    - Track last watched episodes/movies
- **Security & Performance**
    - CORS-enabled for controlled frontend access
    - Production-ready deployment with **Gunicorn**
    - Environment-based configuration (development/production)

### 1.3. Tech Stack

- **Backend Framework:** Flask (Python)
- **Database:** PostgreSQL (Neon Console hosted)
- **Authentication:** Flask-JWT-Extended
- **ORM:** SQLAlchemy with Flask-SQLAlchemy
- **Password Hashing:** Flask-Bcrypt
- **Email Service:** Flask-Mail (SMTP-based)
- **Media Storage:** AWS S3 with presigned URL support
- **Image Handling:** Pillow (PIL) for profile pictures
- **Deployment:** Render with Gunicorn
- **Other Utilities:**
    - `python-dotenv` for environment variables
    - `Flask-CORS` for cross-origin requests
    - `itsdangerous` for secure token generation

---

## 2. License

Licensed under the Apache License 2.0 — see LICENSE for details.

---

## 3. Prerequisites

- Python 3.12+
- Neon PostgreSQL database ([console.neon.tech](https://console.neon.tech/))
- AWS S3 bucket & credentials
- Render for deployment

---

## 4. Installation

1. Clone repository:

```
git clone https://github.com/your-username/veeplay-backend.git
cd veeplay-backend
```

2. Create virtual environment & install dependencies:

```
python -m venv venv
source venv/bin/activate   # Mac/Linux  
venv\Scripts\activate      # Windows  

pip install -r requirements.txt
```

3. Create `.env` file in root:

```
SECRET_KEY=your-secret
JWT_SECRET_KEY=your-jwt-secret
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://user:password@host/db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_SSL=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_BUCKET_NAME=your-bucket
AWS_BUCKET_REGION=region
```

---

## 5. Database Setup

```
python create_tables.py
```

---

## 6. Running Locally

Development:

```
python run.py
```

Production with Gunicorn:

```
gunicorn "VeePlay:create_app()"
```

---

## 7. API Documentation

This API follows REST principles and uses **JSON** for request and response bodies. Authentication for protected routes is handled via **Bearer JWT tokens** in the `Authorization` header.

---

### 7.1. Authentication Routes

#### 7.1.1. POST /login
Authenticate a user and return a JWT token.
**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response (200):**

```json
{
  "access_token": "<jwt-token>",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Errors:**

* `401 Unauthorized` – Invalid credentials

---

#### 7.1.2. POST /register
Create a new user account.
**Request Body:**

```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (201):**

```json
{
  "message": "User registered successfully."
}
```

**Errors:**

* `400 Bad Request` – Email already exists

---

#### 7.1.3. POST /forgot-password
Send a password reset email with a secure token.
**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response (200):**

```json
{
  "message": "Password reset email sent."
}
```

---

#### 7.1.4. POST /reset-password
Reset the password using the token from the email.
**Request Body:**

```json
{
  "token": "<reset-token>",
  "password": "newsecurepassword"
}
```

**Response (200):**

```json
{
  "message": "Password updated successfully."
}
```

**Errors:**

* `400 Bad Request` – Invalid or expired token

---

### 7.2. Account Routes

#### 7.2.1. GET /account *(Protected)*
Fetch the logged-in user’s account details.
**Headers:**

```
Authorization: Bearer <jwt-token>
```

**Response (200):**

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "user@example.com",
  "profile_picture": "https://s3-bucket/profile_pics/default.jpg"
}
```

---

#### 7.2.2. PUT /account *(Protected)*
Update the logged-in user’s account details.
**Headers:**

```
Authorization: Bearer <jwt-token>
```

**Request Body (example):**

```json
{
  "name": "Updated Name",
  "profile_picture": "<base64-encoded-image>"
}
```

**Response (200):**

```json
{
  "message": "Account updated successfully."
}
```

---

### 7.3. Content Routes

#### 7.3.1. GET /content
Fetch all available content items.
**Response (200):**

```json
[
  {
    "id": 1,
    "title": "Example Show",
    "type": "series",
    "description": "A great show.",
    "poster_url": "https://s3-bucket/..."
  }
]
```

---

#### 7.3.2. GET /content/<id>
Fetch details for a specific content item by ID.
**Response (200):**

```json
{
  "id": 1,
  "title": "Example Show",
  "type": "series",
  "seasons": [
    {
      "season_number": 1,
      "episodes": [
        {
          "episode_number": 1,
          "title": "Episode One",
          "stream_url": "https://signed-url..."
        }
      ]
    }
  ]
}
```

---

#### 7.3.3. POST /content *(Admin, Protected)*
Create a new content item.
**Headers:**

```
Authorization: Bearer <admin-jwt-token>
```

**Request Body:**

```json
{
  "title": "New Movie",
  "type": "movie",
  "description": "Movie description",
  "poster": "<base64-image>"
}
```

**Response (201):**

```json
{
  "message": "Content created successfully."
}
```

---

#### 7.3.4. PUT /content/<id> *(Admin, Protected)*
Update a content item by ID.
**Headers:**

```
Authorization: Bearer <admin-jwt-token>
```

**Request Body:**

```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response (200):**

```json
{
  "message": "Content updated successfully."
}
```

---

#### 7.3.5. DELETE /content/<id> *(Admin, Protected)*
Delete a content item by ID.
**Headers:**

```
Authorization: Bearer <admin-jwt-token>
```

**Response (200):**

```json
{
  "message": "Content deleted successfully."
}
```

---

### 7.4. Watch History Routes

#### 7.4.1. GET /watch-history *(Protected)*
Fetch the logged-in user’s watch history.
**Headers:**

```
Authorization: Bearer <jwt-token>
```

**Response (200):**

```json
[
  {
    "content_id": 1,
    "title": "Example Show",
    "last_watched": "2025-08-11T14:32:00Z"
  }
]
```

---

#### 7.4.2. POST /watch-history *(Protected)*
Add or update watch history for the logged-in user.
**Headers:**

```
Authorization: Bearer <jwt-token>
```

**Request Body:**

```json
{
  "content_id": 1,
  "episode_id": 10,
  "position": 1200
}
```

**Response (200):**

```json
{
  "message": "Watch history updated."
}
```

---
## 8. Security Considerations

Security is a core focus in the design of this backend. This section explains the measures implemented to ensure data confidentiality, integrity, and availability.

---

### 8.1. JWT Expiry & Refresh Tokens

- **Access Tokens (JWT):**
  - All protected endpoints require a valid JSON Web Token (JWT) passed in the `Authorization` header as `Bearer <token>`.
  - Access tokens are **short-lived** (e.g., 15 minutes to 1 hour) to minimize the risk if compromised.
  - Payload contains essential claims such as `user_id`, `email`, and `exp` (expiration timestamp).

- **Refresh Tokens:**
  - A separate long-lived refresh token can be issued upon login (if implemented).
  - Refresh tokens are securely stored **server-side** or in an HTTP-only cookie to prevent XSS attacks.
  - Clients can use the refresh token to request a new access token without requiring the user to re-login.
  
- **Best Practices:**
  - Do not store JWTs in `localStorage` for sensitive applications — prefer **HTTP-only cookies** or secure storage mechanisms.
  - Always validate the token’s `exp` and signature before processing requests.

---

### 8.2. Password Hashing with bcrypt

- **Why bcrypt?**
  - bcrypt is a strong hashing algorithm designed specifically for passwords, offering resistance against brute-force and rainbow table attacks.

- **Implementation Details:**
  - Plaintext passwords are **never stored** in the database.
  - Before saving, passwords are hashed with a **random salt** using bcrypt (default work factor: `12`).
  - On login, bcrypt's `check_password_hash` function is used to compare the provided password against the stored hash.

- **Security Notes:**
  - Increasing the work factor (cost) over time enhances security as hardware performance improves.
  - Even if the database is compromised, raw passwords remain undisclosed due to hashing.

---

### 8.3. CORS Configuration

- **Purpose:**
  - Cross-Origin Resource Sharing (CORS) is configured to control which domains can access the API from browsers.

- **Configuration:**
  - By default, only whitelisted frontend domains (e.g., `https://your-frontend.com`) are allowed to make requests.
  - Allowed HTTP methods: `GET`, `POST`, `PUT`, `DELETE`, and `OPTIONS`.
  - Allowed headers: `Content-Type`, `Authorization`.
  - Preflight requests (`OPTIONS`) are handled automatically by the CORS middleware.

- **Security Notes:**
  - Avoid using `Access-Control-Allow-Origin: *` in production.
  - Keep the allowed origins list minimal to prevent misuse of the API from untrusted domains.

---

## 9. Contributing

### 9.1. Fork & Branch Workflow

We welcome contributions from the community to improve and expand the project. To maintain a clean and organized development process, we follow the **Fork & Branch** workflow:

1. **Fork the Repository**

   * Click the **Fork** button on the repository page to create your own copy of the project under your GitHub account.

2. **Clone Your Fork**

   * Clone your fork locally using:
     `git clone https://github.com/<your-username>/<repository-name>.git`

3. **Create a New Branch**

   * Always create a new branch for your changes instead of committing directly to the `main` branch.
   * Use a descriptive branch name, for example:
     `feature/add-user-profile` or `fix/auth-bug`.
   * Command:
     `git checkout -b feature/your-feature-name`

4. **Make Your Changes**

   * Implement the desired features or bug fixes.
   * Follow the existing code style and conventions.

5. **Commit Your Changes**

   * Write clear and concise commit messages.
   * Example:
     `"fix: corrected JWT token parsing in account route"`

6. **Push to Your Fork**

   * Push your branch to your forked repository:
     `git push origin feature/your-feature-name`

7. **Open a Pull Request (PR)**

   * Go to the original repository and click **New Pull Request**.
   * Select your branch and submit the PR for review.

---

### 9.2. Pull Request Guidelines

To ensure smooth collaboration and maintain high code quality, please follow these guidelines when submitting pull requests:

* **Code Quality:**

  * Ensure your code passes all linting and formatting rules.
  * Avoid introducing unused variables, imports, or functions.

* **Testing:**

  * Test your changes locally to confirm they work as intended.
  * If applicable, add unit tests for new functionality.

* **Documentation:**

  * Update README or API documentation if your changes affect usage or add new features.

* **PR Description:**

  * Provide a detailed explanation of the changes, including the problem solved or feature added.
  * Mention any related issues by referencing their number (e.g., `Fixes #42`).

* **Small & Focused Changes:**

  * Avoid large, unrelated changes in a single PR. Keep contributions focused on one feature or fix at a time.

* **Review Process:**

  * Be responsive to feedback from maintainers and reviewers.
  * Make necessary updates to your branch based on review comments.

This structured process helps keep the codebase maintainable, reduces merge conflicts, and ensures high-quality contributions from all collaborators.
