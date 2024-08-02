## Install process

1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt --timeout 60`
4. Setup config file

## default_data.py

```
python default_data.py
```

For add the default user admin.

## Routes

### Login

`http://localhost:5000/api/auth/login`

- Only active user can login.

Request Body:

```json
{
  "username": "admin",
  "password": "adminpassword"
}
```

Response Body:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMjUyMjM1NiwianRpIjoiMWIwMWQzZmUtMjc5OC00MTAxLWFhNzktYjM0YmI4NzU0MjFjIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MSwicm9sZSI6IkFETUlOIn0sIm5iZiI6MTcyMjUyMjM1NiwiY3NyZiI6IjljMmRiNWNkLTM0ZTEtNDI0MC04YjdmLWM1ODk0MTM4ZTRiZSIsImV4cCI6MTcyMjUyMzI1Nn0.xnJXlibyBWUSMW21lJe-_547a8rkrXCXwDV3wJvzgjk"
}
```

### Register

`http://localhost:5000/api/auth/register`
**Request Method: POST**

Request Body:

```json
{
  "username": "user1",
  "first_name": "user1",
  "last_name": "user1",
  "email": "user1@example.com",
  "role": "ADMIN",
  "password": "user1"
}
```

Response Body:

```json
{
  "msg": "User registered successfully."
}
```

### Update user

- An admin updates their own information.
- An admin updates a non-admin user.

**Request Method: PUT**

`http://localhost:5000/api/user/user2`
Request Body:

```json
{
  "first_name": "user2_update",
  "last_name": "user2_update"
}
```

Request Header:

**Authorization:** **Bearer Access-token**

Demo:

`Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMjU3NjIxNCwianRpIjoiNjE4MzM5MTItNDIwNS00YTAxLWE1ZTEtZjZlYjIzNjBmYzUwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MywidXNlcm5hbWUiOiJ1c2VyMiIsInJvbGUiOiJBRE1JTiJ9LCJuYmYiOjE3MjI1NzYyMTQsImNzcmYiOiJlZGI2Yzc1Yi05Njg0LTQ5ZWMtYTNjOS05MTU2MjY1ODFlNjAiLCJleHAiOjE3MjI1NzcxMTR9.WUkPw2O_zZrL7n3KydYNHKxsQ2X6NWvtx8qIgIx8hbY`

Response Body:

```json
{
  "msg": "User details updated."
}
```

### Delete user

- An admin can delete only users.
- An admin can't delete other admin or ownself.

**Request Method: DELETE**

`http://localhost:5000/api/user/user3`

Request Header:

**Authorization:** **Bearer Access-token**

Demo:

`Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMjU3NjIxNCwianRpIjoiNjE4MzM5MTItNDIwNS00YTAxLWE1ZTEtZjZlYjIzNjBmYzUwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MywidXNlcm5hbWUiOiJ1c2VyMiIsInJvbGUiOiJBRE1JTiJ9LCJuYmYiOjE3MjI1NzYyMTQsImNzcmYiOiJlZGI2Yzc1Yi05Njg0LTQ5ZWMtYTNjOS05MTU2MjY1ODFlNjAiLCJleHAiOjE3MjI1NzcxMTR9.WUkPw2O_zZrL7n3KydYNHKxsQ2X6NWvtx8qIgIx8hbY`

Response Body:

```json
{
  "msg": "User deleted."
}
```
