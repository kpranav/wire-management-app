# Wire Management Application - Architecture

## System Architecture

The Wire Management application is a full-stack application with the following components:

### Backend (FastAPI)
- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **Caching**: Redis 7
- **Background Tasks**: Celery with Redis broker
- **Real-time**: WebSocket connections
- **Authentication**: JWT tokens with Bearer authentication

### Frontend (React)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI)
- **State Management**: TanStack Query for server state
- **Forms**: React Hook Form with Zod validation
- **Real-time**: WebSocket client

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: EC2 with multi-environment support
- **Registry**: Docker Hub

## Data Flow

### 1. User Authentication Flow

```
User → Login Form → POST /api/auth/login
  ↓
Backend validates credentials
  ↓
Generate JWT tokens (access + refresh)
  ↓
Return tokens to client
  ↓
Client stores tokens in localStorage
  ↓
All subsequent requests include Bearer token
```

### 2. Wire Transfer CRUD Flow

```
User → Wire List Component → GET /api/wires
  ↓
Backend checks JWT token
  ↓
Check Redis cache (5 min TTL)
  ↓
If cache miss: Query PostgreSQL
  ↓
Return paginated wire list
  ↓
Cache result in Redis
  ↓
Display in Material-UI DataGrid
```

### 3. Real-time Update Flow

```
Wire status changes (background task)
  ↓
Publish to Redis Pub/Sub channel
  ↓
WebSocket server receives update
  ↓
Broadcast to all connected clients
  ↓
Frontend receives update via WebSocket
  ↓
Update UI without page refresh
```

### 4. Background Processing Flow

```
User creates wire → POST /api/wires
  ↓
Wire saved to DB with PENDING status
  ↓
Trigger Celery task: process_wire_async
  ↓
Celery worker picks up task
  ↓
Simulate processing (API calls, validation)
  ↓
Update wire status to COMPLETED
  ↓
Publish WebSocket update
  ↓
UI updates in real-time
```

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique, indexed
- `hashed_password`: bcrypt hash
- `is_active`: Boolean
- `created_at`: Timestamp

### Wires Table
- `id`: Primary key
- `sender_name`: String(200)
- `recipient_name`: String(200)
- `amount`: Numeric(15,2)
- `currency`: String(3), default 'USD'
- `status`: Enum (pending, processing, completed, failed)
- `reference_number`: Unique identifier
- `created_by`: Foreign key to users.id
- `created_at`: Timestamp
- `updated_at`: Timestamp

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT)
- `GET /api/auth/me` - Get current user

### Wire Transfers
- `POST /api/wires` - Create wire
- `GET /api/wires` - List wires (paginated, filterable)
- `GET /api/wires/{id}` - Get single wire
- `PUT /api/wires/{id}` - Update wire
- `DELETE /api/wires/{id}` - Delete wire

### Real-time
- `WS /ws` - WebSocket connection for live updates

### Health
- `GET /` - API info
- `GET /health` - Health check

## Caching Strategy

### Redis Cache Keys

- `wires:user:{user_id}` - User's wire list (TTL: 5 min)
- `wire:{wire_id}` - Single wire details (TTL: 10 min)
- `session:user:{user_id}` - User session data (TTL: 1 hour)
- `ratelimit:{user_id}:{endpoint}` - Rate limiting counter (TTL: 60 sec)

### Cache Invalidation

Cache is invalidated when:
- Wire is created → Invalidate `wires:user:{user_id}`
- Wire is updated → Invalidate both `wire:{id}` and `wires:user:{user_id}`
- Wire is deleted → Invalidate both caches
- User logs out → Clear session cache

## Security

### Authentication
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens with 15-minute expiry
- Refresh tokens with 7-day expiry
- Bearer token authentication on all protected endpoints

### Authorization
- User can only access their own wires
- All wire operations check `created_by == current_user.id`

### Input Validation
- Pydantic schemas validate all inputs
- SQL injection prevented by SQLAlchemy ORM
- XSS prevented by React's built-in escaping

### Rate Limiting
- 100 requests per minute per endpoint per user
- Implemented via Redis counters

## Deployment Environments

### Dev (develop branch)
- **Purpose**: Latest features for testing
- **Database**: `wire_dev` (port 5432)
- **API**: Port 8001
- **UI**: Port 3001
- **Auto-deploy**: Yes
- **Features**: All enabled

### QA (qa branch)
- **Purpose**: Quality assurance testing
- **Database**: `wire_qa` (port 5433)
- **API**: Port 8002
- **UI**: Port 3002
- **Auto-deploy**: Yes
- **Features**: Stable features only

### UAT (uat branch)
- **Purpose**: User acceptance testing
- **Database**: `wire_uat` (port 5434)
- **API**: Port 8003
- **UI**: Port 3003
- **Auto-deploy**: With approval
- **Features**: Release candidates

### Production (main branch)
- **Purpose**: Live production system
- **Database**: `wire_prod` (port 5435)
- **API**: Port 8000
- **UI**: Port 3000
- **Auto-deploy**: With 2 approvals + wait timer
- **Features**: Stable, tested features only

## Technology Choices

### Why FastAPI?
- Modern async Python framework
- Auto-generated OpenAPI docs
- Type hints and validation with Pydantic
- High performance (comparable to Node.js)

### Why PostgreSQL?
- ACID compliance for financial transactions
- Robust, production-proven
- Excellent SQLAlchemy support
- JSON support for flexible schemas

### Why Redis?
- Fast in-memory caching (sub-millisecond response)
- Pub/Sub for real-time messaging
- Celery message broker
- Rate limiting and session storage

### Why React + TypeScript?
- Type safety prevents runtime errors
- Large ecosystem and community
- Component reusability
- Excellent developer experience

### Why Docker?
- Consistent environments (dev = prod)
- Easy deployment and scaling
- Isolated services
- Simplified dependency management

## Performance Considerations

### Backend
- Async database operations (asyncpg)
- Redis caching for read-heavy operations
- Background tasks for long-running operations
- Connection pooling for database

### Frontend
- Code splitting with Vite
- React Query for efficient data fetching
- Memoization of expensive computations
- Lazy loading of components

### Database
- Indexes on frequently queried columns (email, reference_number)
- Pagination to limit result set size
- Query optimization with SQLAlchemy

## Scalability

Current setup supports:
- **Users**: ~1000 concurrent users on t3.medium
- **Throughput**: ~100 requests/second
- **Database**: ~100K wire records

To scale further:
1. Upgrade EC2 instance (t3.large, t3.xlarge)
2. Add read replicas for PostgreSQL
3. Use ECS/EKS for container orchestration
4. Add load balancer (ALB)
5. Implement CDN for frontend assets
6. Add ElastiCache for Redis clustering
