#!/bin/bash
# Railway startup script for SunLighter backend

echo "🚀 Starting SunLighter Backend..."

# Run database schema update directly with Python
echo "📊 Updating database schema..."

python3 -c "
import os
import sys
import psycopg2
from urllib.parse import urlparse

def update_database_schema():
    print('🔗 Connecting to database...')
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print('❌ DATABASE_URL not found')
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print('✅ Connected to database')
        
        # Check current columns
        cursor.execute('''
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name IN ('user_id', 'company_handle', 'employer_id')
        ''')
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f'📋 Existing columns: {existing_columns}')
        
        # Add missing columns
        columns_added = []
        
        if 'user_id' not in existing_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN user_id VARCHAR')
            columns_added.append('user_id')
            print('✅ Added user_id column')
        
        if 'company_handle' not in existing_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN company_handle VARCHAR')
            columns_added.append('company_handle')
            print('✅ Added company_handle column')
        
        if 'employer_id' not in existing_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN employer_id INTEGER')
            columns_added.append('employer_id')
            print('✅ Added employer_id column')
        
        if not columns_added:
            print('✅ All required columns already exist')
        else:
            print(f'🎉 Added columns: {columns_added}')
        
        # Create indexes (ignore errors if they exist)
        try:
            cursor.execute('CREATE UNIQUE INDEX CONCURRENTLY idx_users_user_id ON users (user_id) WHERE user_id IS NOT NULL')
            print('✅ Created user_id index')
        except:
            print('📋 user_id index already exists or creation skipped')
        
        try:
            cursor.execute('CREATE UNIQUE INDEX CONCURRENTLY idx_users_company_handle ON users (company_handle) WHERE company_handle IS NOT NULL')
            print('✅ Created company_handle index')
        except:
            print('📋 company_handle index already exists or creation skipped')
        
        try:
            cursor.execute('CREATE UNIQUE INDEX CONCURRENTLY idx_users_employer_id ON users (employer_id) WHERE employer_id IS NOT NULL')
            print('✅ Created employer_id index')
        except:
            print('📋 employer_id index already exists or creation skipped')
        
        cursor.close()
        conn.close()
        print('🎉 Database schema update completed successfully!')
        return True
        
    except Exception as e:
        print(f'❌ Database update failed: {e}')
        return False

# Run the update
success = update_database_schema()
if success:
    print('✅ Schema update successful')
    sys.exit(0)
else:
    print('⚠️  Schema update failed, but continuing...')
    sys.exit(0)  # Don't fail the startup
"

echo "🌟 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT
