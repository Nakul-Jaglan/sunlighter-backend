#!/bin/bash
# Railway startup script for SunLighter backend

echo "🚀 Starting SunLighter Backend..."

# Run database migrations with error handling
echo "📊 Running database migrations..."

# First, try to mark the initial migration as already applied (since the schema exists)
echo "🔍 Checking migration status..."
alembic stamp 197ff6ce9f91 2>/dev/null || echo "⚠️ Could not stamp initial migration (might already be applied)"

# Then run the upgrade to apply only the new migrations
echo "⬆️ Applying new migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migration failed"
    echo "🔄 Attempting alternative migration approach..."
    
    # Try to run just the specific migration we need
    alembic upgrade a1b2c3d4e5f6
    
    if [ $? -eq 0 ]; then
        echo "✅ Alternative migration approach successful"
    else
        echo "❌ All migration attempts failed"
        echo "📋 Migration will be skipped, server starting anyway..."
        echo "⚠️  Please run migrations manually if needed"
    fi
fi

# Start the FastAPI server
echo "🌟 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT
