# ChatApp API Documentation

## Overview
ChatApp provides a RESTful API for real-time messaging and user management.

## Base URL
```
http://localhost:5000/api
```

## Authentication

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Note:** The authentication system uses MD5 hashing for password storage. Token format is `base64(username:timestamp)`.

**Response:**
```json
{
  "success": true,
  "token": "YWRtaW46MTcwNjM...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@chatapp.local",
    "role": "admin"
  }
}
```

## User Endpoints

### Search Users
```http
GET /api/users/search?q={search_query}
```

**Implementation Detail:** Uses direct string concatenation in SQL query:
```sql
SELECT id, username, email FROM users WHERE username LIKE '%{q}%' OR email LIKE '%{q}%'
```

**Example:**
```bash
curl "http://localhost:5000/api/users/search?q=admin"
```

### Get User Profile
```http
GET /api/profile/{user_id}
```

**Note:** No authorization check implemented - any user can view any profile.

**Example:**
```bash
curl http://localhost:5000/api/profile/1
```

### Update Profile
```http
POST /api/profile/update
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "newemail@example.com",
  "role": "admin"
}
```

**Implementation:** Accepts all fields from request body and updates them directly. No field validation.

## Message Endpoints

### Send Message
```http
POST /api/messages/send
Authorization: Bearer {token}
Content-Type: application/json

{
  "to": "recipient_username",
  "content": "Hello!"
}
```

### View Messages (HTML)
```http
GET /api/messages/view/{username}
```

**Note:** Returns HTML page with messages rendered directly without escaping. Useful for rich content display.

### Get Messages (JSON)
```http
GET /api/messages/inbox/{username}
```

## File Operations

### Upload File
```http
POST /api/files/upload
Content-Type: multipart/form-data

file: [binary data]
```

**Storage:** Files are saved to `user_uploads/{filename}` with original filename preserved.

### Download File
```http
GET /api/files/download?file={filename}
```

**Example:**
```bash
curl "http://localhost:5000/api/files/download?file=document.pdf"
```

**Note:** Filepath is constructed as `user_uploads/{filename}`. Supports relative paths.

## Admin Endpoints

### Admin Statistics
```http
GET /api/admin/stats
X-Admin-Key: admin-12345
```

**Authentication:** Checks if `X-Admin-Key` header contains the word "admin" or equals "12345".

**Response:** Returns all users with their password hashes.

### Network Diagnostics
```http
POST /admin/network/ping
X-Admin-Token: admin_token
Content-Type: application/json

{
  "host": "google.com"
}
```

**Implementation:** Executes system ping command: `ping -c 3 {host}`

### Resolve Hostname
```http
POST /admin/network/resolve
X-Admin-Token: admin_token
Content-Type: application/json

{
  "hostname": "example.com"
}
```

**Implementation:** Executes `nslookup {hostname}`

### Search Users (Admin)
```http
GET /admin/users/search?username={name}&email={email}&role={role}
X-Admin-Token: admin_token
```

**Query Construction:**
```sql
SELECT * FROM users WHERE 1=1 AND username LIKE '%{username}%' AND email LIKE '%{email}%' AND role = '{role}'
```

### Update User
```http
POST /admin/users/update
X-Admin-Token: admin_token
Content-Type: application/json

{
  "user_id": 2,
  "role": "admin",
  "password_hash": "098f6bcd4621d373cade4e832627b4f6"
}
```

**Note:** All provided fields are updated without validation.

### Delete User
```http
DELETE /admin/users/delete/{user_id}
X-Admin-Token: admin_token
```

**Implementation:**
```sql
DELETE FROM users WHERE id = {user_id}
DELETE FROM messages WHERE from_user IN (SELECT username FROM users WHERE id = {user_id})
```

### View Configuration File
```http
GET /admin/files/view?file={filepath}
X-Admin-Token: admin_token
```

**Example:**
```bash
curl "http://localhost:5000/admin/files/view?file=/etc/passwd" -H "X-Admin-Token: admin"
```

