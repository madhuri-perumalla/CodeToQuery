"""Recreate test user with new password hashing."""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User

def recreate_test_user():
    """Recreate test user in the database with new password hashing."""
    db: Session = SessionLocal()
    
    try:
        # Delete existing user if exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
            print("Deleted existing test user")
        
        # Create new test user with sha256_crypt hash
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("test"),
            full_name="Test User",
            is_active=True,
            is_superuser=False,
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print("Test user recreated successfully with new password hashing!")
        print(f"Email: test@example.com")
        print(f"Username: testuser")
        print(f"Password: test")
        print(f"User ID: {user.id}")
        
    except Exception as e:
        print(f"Error recreating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    recreate_test_user()
