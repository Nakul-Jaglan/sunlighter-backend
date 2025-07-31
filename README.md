# SunLighter Backend

A privacy-first employment verification platform built with FastAPI, PostgreSQL, and modern Python practices.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)

### Installation

1. **Clone and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Run the setup script**
   ```bash
   ./setup.sh
   ```

3. **Set up PostgreSQL database**
   ```sql
   sudo -u postgres psql
   CREATE DATABASE sunlighter_db;
   CREATE USER sunlighter_user WITH PASSWORD 'sunlighter_password';
   GRANT ALL PRIVILEGES ON DATABASE sunlighter_db TO sunlighter_user;
   \q
   ```

4. **Update environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Run database migrations**
   ```bash
   source venv/bin/activate
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

### User Management
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `DELETE /api/v1/users/me` - Delete user account

### Employment Management
- `GET /api/v1/employments/` - Get user's employments
- `POST /api/v1/employments/` - Create new employment
- `GET /api/v1/employments/{id}` - Get specific employment
- `PUT /api/v1/employments/{id}` - Update employment
- `DELETE /api/v1/employments/{id}` - Delete employment
- `POST /api/v1/employments/{id}/set-current` - Set as current job

### Verification Codes
- `GET /api/v1/verification-codes/` - Get user's verification codes
- `POST /api/v1/verification-codes/` - Create new verification code
- `GET /api/v1/verification-codes/{id}` - Get specific code
- `PUT /api/v1/verification-codes/{id}` - Update verification code
- `DELETE /api/v1/verification-codes/{id}` - Delete verification code
- `POST /api/v1/verification-codes/{id}/revoke` - Revoke verification code
- `POST /api/v1/verification-codes/verify` - Verify employment (for employers)

### Access Logs
- `GET /api/v1/access-logs/` - Get access logs
- `GET /api/v1/access-logs/{id}` - Get specific log
- `GET /api/v1/access-logs/verification-code/{id}` - Get logs for specific code
- `POST /api/v1/access-logs/{id}/approve` - Approve access request
- `POST /api/v1/access-logs/{id}/deny` - Deny access request

## 🏗️ Architecture

### Database Models
- **Users** - Employee and employer accounts
- **Employments** - Employment history and current jobs
- **VerificationCodes** - Time-limited access codes
- **AccessLogs** - Audit trail of all verification attempts

### Key Features
- **JWT Authentication** with refresh tokens
- **Role-based access control** (Employee/Employer)
- **Privacy-first design** with controlled data sharing
- **Comprehensive audit logging**
- **Automatic code expiration**
- **Rate limiting** and security measures
- **Database migrations** with Alembic

### Security Features
- Password hashing with bcrypt
- JWT token authentication
- Request rate limiting
- IP address logging
- User agent tracking
- CORS protection
- Input validation with Pydantic

## 🛠️ Development

### Project Structure
```
backend/
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core functionality (config, security)
│   ├── crud/           # Database operations
│   ├── db/             # Database configuration
│   ├── models/         # SQLAlchemy models
│   └── schemas/        # Pydantic schemas
├── alembic/            # Database migrations
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
└── setup.sh           # Setup script
```

### Environment Variables
See `.env.example` for all available configuration options.

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 🔒 Security Considerations

- **Data Privacy**: Employees control what data is shared and when
- **Access Control**: Time-limited verification codes with usage limits
- **Audit Trail**: Complete logging of all access attempts
- **Secure Authentication**: JWT tokens with proper expiration
- **Input Validation**: All inputs validated with Pydantic schemas
- **Rate Limiting**: Protection against brute force attacks

## 📊 Monitoring

- Health check endpoint: `GET /health`
- Structured logging with timestamps
- Database connection pooling
- Error tracking and reporting

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Environment Setup
1. Set up production database
2. Configure environment variables
3. Run database migrations
4. Set up reverse proxy (nginx)
5. Configure SSL certificates
6. Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
