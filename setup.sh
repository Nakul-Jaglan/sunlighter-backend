#!/bin/bash

echo "🚀 Starting SunLighter Backend Setup..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL first."
    echo "   On macOS: brew install postgresql"
    echo "   On Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating environment configuration..."
    cp .env.example .env
    echo "📝 Please update .env file with your actual configuration values"
fi

# Database setup instructions
echo ""
echo "🗄️  DATABASE SETUP REQUIRED:"
echo "1. Start PostgreSQL service"
echo "2. Create database and user:"
echo "   sudo -u postgres psql"
echo "   CREATE DATABASE sunlighter_db;"
echo "   CREATE USER sunlighter_user WITH PASSWORD 'sunlighter_password';"
echo "   GRANT ALL PRIVILEGES ON DATABASE sunlighter_db TO sunlighter_user;"
echo "   \\q"
echo ""

# Initialize database migrations
echo "🗄️  Initializing database migrations..."
alembic revision --autogenerate -m "Initial migration"

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "🚀 TO START THE SERVER:"
echo "   source venv/bin/activate"
echo "   alembic upgrade head  # Run database migrations"
echo "   python main.py       # Start the server"
echo ""
echo "📖 API Documentation will be available at:"
echo "   http://localhost:8000/docs"
echo ""
echo "⚠️  Don't forget to:"
echo "   1. Update .env file with your actual values"
echo "   2. Set up your PostgreSQL database"
echo "   3. Configure your email settings (optional)"
