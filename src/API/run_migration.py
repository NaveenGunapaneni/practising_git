#!/usr/bin/env python3
"""
Run Alembic migration for API Usage table
"""

import subprocess
import sys
from pathlib import Path

def run_migration():
    """Run the Alembic migration to create the user_api_usage table."""
    
    try:
        print("🚀 Running Alembic migration to create user_api_usage table...")
        
        # Run alembic upgrade
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
            print(result.stdout)
        else:
            print("❌ Migration failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            sys.exit(1)
            
    except FileNotFoundError:
        print("❌ Alembic not found. Please install alembic:")
        print("pip install alembic")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    run_migration()