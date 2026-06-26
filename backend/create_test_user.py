"""Create a test user for development."""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User

def create_test_user():
    """Create a test user in the database."""
    db: Session = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("Test user already exists!")
            print(f"Email: test@example.com")
            print(f"Username: testuser")
            print(f"Password: test")
            return
        
        # Create test user with very short password
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
        
        print("Test user created successfully!")
        print(f"Email: test@example.com")
        print(f"Username: testuser")
        print(f"Password: test")
        print(f"User ID: {user.id}")
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
