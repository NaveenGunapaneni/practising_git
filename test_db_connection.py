#!/usr/bin/env python3
"""Test database connection and setup."""

import asyncio
import asyncpg
import sys
from datetime import datetime

async def test_connection():
    """Test database connection and setup."""
    try:
        # Connection parameters
        host = "localhost"
        port = 5432
        database = "geopulse_db"
        user = "geopulse_user"
        password = "geopulse_secure_123"
        
        print(f"🔄 Attempting to connect to PostgreSQL...")
        print(f"   Host: {host}:{port}")
        print(f"   Database: {database}")
        print(f"   User: {user}")
        
        # Test connection
        conn = await asyncpg.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        print("✅ Database connection successful!")
        
        # Test basic query
        result = await conn.fetchval("SELECT version()")
        print(f"📊 PostgreSQL Version: {result}")
        
        # Check if tables exist
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        print(f"📋 Tables found: {[row['table_name'] for row in tables]}")
        
        # Check users table structure
        if any(row['table_name'] == 'users' for row in tables):
            columns = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            print("👤 Users table structure:")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']}")
        
        # Test insert a user
        print("\n🧪 Testing user registration...")
        
        # Clear existing users first
        await conn.execute("DELETE FROM users WHERE email = 'test@example.com'")
        
        # Insert test user
        user_id = await conn.fetchval("""
            INSERT INTO users (
                organization_name, user_name, contact_phone, 
                email, password_hash, logo_path, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING user_id
        """, 
            "Test Org",
            "Test User", 
            "1234567890",
            "test@example.com",
            "$2b$12$dummy.hash.for.testing",
            "/default/logo.png",
            datetime.utcnow(),
            datetime.utcnow()
        )
        
        print(f"✅ Test user created with ID: {user_id}")
        
        # Verify user exists
        user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        if user:
            print(f"✅ User verification successful: {user['user_name']} ({user['email']})")
        
        # Clean up test user
        await conn.execute("DELETE FROM users WHERE user_id = $1", user_id)
        print("🧹 Test user cleaned up")
        
        await conn.close()
        print("\n🎉 All database tests passed! Registration should work now.")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)