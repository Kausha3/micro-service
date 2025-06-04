# 📡 API Documentation

Comprehensive API documentation for the Lead-to-Lease Chat Concierge microservice with AI-powered conversation capabilities.

## 🔗 Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## 📋 Interactive Documentation

- **Swagger UI**: `/docs` - Interactive API documentation with request/response examples
- **ReDoc**: `/redoc` - Alternative documentation with detailed schemas
- **OpenAPI Spec**: `/openapi.json` - Machine-readable API specification

## 🤖 AI Features

The API leverages OpenAI GPT models for intelligent conversation processing:

### Natural Language Understanding

- **Intent Detection**: Automatically identifies user goals (searching, booking, inquiring)
- **Entity Extraction**: Extracts names, emails, phone numbers, dates, and preferences
- **Context Awareness**: Maintains conversation history and context across messages
- **Flexible Input**: Understands natural language variations and colloquialisms

### Intelligent Response Generation

- **Contextual Responses**: AI generates responses based on conversation history and available inventory
- **Personalization**: Tailors responses to user preferences and requirements
- **Graceful Fallback**: Provides helpful responses when AI services are unavailable
- **Multi-turn Conversations**: Maintains coherent dialogue across multiple exchanges

### Configuration

```bash
# Environment variables for AI configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4, gpt-4-turbo-preview
```

## 🛡 Authentication

Currently, the API does not require authentication for public endpoints. In production, consider implementing:

- API key authentication for external integrations
- Rate limiting for abuse prevention
- CORS configuration for frontend security

## 📊 Endpoints Overview

| Endpoint | Method | Description | Tags |
|----------|--------|-------------|------|
| `/` | GET | Health check and API information | Health |
| `/chat` | POST | AI-powered conversation processing | Chat |
| `/inventory` | GET | Apartment unit availability | Inventory |
| `/sessions/{id}` | GET | Conversation session details | Sessions |

## 🔍 Detailed Endpoint Documentation

### Health Check

```http
GET /
```

**Description**: Returns API status, version, and available features.

**Response**: `200 OK`

```json
{
  "message": "Lead-to-Lease Chat Concierge API",
  "status": "healthy",
  "version": "1.0.0",
  "description": "AI-powered chat microservice for apartment leasing",
  "features": [
    "AI-powered natural language conversation",
    "Automated lead qualification and data collection",
    "Real-time apartment inventory management",
    "Professional email notifications with retry logic",
    "Multi-unit booking support",
    "Session persistence and conversation history"
  ],
  "endpoints": {
    "/": "API health check and information",
    "/chat": "AI-powered conversation processing",
    "/inventory": "Apartment unit availability",
    "/sessions/{id}": "Conversation session details"
  }
}
```

### Chat Processing

```http
POST /chat
```

**Description**: Processes user messages through AI-powered conversation flow.

**Request Body**:

```json
{
  "message": "Hi, I'm looking for a 2-bedroom apartment",
  "session_id": "optional-session-id"
}
```

**Response**: `200 OK`

```json
{
  "response": "Hello! I'd be happy to help you find a 2-bedroom apartment. To get started, may I have your name?",
  "session_id": "generated-or-provided-session-id",
  "state": "COLLECTING_NAME",
  "collected_data": {
    "bedroom_preference": "2"
  },
  "available_units": [],
  "booking_confirmed": false
}
```

**Error Responses**:

- `400 Bad Request`: Invalid message format
- `500 Internal Server Error`: AI service unavailable

### Inventory Management

```http
GET /inventory
```

**Description**: Returns current apartment unit availability.

**Query Parameters**:

- `bedrooms` (optional): Filter by bedroom count (0-4)
- `available_only` (optional): Show only available units (default: true)

**Response**: `200 OK`

```json
{
  "units": [
    {
      "unit_id": "A101",
      "bedrooms": 2,
      "bathrooms": 2,
      "square_feet": 950,
      "rent": 2400,
      "available": true,
      "floor": 1,
      "amenities": ["In-unit laundry", "Balcony", "Dishwasher"]
    }
  ],
  "total_units": 15,
  "available_units": 13,
  "occupancy_rate": "87%"
}
```

### Session Details

```http
GET /sessions/{session_id}
```

**Description**: Retrieves conversation history and session details.

**Path Parameters**:

- `session_id`: Unique session identifier

**Response**: `200 OK`

```json
{
  "session_id": "session-123",
  "created_at": "2024-01-15T10:30:00Z",
  "last_activity": "2024-01-15T10:45:00Z",
  "state": "BOOKING_CONFIRMED",
  "collected_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "(555) 123-4567",
    "move_in_date": "2024-02-01",
    "bedroom_preference": "2"
  },
  "conversation_history": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "type": "user",
      "message": "Hi, I'm looking for a 2-bedroom apartment"
    },
    {
      "timestamp": "2024-01-15T10:30:05Z",
      "type": "assistant",
      "message": "Hello! I'd be happy to help you find a 2-bedroom apartment..."
    }
  ],
  "booked_units": [
    {
      "unit_id": "A101",
      "tour_date": "2024-01-16",
      "tour_time": "2:00 PM"
    }
  ]
}
```

**Error Responses**:

- `404 Not Found`: Session not found

## 📝 Data Models

### ChatMessage

```json
{
  "message": "string (required, 1-1000 characters)",
  "session_id": "string (optional, UUID format)"
}
```

### ChatResponse

```json
{
  "response": "string",
  "session_id": "string",
  "state": "enum (GREETING, COLLECTING_NAME, COLLECTING_EMAIL, etc.)",
  "collected_data": "object",
  "available_units": "array",
  "booking_confirmed": "boolean"
}
```

### Unit

```json
{
  "unit_id": "string",
  "bedrooms": "integer (0-4)",
  "bathrooms": "number",
  "square_feet": "integer",
  "rent": "integer",
  "available": "boolean",
  "floor": "integer",
  "amenities": "array of strings"
}
```

## 🚨 Error Handling

### Standard Error Response

```json
{
  "detail": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

- `INVALID_MESSAGE`: Message format is invalid
- `SESSION_NOT_FOUND`: Session ID does not exist
- `AI_SERVICE_UNAVAILABLE`: OpenAI service is down
- `EMAIL_SERVICE_ERROR`: Email delivery failed
- `VALIDATION_ERROR`: Request data validation failed

## 📈 Rate Limiting

Current implementation does not include rate limiting. For production deployment, consider:

- 100 requests per minute per IP
- 1000 requests per hour per session
- Exponential backoff for repeated failures

## 🔧 Development Tools

### cURL Examples

```bash
# Health check
curl -X GET "http://localhost:8000/"

# Send chat message
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi, I need a 1-bedroom apartment"}'

# Get inventory
curl -X GET "http://localhost:8000/inventory?bedrooms=2"

# Get session details
curl -X GET "http://localhost:8000/sessions/session-123"
```

### Postman Collection

Import the provided Postman collection for comprehensive API testing:

- Pre-configured requests for all endpoints
- Environment variables for different deployment stages
- Test scripts for response validation

## 🔄 Webhooks (Future Enhancement)

Planned webhook support for external integrations:

- `conversation.completed`: When a conversation reaches completion
- `booking.confirmed`: When a tour is successfully booked
- `lead.qualified`: When all required data is collected

## 📊 Monitoring & Analytics

### Metrics Available

- Request/response times
- Error rates by endpoint
- Conversation completion rates
- Booking conversion rates
- Popular unit types and features

### Health Monitoring

- Database connectivity
- Email service status
- AI service availability
- Memory and CPU usage

## 🔐 Security Considerations

### Current Security Measures

- Input validation with Pydantic models
- SQL injection prevention with SQLAlchemy ORM
- CORS configuration for frontend integration
- Environment variable configuration

### Recommended Enhancements

- API key authentication
- Request rate limiting
- Input sanitization
- Audit logging
- HTTPS enforcement
