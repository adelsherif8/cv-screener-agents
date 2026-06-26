#!/usr/bin/env python3
"""
Database initialization script for CV2 platform
Creates all tables including the new User table
"""

import sys
import os
from pathlib import Path

# Add the gateway directory to the path
sys.path.append(str(Path(__file__).parent / "gateway"))

from gateway.db import engine, Base
from gateway.models import User, Job

def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Successfully created all database tables!")
        print("Tables created:")
        print("  - users")
        print("  - jobs")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n🎉 Database initialization completed successfully!")
        print("You can now start the FastAPI server.")
    else:
        print("\n💥 Database initialization failed!")
        sys.exit(1)
