#!/bin/bash
# Railway startup script for SunLighter backend

echo "🚀 Starting SunLighter Backend..."

# Run database migrations
echo "📊 Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migration failed"
    exit 1
fi

# Start the FastAPI server
echo "🌟 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT
