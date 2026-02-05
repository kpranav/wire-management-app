# API Documentation

## Base URL

```
Development: http://localhost:8000
Dev Environment: http://YOUR-EC2-IP:8001
QA Environment: http://YOUR-EC2-IP:8002
UAT Environment: http://YOUR-EC2-IP:8003
Production: http://YOUR-EC2-IP:8000
```

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```bash
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 201 Created
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00Z"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Wire Transfers

#### Create Wire
```http
POST /api/wires
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "sender_name": "John Doe",
  "recipient_name": "Jane Smith",
  "amount": 1000.00,
  "currency": "USD"
}

Response: 201 Created
{
  "id": 1,
  "sender_name": "John Doe",
  "recipient_name": "Jane Smith",
  "amount": 1000.00,
  "currency": "USD",
  "status": "pending",
  "reference_number": "WIRE-ABC123XYZ",
  "created_by": 1,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": null
}
```

#### List Wires
```http
GET /api/wires?page=1&page_size=20&status=pending
Authorization: Bearer <access_token>

Response: 200 OK
{
  "wires": [
    {
      "id": 1,
      "sender_name": "John Doe",
      "recipient_name": "Jane Smith",
      "amount": 1000.00,
      "currency": "USD",
      "status": "pending",
      "reference_number": "WIRE-ABC123XYZ",
      "created_by": 1,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": null
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "cached": false
}
```

#### Get Wire by ID
```http
GET /api/wires/1
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": 1,
  "sender_name": "John Doe",
  "recipient_name": "Jane Smith",
  "amount": 1000.00,
  "currency": "USD",
  "status": "pending",
  "reference_number": "WIRE-ABC123XYZ",
  "created_by": 1,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": null
}
```

#### Update Wire
```http
PUT /api/wires/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount": 1500.00,
  "status": "processing"
}

Response: 200 OK
{
  "id": 1,
  "sender_name": "John Doe",
  "recipient_name": "Jane Smith",
  "amount": 1500.00,
  "currency": "USD",
  "status": "processing",
  "reference_number": "WIRE-ABC123XYZ",
  "created_by": 1,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:05:00Z"
}
```

#### Delete Wire
```http
DELETE /api/wires/1
Authorization: Bearer <access_token>

Response: 204 No Content
```

### WebSocket

#### Connect to WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Wire update:', data);
  // {
  //   "type": "wire_update",
  //   "wire_id": 1,
  //   "status": "completed",
  //   "user_id": 1,
  //   "timestamp": 1234567890
  // }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Error description",
  "status_code": 400,
  "timestamp": "2024-01-01T10:00:00Z",
  "path": "/api/wires/999"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource doesn't exist
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

- **Limit**: 100 requests per minute per endpoint per user
- **Response**: 429 Too Many Requests
- **Reset**: After 60 seconds

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1, min: 1)
- `page_size`: Items per page (default: 20, min: 1, max: 100)

**Response includes:**
- `total`: Total number of items
- `page`: Current page number
- `page_size`: Items per page

## Filtering

Wire list supports filtering:

**Query Parameters:**
- `status`: Filter by wire status (pending, processing, completed, failed)

Example:
```http
GET /api/wires?status=completed&page=1&page_size=20
```

## Testing the API

### Using curl

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.access_token')

# Create wire
curl -X POST http://localhost:8000/api/wires \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"sender_name":"John","recipient_name":"Jane","amount":1000,"currency":"USD"}'

# List wires
curl http://localhost:8000/api/wires \
  -H "Authorization: Bearer $TOKEN"
```

### Using the Interactive Docs

1. Go to `http://localhost:8000/docs`
2. Click on `/api/auth/login`
3. Click "Try it out"
4. Fill in credentials and execute
5. Copy the `access_token` from response
6. Click "Authorize" button at top of page
7. Paste token and click "Authorize"
8. Now you can test all protected endpoints

## WebSocket Testing

Using browser console:

```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws');

// Listen for updates
ws.onmessage = (event) => {
  console.log('Received:', JSON.parse(event.data));
};

// Send message
ws.send(JSON.stringify({ type: 'ping' }));
```

## API Versioning

Current version: `v1.0.0`

Future versions will be prefixed:
- `v1`: `/api/v1/wires`
- `v2`: `/api/v2/wires`
