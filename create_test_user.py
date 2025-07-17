import sys
import os
sys.path.append(os.path.dirname(__file__))

from backend.app.core.database import SessionLocal, create_tables
from backend.app.models.user import User
from backend.app.core.security import get_password_hash

def create_test_user():
    """Create a test user for login testing."""
    # Ensure tables exist
    create_tables()
    
    db = SessionLocal()
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.username == "test").first()
        if existing_user:
            print("Utilizador de teste já existe!")
            print(f"Username: test")
            print(f"Password: test123")
            return
        
        # Create test user
        hashed_password = get_password_hash("test123")
        test_user = User(
            username="test",
            email="test@example.com",
            password_hash=hashed_password,
            full_name="Utilizador Teste"
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✅ Utilizador de teste criado com sucesso!")
        print(f"Username: test")
        print(f"Password: test123")
        print(f"Email: test@example.com")
        
    except Exception as e:
        print(f"❌ Erro ao criar utilizador de teste: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