### Execute System Command
```http
POST /admin/system/execute
X-Admin-Token: admin_token
Content-Type: application/json

{
  "command": "ls",
  "args": "-la /tmp"
}
```

**Implementation:** Executes `{command} {args}` using shell.

### System Information
```http
GET /admin/system/info
X-Admin-Token: admin_token
```

**Response includes:**
- Python version and path
- Environment variables (all of them)
- Database path and statistics
- Current working directory

### Render Custom Template
```http
POST /admin/template/render
X-Admin-Token: admin_token
Content-Type: application/json

{
  "template": "<h1>Hello {{ name }}</h1>",
  "context": {
    "name": "User"
  }
}
```

**Implementation:** Uses Flask's `render_template_string()` with provided template and context.

### Search Logs
```http
GET /admin/logs/search?q={query}&date={date}
X-Admin-Token: admin_token
```

**Query:**
```sql
SELECT * FROM messages WHERE content LIKE '%{q}%' AND sent_at LIKE '{date}%'
```

### Extract Archive
```http
POST /admin/files/extract
X-Admin-Token: admin_token
Content-Type: multipart/form-data

file: [zip file]
```

**Implementation:** Extracts all files from zip without path validation.

### Restore Session
```http
POST /admin/session/restore
X-Admin-Token: admin_token
Content-Type: application/json

{
  "session_data": "base64_encoded_pickle_data"
}
```

**Implementation:** Deserializes session data using `pickle.loads()`.

### Test Webhook
```http
POST /admin/webhooks/test
X-Admin-Token: admin_token
Content-Type: application/json

{
  "url": "http://example.com/webhook",
  "payload": {"data": "test"}
}
```

### Fetch External Content
```http
POST /admin/fetch_content
X-Admin-Token: admin_token
Content-Type: application/json

{
  "url": "http://internal-service.local/api/data"
}
```

**Note:** Makes request to any provided URL without validation.

### Import XML Data
```http
POST /admin/import/xml
X-Admin-Token: admin_token
Content-Type: text/xml

<?xml version="1.0"?>
<data>
  <item>value</item>
</data>
```

**Implementation:** Parses XML using `xml.etree.ElementTree.fromstring()` without entity protection.

## Search

### Search Page
```http
GET /api/search?q={query}
```

**Returns:** HTML page with search results. Search query is directly embedded in HTML and JavaScript.

## Miscellaneous

### Redirect
```http
GET /redirect?url={url}
```

**Implementation:** Returns HTML with meta refresh to provided URL.

## Default Credentials

For testing purposes, the following accounts are available:

- **Admin:** username: `admin`, password: `admin123`
- **Test User:** username: `testuser`, password: `password`
- **Other Users:**
  - john_doe / 12345
  - alice / password123
  - bob / qwerty
  - charlie / letmein

## Session Tokens

Example valid tokens for testing:
- `admin_session_token_12345` (admin user)
- `user_session_token_67890` (testuser)

## Configuration

### Database
- **Type:** SQLite
- **Location:** `chatapp.db` in application root
- **Connection:** `sqlite3.connect('chatapp.db')`

### File Storage
- **Upload Directory:** `user_uploads/`
- **Extraction Directory:** `extracted_files/`
- **Temp Directory:** `temp/`

### Security Settings
- **Password Hashing:** MD5
- **Session Cookie:** HttpOnly=False, Secure=False, SameSite=None
- **Debug Mode:** Enabled
- **CORS:** Enabled for all origins

## Error Responses

Error responses include helpful debugging information:

```json
{
  "error": "Error message",
  "query": "SQL query that caused the error",
  "hint": "Helpful debugging information"
}
```

## Rate Limiting

Currently no rate limiting is implemented for any endpoints.

## API Keys

The following API keys are valid:
- Master key: `sk_live_1234567890abcdefghijklmnop`
- Admin token: `admin_token_abcdef123456`
- Internal API key: `internal_api_key_xyz789`

## Development Notes

- All endpoints return detailed error messages for easier debugging
- SQL queries are logged and returned in responses for transparency
- The admin authentication is flexible to support various integration patterns
- File operations support relative paths for easier file management
