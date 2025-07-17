import sqlite3
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))
from config.settings import settings

def check_users():
    """Check users in database."""
    db_path = settings.database_url.replace("sqlite:///", "")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT id, username, email, full_name, is_active, created_at FROM users")
        users = cursor.fetchall()
        
        print("=== UTILIZADORES NA BASE DE DADOS ===")
        if users:
            for user in users:
                print(f"ID: {user[0]}")
                print(f"Username: {user[1]}")
                print(f"Email: {user[2]}")
                print(f"Nome completo: {user[3]}")
                print(f"Ativo: {user[4]}")
                print(f"Criado em: {user[5]}")
                print("-" * 40)
        else:
            print("Nenhum utilizador encontrado!")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar utilizadores: {e}")

if __name__ == "__main__":
    check_users()
