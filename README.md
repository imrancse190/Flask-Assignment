# Flask User Management API

## Overview

This project is a Flask-based API for managing user accounts with JWT authentication, SQLAlchemy for ORM, and Flask-Restx for building RESTful APIs. The application supports user registration, login, password reset, and user management features.

## Installation

Follow these steps to set up the project on your local machine:

1. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the configuration file:**

   - Copy `config.demo.txt` to `.env` and fill in your configuration values. Ensure you set up all necessary environment variables.

5. **Initialize the database:**

   ```bash
   python default_data.py
   ```

   This script sets up the default admin user and initializes the database schema.

## Configuration

The configuration is loaded from environment variables. Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://username:password@localhost:5433/database_name
JWT_SECRET_KEY=your_jwt_secret_key
MAIL_SERVER=smtp.yourmailserver.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
SECURITY_PASSWORD_SALT=your_password_salt
```

- **SECRET_KEY**: A secret key used for securing session data.
- **DATABASE_URL**: URL for connecting to the PostgreSQL database.
- **JWT_SECRET_KEY**: Secret key for encoding and decoding JWT tokens.
- **MAIL_SERVER**: SMTP server for sending emails.
- **MAIL_PORT**: Port for the SMTP server.
- **MAIL_USE_TLS**: Whether to use TLS for the SMTP connection.
- **MAIL_USERNAME**: Email address used for sending emails.
- **MAIL_PASSWORD**: Password for the email account.
- **SECURITY_PASSWORD_SALT**: Salt for password hashing.

## API Endpoints

### User Registration

**POST** `/api/user/register`

**Request Body:**

```json
{
  "username": "user1",
  "first_name": "User",
  "last_name": "One",
  "email": "user1@example.com",
  "password": "password123"
}
```

**Response:**

```json
{
  "msg": "User registered successfully."
}
```

### User Login

**POST** `/api/user/login`

**Request Body:**

```json
{
  "username": "user1",
  "password": "password123"
}
```

**Response:**

```json
{
  "access_token": "your_jwt_access_token"
}
```

### Request Password Reset

**POST** `/api/user/forget_password`

**Request Body:**

```json
{
  "username": "user1",
  "email": "user1@example.com"
}
```

**Response:**

```json
{
  "msg": "Token generated successfully.",
  "token": "reset_token"
}
```

### Reset Password

**POST** `/api/user/reset_password`

**Request Body:**

```json
{
  "token": "reset_token",
  "new_password": "new_password123"
}
```

**Response:**

```json
{
  "msg": "Password has been reset."
}
```

### Get User Details

**GET** `/api/user/<username>`

**Headers:**

```http
Authorization: Bearer your_jwt_access_token
```

**Response:**

```json
{
  "id": 1,
  "username": "user1",
  "first_name": "User",
  "last_name": "One",
  "email": "user1@example.com",
  "role": "USER",
  "active": true
}
```

### Update User Details

**PUT** `/api/user/<username>`

**Headers:**

```http
Authorization: Bearer your_jwt_access_token
```

**Request Body:**

```json
{
  "first_name": "UpdatedName"
}
```

**Response:**

```json
{
  "msg": "User details updated."
}
```

### Delete User

**DELETE** `/api/user/<username>`

**Headers:**

```http
Authorization: Bearer your_jwt_access_token
```

**Response:**

```json
{
  "msg": "User deleted."
}
```

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.
