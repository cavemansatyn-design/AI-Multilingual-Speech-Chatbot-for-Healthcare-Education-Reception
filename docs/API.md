# API Reference

Base URL (local): `http://localhost:8000`

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Authentication

### Register

```http
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "full_name": "optional",
  "role": "user"
}
```

### Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=...&password=...
```

Returns: `{ "access_token": "...", "token_type": "bearer" }`

Use the token in protected routes:

```http
Authorization: Bearer <access_token>
```

## Chat

### Text chat

```http
POST /chat/text
Content-Type: application/x-www-form-urlencoded

text=...&language=en&state_json=... (optional)
```

Returns: `reply`, `reply_en`, `report_text`, `structured`, `state`, `audio_base64`.

### Audio chat

```http
POST /chat/audio
Content-Type: multipart/form-data

audio=<file>&language=en&state_json=... (optional)
```

Returns: same as text, plus `transcribed`.

## Reports

Require **doctor** or **admin** role.

```http
GET /report/{patient_id}
Authorization: Bearer <token>
```

```http
GET /report/{patient_id}/history?limit=10
Authorization: Bearer <token>
```
